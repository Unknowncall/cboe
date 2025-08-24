"""
Database operations for the CBOE Trail Search API
"""
import sqlite3
import logging
import time
import threading
from typing import List, Dict, Any, Optional
from pathlib import Path
from queue import Queue, Empty
from contextlib import contextmanager

from config import DB_PATH, DB_POOL_SIZE
from utils import log_database_operation, PerformanceTimer, km_to_miles

logger = logging.getLogger("trail_search.database")

class DatabaseManager:
    """Manages database connections and operations with connection pooling"""
    
    def __init__(self, db_path: str = DB_PATH, pool_size: int = 5):
        self.db_path = db_path
        self.pool_size = pool_size
        self.pool = Queue(maxsize=pool_size)
        self.lock = threading.Lock()
        self._initialized = False
        
        # Pre-populate connection pool
        for _ in range(pool_size):
            conn = sqlite3.connect(db_path, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            # Enable WAL mode for better concurrency
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA synchronous=NORMAL")
            conn.execute("PRAGMA cache_size=1000")
            conn.execute("PRAGMA temp_store=memory")
            self.pool.put(conn)
        
        logger.info(f"Initialized DatabaseManager with {pool_size} connections at {db_path}")
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = None
        try:
            # Get connection from pool with timeout
            conn = self.pool.get(timeout=30)
            yield conn
        except Empty:
            raise Exception("Database connection pool exhausted")
        except Exception as e:
            if conn:
                # Rollback on error
                try:
                    conn.rollback()
                except:
                    pass
            raise e
        finally:
            if conn:
                # Return connection to pool
                self.pool.put(conn)
    
    def get_connection_legacy(self) -> sqlite3.Connection:
        """Legacy method for backward compatibility - use get_connection() context manager instead"""
        try:
            conn = self.pool.get(timeout=30)
            return conn
        except Empty:
            raise Exception("Database connection pool exhausted")
    
    def return_connection(self, conn: sqlite3.Connection):
        """Return a connection to the pool - for legacy compatibility"""
        self.pool.put(conn)
    
    def init_database(self, request_id: str = "init") -> bool:
        """Initialize SQLite database with trails table and FTS5 index"""
        logger.info(f"Initializing database at {self.db_path}")
        
        try:
            with PerformanceTimer("database_init", request_id) as timer:
                with self.get_connection() as conn:
                    cursor = conn.cursor()
                    
                    # Create trails table
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS trails (
                            id INTEGER PRIMARY KEY,
                            name TEXT NOT NULL,
                            distance_km REAL NOT NULL,
                            elevation_gain_m INTEGER NOT NULL,
                            difficulty TEXT NOT NULL,
                            dogs_allowed BOOLEAN NOT NULL,
                            route_type TEXT NOT NULL,
                            features TEXT NOT NULL,
                            latitude REAL NOT NULL,
                            longitude REAL NOT NULL,
                            description TEXT NOT NULL,
                            
                            -- Enhanced location information
                            city TEXT,
                            county TEXT,
                            state TEXT NOT NULL DEFAULT 'Illinois',
                            region TEXT,
                            country TEXT NOT NULL DEFAULT 'United States',
                            
                            -- Amenities and access information
                            parking_available BOOLEAN DEFAULT TRUE,
                            parking_type TEXT,  -- 'free', 'paid', 'limited', 'street'
                            restrooms BOOLEAN DEFAULT FALSE,
                            water_available BOOLEAN DEFAULT FALSE,
                            picnic_areas BOOLEAN DEFAULT FALSE,
                            camping_available BOOLEAN DEFAULT FALSE,
                            
                            -- Access and permit information
                            entry_fee BOOLEAN DEFAULT FALSE,
                            permit_required BOOLEAN DEFAULT FALSE,
                            seasonal_access TEXT,  -- 'year-round', 'seasonal', 'summer', 'winter'
                            accessibility TEXT,  -- 'wheelchair', 'stroller', 'none'
                            
                            -- Trail characteristics
                            surface_type TEXT,  -- 'paved', 'gravel', 'dirt', 'boardwalk', 'mixed'
                            trail_markers BOOLEAN DEFAULT TRUE,
                            loop_trail BOOLEAN,
                            
                            -- Contact and website
                            managing_agency TEXT,
                            website_url TEXT,
                            phone_number TEXT,
                            
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """)
                    
                    # Create FTS5 table with weighted columns including new location fields
                    cursor.execute("""
                        CREATE VIRTUAL TABLE IF NOT EXISTS trails_fts USING fts5(
                            name, description, features, city, county, state, region, 
                            managing_agency, surface_type, parking_type,
                            content='trails',
                            content_rowid='id',
                            prefix='2,3,4'
                        )
                    """)
                    
                    # Create indexes for better performance
                    cursor.execute("""
                        CREATE INDEX IF NOT EXISTS idx_trails_difficulty 
                        ON trails(difficulty)
                    """)
                    
                    cursor.execute("""
                        CREATE INDEX IF NOT EXISTS idx_trails_distance 
                        ON trails(distance_km)
                    """)
                
                    cursor.execute("""
                        CREATE INDEX IF NOT EXISTS idx_trails_elevation 
                        ON trails(elevation_gain_m)
                    """)
                
                    cursor.execute("""
                        CREATE INDEX IF NOT EXISTS idx_trails_location 
                        ON trails(latitude, longitude)
                    """)
                    
                    # New indexes for enhanced fields
                    cursor.execute("""
                        CREATE INDEX IF NOT EXISTS idx_trails_state_county 
                        ON trails(state, county)
                    """)
                    
                    cursor.execute("""
                        CREATE INDEX IF NOT EXISTS idx_trails_city 
                        ON trails(city)
                    """)
                    
                    cursor.execute("""
                        CREATE INDEX IF NOT EXISTS idx_trails_amenities 
                        ON trails(parking_available, restrooms, dogs_allowed)
                    """)
                    
                    cursor.execute("""
                        CREATE INDEX IF NOT EXISTS idx_trails_surface_access 
                        ON trails(surface_type, accessibility)
                    """)
                
                    conn.commit()
                
                log_database_operation(request_id, "init_database", "trails", timer.duration_ms)
                logger.info("Database initialized successfully")
                return True
                
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            return False
    
    def get_trail_count(self, request_id: str = "count") -> int:
        """Get the number of trails in the database"""
        try:
            with PerformanceTimer("get_trail_count", request_id) as timer:
                with self.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT COUNT(*) FROM trails")
                    count = cursor.fetchone()[0]
                    
                    log_database_operation(request_id, "count", "trails", timer.duration_ms, count)
                    logger.debug(f"Trail count: {count}")
                    return count
                
        except Exception as e:
            logger.error(f"Failed to get trail count: {e}")
            return 0
    
    def seed_trails(self, request_id: str = "seed") -> int:
        """Seed database with Chicago and Midwest trails with enhanced information"""
        logger.info("Seeding database with enhanced trail data")
        
        # Enhanced trail data structure: (id, name, distance_km, elevation_gain_m, difficulty, dogs_allowed, route_type, features, 
        # latitude, longitude, description, city, county, state, region, country, parking_available, parking_type, 
        # restrooms, water_available, picnic_areas, camping_available, entry_fee, permit_required, seasonal_access, 
        # accessibility, surface_type, trail_markers, loop_trail, managing_agency, website_url, phone_number)
        trails_data = [
            # Chicago Area Trails with Enhanced Data
            (1, "Lakefront Trail Loop", 3.2, 5, "easy", True, "loop", "lake,boardwalk,urban", 
             41.8819, -87.6278, "Scenic loop along Lake Michigan with stunning skyline views and boardwalk sections.",
             "Chicago", "Cook County", "Illinois", "Great Lakes", "United States", True, "free", True, True, True, False, 
             False, False, "year-round", "wheelchair", "paved", True, True, "Chicago Park District", 
             "https://www.chicagoparkdistrict.com/", "312-742-7529"),
             
            (2, "Starved Rock Waterfall Trail", 4.8, 120, "moderate", True, "out and back", "waterfall,canyon,forest", 
             41.3186, -88.9951, "Beautiful trail leading to cascading waterfalls through wooded canyons.",
             "Oglesby", "LaSalle County", "Illinois", "North Central Illinois", "United States", True, "paid", True, True, True, True, 
             True, False, "year-round", "none", "dirt", True, False, "Illinois Department of Natural Resources", 
             "https://www2.illinois.gov/dnr/Parks/Pages/StarvedRock.aspx", "815-667-4726"),
             
            (3, "Indiana Dunes Beach Trail", 2.1, 45, "easy", True, "loop", "dunes,beach,lake", 
             41.6532, -87.0921, "Short loop through impressive sand dunes with Lake Michigan access.",
             "Porter", "Porter County", "Indiana", "Great Lakes", "United States", True, "free", True, True, True, True, 
             True, False, "year-round", "stroller", "mixed", True, True, "National Park Service", 
             "https://www.nps.gov/indu/", "219-395-1882"),
             
            (4, "Kettle Moraine Prairie Path", 6.7, 85, "moderate", True, "loop", "prairie,wildflowers,hills", 
             42.9633, -88.5439, "Rolling prairie trail with seasonal wildflowers and glacial landscape features.",
             "Eagle", "Waukesha County", "Wisconsin", "Southeast Wisconsin", "United States", True, "free", True, False, True, True, 
             False, False, "year-round", "none", "dirt", True, True, "Wisconsin Department of Natural Resources", 
             "https://dnr.wisconsin.gov/topic/parks/kettlemoraine", "262-594-6200"),
             
            (5, "Chicago Riverwalk", 2.4, 0, "easy", False, "out and back", "urban,river,boardwalk", 
             41.8887, -87.6233, "Urban boardwalk along the Chicago River through downtown architecture.",
             "Chicago", "Cook County", "Illinois", "Great Lakes", "United States", True, "paid", True, True, False, False, 
             False, False, "year-round", "wheelchair", "boardwalk", True, False, "City of Chicago", 
             "https://www.chicago.gov/city/en/depts/dcd/supp_info/chicago_riverwalk.html", "311"),
             
            (6, "Palos Forest Preserve", 8.2, 65, "moderate", True, "loop", "forest,creek,hills", 
             41.6611, -87.8167, "Peaceful forest trail with creek crossings and gentle elevation changes.",
             "Palos Hills", "Cook County", "Illinois", "Chicago Metropolitan", "United States", True, "free", True, True, True, False, 
             False, False, "year-round", "none", "dirt", True, True, "Forest Preserve District of Cook County", 
             "https://fpdcc.com/places/locations/palos/", "800-870-3666"),
             
            (7, "Devil's Lake State Park", 12.4, 380, "hard", True, "loop", "lake,bluffs,quartzite", 
             43.4221, -89.7251, "Challenging loop around pristine lake with dramatic quartzite bluffs.",
             "Baraboo", "Sauk County", "Wisconsin", "South Central Wisconsin", "United States", True, "paid", True, True, True, True, 
             True, True, "year-round", "none", "dirt", True, True, "Wisconsin State Parks", 
             "https://dnr.wisconsin.gov/topic/parks/devilslake", "608-356-8301"),
             
            (8, "Millennium Park Garden Walk", 1.8, 15, "easy", False, "loop", "garden,urban,art", 
             41.8826, -87.6220, "Easy urban walk through award-winning gardens and public art installations.",
             "Chicago", "Cook County", "Illinois", "Great Lakes", "United States", True, "paid", True, True, False, False, 
             False, False, "year-round", "wheelchair", "paved", True, True, "Chicago Park District", 
             "https://www.millenniumpark.org/", "312-742-1168"),
             
            (9, "Warren Dunes Summit Trail", 5.3, 190, "moderate", True, "out and back", "dunes,beach,forest", 
             41.9089, -86.5986, "Moderate climb to the highest dune with panoramic lake views.",
             "Sawyer", "Berrien County", "Michigan", "Great Lakes", "United States", True, "paid", True, True, True, True, 
             True, True, "year-round", "none", "mixed", True, False, "Michigan State Parks", 
             "https://www.michigan.gov/dnr/places/state-parks/warren-dunes", "269-426-4013"),
             
            (10, "Fox River Trail", 7.9, 25, "easy", True, "out and back", "river,prairie,boardwalk", 
             42.3297, -88.3251, "Flat trail following the Fox River with prairie restoration areas.",
             "St. Charles", "Kane County", "Illinois", "Fox River Valley", "United States", True, "free", True, False, True, False, 
             False, False, "year-round", "wheelchair", "paved", True, False, "Kane County Forest Preserve", 
             "https://www.kaneforest.com/", "630-232-5980"),
             
            # Add more enhanced trail data here...
            # For now, I'll include a few more examples and then we can expand later
            
            (11, "Morton Arboretum", 3.8, 35, "easy", False, "loop", "garden,forest,lake", 
             41.8167, -88.0667, "Beautiful arboretum with themed tree collections and lake views.",
             "Lisle", "DuPage County", "Illinois", "Chicago Metropolitan", "United States", True, "paid", True, True, True, False, 
             True, False, "year-round", "wheelchair", "paved", True, True, "Morton Arboretum", 
             "https://www.mortonarb.org/", "630-968-0074"),
             
            (12, "Starved Rock Eagle Cliff", 11.8, 320, "hard", True, "out and back", "bluffs,forest,overlook", 
             41.3186, -88.9951, "Extended challenging hike to highest overlook in park.",
             "Oglesby", "LaSalle County", "Illinois", "North Central Illinois", "United States", True, "paid", True, True, True, True, 
             True, False, "year-round", "none", "dirt", True, False, "Illinois Department of Natural Resources", 
             "https://www2.illinois.gov/dnr/Parks/Pages/StarvedRock.aspx", "815-667-4726"),
             
            (13, "Geneva Lake Shore Path", 21.1, 60, "moderate", False, "loop", "lake,historic,beach", 
             42.5917, -88.5417, "Complete loop around pristine glacial lake with historic estates.",
             "Lake Geneva", "Walworth County", "Wisconsin", "Southeast Wisconsin", "United States", True, "free", True, False, True, False, 
             False, False, "year-round", "stroller", "mixed", True, True, "Lake Geneva Path Commission", 
             "https://www.lakegenevawi.com/", "262-248-3673"),
             
            (14, "Illinois & Michigan Canal Trail", 24.5, 60, "easy", True, "out and back", "historic,canal,urban", 
             41.6000, -88.0000, "Historic canal towpath through multiple communities.",
             "Joliet", "Will County", "Illinois", "Chicago Metropolitan", "United States", True, "free", True, False, True, False, 
             False, False, "year-round", "wheelchair", "gravel", True, False, "Illinois Department of Natural Resources", 
             "https://www2.illinois.gov/dnr/Parks/Pages/IlLinoisMichiganCanal.aspx", "815-727-8700"),
             
            (15, "Chain O'Lakes State Park", 8.3, 45, "easy", True, "loop", "lake,prairie,forest", 
             42.4167, -88.1833, "Multi-lake trail system with diverse wildlife viewing.",
             "Spring Grove", "McHenry County", "Illinois", "Fox River Valley", "United States", True, "paid", True, True, True, True, 
             True, False, "year-round", "stroller", "mixed", True, True, "Illinois Department of Natural Resources", 
             "https://www2.illinois.gov/dnr/Parks/Pages/ChainOLakes.aspx", "847-587-5512"),
             
            # Additional Chicago Metropolitan Area Trails
            
            (16, "Salt Creek Trail", 9.6, 30, "easy", True, "out and back", "creek,forest,prairie", 
             41.8700, -87.9200, "Peaceful trail following Salt Creek through Cook County forest preserves.",
             "Brookfield", "Cook County", "Illinois", "Chicago Metropolitan", "United States", True, "free", True, False, True, False, 
             False, False, "year-round", "wheelchair", "paved", True, False, "Forest Preserve District of Cook County", 
             "https://fpdcc.com/", "800-870-3666"),
             
            (17, "North Branch Trail", 16.1, 40, "easy", True, "out and back", "river,forest,prairie", 
             42.0950, -87.7800, "Long paved trail following North Branch Chicago River from Chicago to Lake County.",
             "Northbrook", "Cook County", "Illinois", "Chicago Metropolitan", "United States", True, "free", True, True, True, False, 
             False, False, "year-round", "wheelchair", "paved", True, False, "Forest Preserve District of Cook County", 
             "https://fpdcc.com/", "800-870-3666"),
             
            (18, "Busse Woods Trail", 11.2, 25, "easy", True, "loop", "lake,forest,prairie", 
             42.0400, -88.0300, "Popular loop trail around Busse Lake with wildlife viewing opportunities.",
             "Elk Grove Village", "Cook County", "Illinois", "Chicago Metropolitan", "United States", True, "free", True, True, True, False, 
             False, False, "year-round", "wheelchair", "paved", True, True, "Forest Preserve District of Cook County", 
             "https://fpdcc.com/", "800-870-3666"),
             
            (19, "Des Plaines River Trail", 22.5, 35, "easy", True, "out and back", "river,forest,prairie", 
             42.1500, -87.8900, "Scenic trail following Des Plaines River through multiple counties.",
             "Des Plaines", "Cook County", "Illinois", "Chicago Metropolitan", "United States", True, "free", True, True, True, False, 
             False, False, "year-round", "wheelchair", "paved", True, False, "Lake County Forest Preserve", 
             "https://www.lcfpd.org/", "847-367-6640"),
             
            (20, "606 Trail (Bloomingdale Trail)", 4.4, 10, "easy", False, "out and back", "urban,elevated,art", 
             41.9130, -87.6950, "Elevated linear park on former railway with city views and art installations.",
             "Chicago", "Cook County", "Illinois", "Chicago Metropolitan", "United States", True, "free", True, True, False, False, 
             False, False, "year-round", "wheelchair", "paved", True, False, "Chicago Park District", 
             "https://www.the606.org/", "312-742-7529"),
             
            (21, "Lakefront Trail - South", 12.9, 15, "easy", True, "out and back", "lake,beach,urban", 
             41.7800, -87.5700, "Southern section of Chicago's famous lakefront trail with beaches and parks.",
             "Chicago", "Cook County", "Illinois", "Great Lakes", "United States", True, "free", True, True, True, False, 
             False, False, "year-round", "wheelchair", "paved", True, False, "Chicago Park District", 
             "https://www.chicagoparkdistrict.com/", "312-742-7529"),
             
            (22, "Waterfall Glen Forest Preserve", 9.7, 85, "moderate", True, "loop", "forest,creek,prairie", 
             41.7200, -87.9700, "Beautiful loop trail with creek crossings and diverse ecosystems.",
             "Darien", "DuPage County", "Illinois", "Chicago Metropolitan", "United States", True, "free", True, False, True, False, 
             False, False, "year-round", "none", "gravel", True, True, "Forest Preserve District of DuPage County", 
             "https://www.dupageforest.org/", "630-933-7200"),
             
            (23, "Prarie Path Trail", 24.1, 40, "easy", True, "out and back", "prairie,creek,forest", 
             41.9300, -88.2100, "Long rail-trail connecting multiple DuPage County communities.",
             "Wheaton", "DuPage County", "Illinois", "Chicago Metropolitan", "United States", True, "free", True, True, True, False, 
             False, False, "year-round", "wheelchair", "paved", True, False, "Forest Preserve District of DuPage County", 
             "https://www.dupageforest.org/", "630-933-7200"),
             
            (24, "Caldwell Woods", 4.2, 20, "easy", True, "loop", "forest,creek,trails", 
             41.9800, -87.7600, "Peaceful forest preserve with meandering trails and North Branch Chicago River access.",
             "Chicago", "Cook County", "Illinois", "Chicago Metropolitan", "United States", True, "free", True, False, True, False, 
             False, False, "year-round", "stroller", "dirt", True, True, "Forest Preserve District of Cook County", 
             "https://fpdcc.com/", "800-870-3666"),
             
            (25, "Blackwell Forest Preserve", 5.8, 55, "moderate", True, "loop", "lake,forest,hills", 
             41.8100, -88.1200, "Rolling trail around McKee Marsh with bird watching opportunities.",
             "Warrenville", "DuPage County", "Illinois", "Chicago Metropolitan", "United States", True, "free", True, True, True, False, 
             False, False, "year-round", "none", "mixed", True, True, "Forest Preserve District of DuPage County", 
             "https://www.dupageforest.org/", "630-933-7200"),
             
            (26, "Great Western Trail", 19.3, 30, "easy", True, "out and back", "prairie,forest,rail-trail", 
             41.9200, -88.4200, "Former railway converted to trail connecting DuPage and Kane counties.",
             "West Chicago", "DuPage County", "Illinois", "Chicago Metropolitan", "United States", True, "free", True, False, True, False, 
             False, False, "year-round", "wheelchair", "paved", True, False, "DuPage County", 
             "https://www.dupageco.org/", "630-407-6700"),
             
            (27, "Camp Sagawau", 6.4, 70, "moderate", True, "loop", "forest,creek,wildlife", 
             41.6500, -87.9200, "Nature preserve with diverse wildlife and environmental education center.",
             "Lemont", "Cook County", "Illinois", "Chicago Metropolitan", "United States", True, "free", True, True, True, False, 
             False, False, "year-round", "none", "dirt", True, True, "Forest Preserve District of Cook County", 
             "https://fpdcc.com/", "800-870-3666"),
             
            (28, "Ned Brown Preserve (Busse Woods)", 8.7, 30, "easy", True, "loop", "lake,forest,fishing", 
             42.0400, -88.0300, "Popular preserve with fishing, boating, and multi-use trails around Busse Lake.",
             "Elk Grove Village", "Cook County", "Illinois", "Chicago Metropolitan", "United States", True, "free", True, True, True, False, 
             False, False, "year-round", "wheelchair", "paved", True, True, "Forest Preserve District of Cook County", 
             "https://fpdcc.com/", "800-870-3666"),
             
            (29, "Illinois Prairie Path", 61.0, 50, "easy", True, "out and back", "prairie,historic,rail-trail", 
             41.8700, -88.0500, "Historic rail-trail system spanning multiple counties west of Chicago.",
             "Elmhurst", "DuPage County", "Illinois", "Chicago Metropolitan", "United States", True, "free", True, True, True, False, 
             False, False, "year-round", "wheelchair", "paved", True, False, "Illinois Prairie Path Association", 
             "https://www.ipp.org/", "630-752-0120"),
             
            (30, "Tampier Lake Trail", 3.2, 15, "easy", True, "loop", "lake,prairie,wildlife", 
             41.5800, -87.9500, "Peaceful lake loop with excellent bird watching and prairie restoration.",
             "Orland Park", "Cook County", "Illinois", "Chicago Metropolitan", "United States", True, "free", True, False, True, False, 
             False, False, "year-round", "stroller", "paved", True, True, "Forest Preserve District of Cook County", 
             "https://fpdcc.com/", "800-870-3666"),
             
            # Lincoln Park and Grant Park Area Trails
            
            (31, "Lincoln Park Zoo to North Avenue Beach", 4.8, 10, "easy", False, "out and back", "urban,zoo,beach", 
             41.9200, -87.6350, "Urban trail connecting Lincoln Park Zoo to North Avenue Beach along the lakefront.",
             "Chicago", "Cook County", "Illinois", "Great Lakes", "United States", True, "paid", True, True, True, False, 
             False, False, "year-round", "wheelchair", "paved", True, False, "Chicago Park District", 
             "https://www.chicagoparkdistrict.com/", "312-742-7529"),
             
            (32, "Grant Park Loop", 2.7, 5, "easy", False, "loop", "urban,garden,historic", 
             41.8756, -87.6244, "Loop through Chicago's 'front yard' including Buckingham Fountain and gardens.",
             "Chicago", "Cook County", "Illinois", "Great Lakes", "United States", True, "paid", True, True, False, False, 
             False, False, "year-round", "wheelchair", "paved", True, True, "Chicago Park District", 
             "https://www.chicagoparkdistrict.com/", "312-742-7529"),
             
            (33, "Jackson Park to Promontory Point", 6.1, 20, "easy", True, "out and back", "lake,historic,gardens", 
             41.7900, -87.5800, "Scenic lakefront trail connecting Jackson Park to historic Promontory Point.",
             "Chicago", "Cook County", "Illinois", "Great Lakes", "United States", True, "free", True, True, True, False, 
             False, False, "year-round", "wheelchair", "paved", True, False, "Chicago Park District", 
             "https://www.chicagoparkdistrict.com/", "312-742-7529"),
             
            # Forest Preserve District Trails
            
            (34, "Palos Trail System - Yellow Trail", 12.3, 95, "moderate", True, "loop", "forest,hills,singletrack", 
             41.6611, -87.8167, "Mountain biking and hiking trail through hilly Palos forest preserve.",
             "Palos Hills", "Cook County", "Illinois", "Chicago Metropolitan", "United States", True, "free", True, True, True, False, 
             False, False, "year-round", "none", "dirt", True, True, "Forest Preserve District of Cook County", 
             "https://fpdcc.com/", "800-870-3666"),
             
            (35, "Swallow Cliff Woods", 7.2, 110, "moderate", True, "loop", "forest,hills,stairs", 
             41.6450, -87.8850, "Hilly preserve with toboggan slides and challenging terrain.",
             "Palos Park", "Cook County", "Illinois", "Chicago Metropolitan", "United States", True, "free", True, True, True, False, 
             False, False, "year-round", "none", "dirt", True, True, "Forest Preserve District of Cook County", 
             "https://fpdcc.com/", "800-870-3666"),
             
            (36, "Deer Grove Forest Preserve", 5.4, 25, "easy", True, "loop", "forest,prairie,creek", 
             42.1400, -88.0500, "Family-friendly trails through diverse ecosystems with interpretive signs.",
             "Palatine", "Cook County", "Illinois", "Chicago Metropolitan", "United States", True, "free", True, True, True, False, 
             False, False, "year-round", "stroller", "mixed", True, True, "Forest Preserve District of Cook County", 
             "https://fpdcc.com/", "800-870-3666"),
             
            # Nearby State Parks and Natural Areas
            
            (37, "Moraine Hills State Park", 10.1, 45, "easy", True, "loop", "lake,prairie,hills", 
             42.3700, -88.2000, "Glacial landscape with kettle lakes and prairie restoration.",
             "McHenry", "McHenry County", "Illinois", "Fox River Valley", "United States", True, "free", True, True, True, False, 
             False, False, "year-round", "wheelchair", "mixed", True, True, "Illinois Department of Natural Resources", 
             "https://www2.illinois.gov/dnr/Parks/Pages/MoraineHills.aspx", "815-385-1624"),
             
            (38, "Silver Springs State Park", 8.9, 35, "easy", True, "loop", "creek,forest,springs", 
             41.3300, -88.6700, "Beautiful park centered around natural springs and York Creek.",
             "Yorkville", "Kendall County", "Illinois", "Fox River Valley", "United States", True, "free", True, True, True, True, 
             False, False, "year-round", "stroller", "mixed", True, True, "Illinois Department of Natural Resources", 
             "https://www2.illinois.gov/dnr/Parks/Pages/SilverSprings.aspx", "630-553-6297"),
             
            (39, "Rock Cut State Park", 14.6, 120, "moderate", True, "loop", "lake,forest,hills", 
             42.3600, -89.0700, "Rolling terrain with Pierce Lake and diverse wildlife habitats.",
             "Loves Park", "Winnebago County", "Illinois", "Northern Illinois", "United States", True, "paid", True, True, True, True, 
             True, False, "year-round", "none", "dirt", True, True, "Illinois Department of Natural Resources", 
             "https://www2.illinois.gov/dnr/Parks/Pages/RockCut.aspx", "815-885-3311"),
             
            (40, "Kankakee River State Park", 13.2, 80, "moderate", True, "loop", "river,forest,limestone", 
             41.1900, -87.9600, "Scenic river valley with limestone canyons and diverse plant life.",
             "Bourbonnais", "Kankakee County", "Illinois", "Kankakee River Valley", "United States", True, "free", True, True, True, True, 
             False, False, "year-round", "none", "dirt", True, True, "Illinois Department of Natural Resources", 
             "https://www2.illinois.gov/dnr/Parks/Pages/KankakeeRiver.aspx", "815-933-1383"),
             
            # Lake County, Illinois Trails
            
            (41, "Ryerson Woods", 4.7, 30, "easy", True, "loop", "forest,creek,education", 
             42.2200, -87.8100, "Educational trail through old-growth forest with Des Plaines River access.",
             "Riverwoods", "Lake County", "Illinois", "Chicago Metropolitan", "United States", True, "free", True, True, True, False, 
             False, False, "year-round", "stroller", "mixed", True, True, "Lake County Forest Preserve", 
             "https://www.lcfpd.org/", "847-367-6640"),
             
            (42, "Volo Bog State Natural Area", 2.8, 10, "easy", False, "loop", "bog,boardwalk,rare plants", 
             42.3400, -88.1700, "Unique bog ecosystem accessible via floating boardwalk trail.",
             "Ingleside", "Lake County", "Illinois", "Fox River Valley", "United States", True, "free", True, False, False, False, 
             False, False, "year-round", "wheelchair", "boardwalk", True, True, "Illinois Department of Natural Resources", 
             "https://www2.illinois.gov/dnr/Parks/Pages/VoloBog.aspx", "815-344-1294"),
             
            (43, "Lake Bluff Open Lands", 6.3, 55, "moderate", True, "loop", "bluff,lake,prairie", 
             42.2800, -87.8300, "Bluff top trails with Lake Michigan views and prairie restoration.",
             "Lake Bluff", "Lake County", "Illinois", "Great Lakes", "United States", True, "free", True, False, True, False, 
             False, False, "year-round", "none", "dirt", True, True, "Lake Bluff Open Lands Association", 
             "https://www.lakebluffopenlands.org/", "847-234-1225"),
             
            # Will County Trails
            
            (44, "Isle a la Cache Museum Trail", 3.1, 15, "easy", True, "loop", "historic,island,museum", 
             41.5600, -88.0700, "Historic island trail with museum and Des Plaines River views.",
             "Romeoville", "Will County", "Illinois", "Chicago Metropolitan", "United States", True, "free", True, True, False, False, 
             False, False, "year-round", "wheelchair", "paved", True, True, "Forest Preserve District of Will County", 
             "https://www.reconnectwithnature.org/", "815-727-8700"),
             
            (45, "Rock Run Rookery Preserve", 4.9, 25, "easy", True, "loop", "prairie,wetland,birds", 
             41.4200, -88.1500, "Important bird habitat with Great Blue Heron rookery and prairie restoration.",
             "Joliet", "Will County", "Illinois", "Chicago Metropolitan", "United States", True, "free", True, False, True, False, 
             False, False, "year-round", "stroller", "gravel", True, True, "Forest Preserve District of Will County", 
             "https://www.reconnectwithnature.org/", "815-727-8700"),
             
            # WISCONSIN - Driving Range from Chicago (1-4 hours)
            
            (46, "Devil's Lake Balanced Rock Trail", 2.8, 180, "moderate", True, "out and back", "bluffs,rock formations,overlook", 
             43.4221, -89.7251, "Shorter challenging hike to iconic balanced rock formation with valley views.",
             "Baraboo", "Sauk County", "Wisconsin", "South Central Wisconsin", "United States", True, "paid", True, True, True, True, 
             True, True, "year-round", "none", "dirt", True, False, "Wisconsin State Parks", 
             "https://dnr.wisconsin.gov/topic/parks/devilslake", "608-356-8301"),
             
            (47, "Wisconsin Dells State Park", 6.2, 95, "moderate", True, "loop", "canyon,river,sandstone", 
             43.6275, -89.7709, "Scenic trail through famous sandstone gorges and Wisconsin River overlooks.",
             "Wisconsin Dells", "Columbia County", "Wisconsin", "South Central Wisconsin", "United States", True, "paid", True, True, True, True, 
             True, False, "year-round", "none", "dirt", True, True, "Wisconsin State Parks", 
             "https://dnr.wisconsin.gov/topic/parks/wisconsindells", "608-254-2333"),
             
            (48, "Kettle Moraine Ice Age Trail", 18.2, 140, "moderate", True, "out and back", "glacial,hills,forest", 
             42.9633, -88.5439, "Section of the famous Ice Age Trail through glacial landscape features.",
             "Eagle", "Waukesha County", "Wisconsin", "Southeast Wisconsin", "United States", True, "free", True, False, True, True, 
             False, False, "year-round", "none", "dirt", True, False, "Wisconsin Department of Natural Resources", 
             "https://dnr.wisconsin.gov/topic/parks/kettlemoraine", "262-594-6200"),
             
            (49, "Lake Geneva Fontana Beach Trail", 3.4, 25, "easy", True, "out and back", "lake,beach,historic", 
             42.5417, -88.6167, "Beautiful lakefront trail along Geneva Lake with beach access.",
             "Fontana", "Walworth County", "Wisconsin", "Southeast Wisconsin", "United States", True, "paid", True, True, True, False, 
             False, False, "year-round", "wheelchair", "paved", True, False, "Village of Fontana", 
             "https://www.villageoffontana.com/", "262-275-6136"),
             
            (50, "Governor Dodge State Park", 11.7, 220, "hard", True, "loop", "bluffs,valleys,creek", 
             43.0167, -90.1167, "Challenging trail through rugged terrain with stunning bluff-top views.",
             "Dodgeville", "Iowa County", "Wisconsin", "Southwest Wisconsin", "United States", True, "paid", True, True, True, True, 
             True, True, "year-round", "none", "dirt", True, True, "Wisconsin State Parks", 
             "https://dnr.wisconsin.gov/topic/parks/governordodge", "608-935-2315"),
             
            (51, "Mirror Lake State Park", 8.3, 65, "moderate", True, "loop", "lake,forest,sandstone", 
             43.5667, -89.8333, "Peaceful trail around pristine lake with sandstone cliffs.",
             "Baraboo", "Sauk County", "Wisconsin", "South Central Wisconsin", "United States", True, "paid", True, True, True, True, 
             True, True, "year-round", "stroller", "mixed", True, True, "Wisconsin State Parks", 
             "https://dnr.wisconsin.gov/topic/parks/mirrorlake", "608-254-2333"),
             
            (52, "Galena River Trail", 12.1, 45, "easy", True, "out and back", "river,historic,rail-trail", 
             42.4167, -90.4292, "Historic trail following the Galena River through charming river towns.",
             "Galena", "Jo Daviess County", "Illinois", "Northwest Illinois", "United States", True, "free", True, True, True, False, 
             False, False, "year-round", "wheelchair", "paved", True, False, "Galena River Trail Commission", 
             "https://www.cityofgalena.org/", "815-777-1050"),
             
            (53, "Peninsula State Park Eagle Bluff", 5.4, 125, "moderate", True, "out and back", "bluff,bay,lighthouse", 
             45.1833, -87.2333, "Scenic bluff trail with Green Bay views and historic Eagle Bluff Lighthouse.",
             "Fish Creek", "Door County", "Wisconsin", "Door Peninsula", "United States", True, "paid", True, True, True, True, 
             True, True, "year-round", "none", "dirt", True, False, "Wisconsin State Parks", 
             "https://dnr.wisconsin.gov/topic/parks/peninsula", "920-868-3258"),
             
            # MICHIGAN - Driving Range from Chicago (1-4 hours)
            
            (54, "Sleeping Bear Dunes Dune Climb", 2.4, 140, "hard", True, "out and back", "dunes,lake,sand", 
             44.8667, -86.0500, "Challenging climb up massive sand dunes with Lake Michigan views.",
             "Glen Arbor", "Leelanau County", "Michigan", "Northern Michigan", "United States", True, "paid", True, True, False, False, 
             True, False, "year-round", "none", "sand", True, False, "National Park Service", 
             "https://www.nps.gov/slbe/", "231-326-4700"),
             
            (55, "Pictured Rocks Munising Falls", 1.6, 30, "easy", True, "out and back", "waterfall,forest,sandstone", 
             46.4167, -86.6500, "Short hike to spectacular 50-foot waterfall in sandstone canyon.",
             "Munising", "Alger County", "Michigan", "Upper Peninsula", "United States", True, "free", True, True, False, False, 
             True, False, "year-round", "stroller", "dirt", True, False, "National Park Service", 
             "https://www.nps.gov/piro/", "906-387-3700"),
             
            (56, "Holland State Park Dune Trail", 3.2, 85, "moderate", True, "loop", "dunes,beach,lighthouse", 
             42.7667, -86.2167, "Coastal dune trail with Lake Michigan beach access and lighthouse views.",
             "Holland", "Ottawa County", "Michigan", "West Michigan", "United States", True, "paid", True, True, True, False, 
             True, True, "year-round", "none", "sand", True, True, "Michigan State Parks", 
             "https://www.michigan.gov/dnr/places/state-parks/holland", "616-399-9390"),
             
            (57, "Tahquamenon Falls Upper Falls Trail", 1.2, 25, "easy", True, "out and back", "waterfall,forest,river", 
             46.5683, -85.2550, "Easy walk to one of Michigan's most impressive waterfalls.",
             "Paradise", "Chippewa County", "Michigan", "Upper Peninsula", "United States", True, "paid", True, True, True, False, 
             True, False, "year-round", "wheelchair", "boardwalk", True, False, "Michigan State Parks", 
             "https://www.michigan.gov/dnr/places/state-parks/tahquamenon-falls", "906-492-3415"),
             
            (58, "Silver Lake Sand Dunes", 4.8, 120, "moderate", True, "loop", "dunes,lake,ORV area", 
             43.6833, -86.4833, "Unique sand dune environment with off-road vehicle area and lake access.",
             "Mears", "Oceana County", "Michigan", "West Michigan", "United States", True, "paid", True, True, False, False, 
             True, False, "year-round", "none", "sand", True, True, "Michigan State Parks", 
             "https://www.michigan.gov/dnr/places/state-parks/silver-lake", "231-873-3083"),
             
            (59, "Porcupine Mountains Escarpment Trail", 7.2, 380, "hard", True, "out and back", "mountains,forest,overlook", 
             46.8167, -89.9333, "Challenging trail to spectacular overlook of Lake of the Clouds.",
             "Ontonagon", "Ontonagon County", "Michigan", "Upper Peninsula", "United States", True, "paid", True, True, False, False, 
             True, True, "year-round", "none", "dirt", True, False, "Michigan State Parks", 
             "https://www.michigan.gov/dnr/places/state-parks/porcupine-mountains", "906-885-5275"),
             
            # INDIANA - Driving Range from Chicago (1-3 hours)
            
            (60, "Turkey Run State Park Trail 3", 1.8, 45, "moderate", True, "loop", "canyon,creek,sandstone", 
             39.8667, -87.2333, "Scenic canyon trail through Sugar Creek gorge with ladder climbs.",
             "Marshall", "Parke County", "Indiana", "West Central Indiana", "United States", True, "paid", True, True, True, True, 
             True, False, "year-round", "none", "dirt", True, True, "Indiana State Parks", 
             "https://www.in.gov/dnr/parksandreservoir/2964.htm", "765-597-2635"),
             
            (61, "Brown County State Park Trail 5", 6.4, 185, "moderate", True, "loop", "hills,forest,overlook", 
             39.1333, -86.2333, "Rolling trail through Indiana's hill country with scenic overlooks.",
             "Nashville", "Brown County", "Indiana", "South Central Indiana", "United States", True, "paid", True, True, True, True, 
             True, True, "year-round", "none", "dirt", True, True, "Indiana State Parks", 
             "https://www.in.gov/dnr/parksandreservoir/2988.htm", "812-988-6406"),
             
            (62, "Pokagon State Park Potawatomi Trail", 4.2, 95, "moderate", True, "loop", "lake,hills,toboggan", 
             41.7833, -85.0167, "Hilly trail system around Lake James with winter toboggan run.",
             "Angola", "Steuben County", "Indiana", "Northeast Indiana", "United States", True, "paid", True, True, True, True, 
             True, True, "year-round", "none", "dirt", True, True, "Indiana State Parks", 
             "https://www.in.gov/dnr/parksandreservoir/2968.htm", "260-833-2012"),
             
            (63, "Shades State Park Trail 6", 2.3, 75, "moderate", True, "loop", "canyon,creek,ladders", 
             39.9333, -87.1167, "Adventure trail with ladder descents into Sugar Creek canyon.",
             "Waveland", "Montgomery County", "Indiana", "West Central Indiana", "United States", True, "paid", True, True, True, False, 
             True, False, "year-round", "none", "dirt", True, True, "Indiana State Parks", 
             "https://www.in.gov/dnr/parksandreservoir/2971.htm", "765-435-2810"),
             
            # IOWA - Driving Range from Chicago (3-5 hours)
            
            (64, "Maquoketa Caves State Park", 3.8, 85, "moderate", True, "loop", "caves,limestone,forest", 
             42.0667, -90.6500, "Unique trail system connecting multiple limestone caves.",
             "Maquoketa", "Jackson County", "Iowa", "Eastern Iowa", "United States", True, "free", True, True, True, False, 
             False, False, "year-round", "none", "dirt", True, True, "Iowa Department of Natural Resources", 
             "https://www.iowadnr.gov/Places-to-Go/State-Parks/Iowa-State-Parks/ParkDetails/ParkID/610156", "563-652-5833"),
             
            (65, "Effigy Mounds Fire Point Trail", 2.6, 120, "moderate", True, "out and back", "historic,bluff,river", 
             43.2167, -91.1000, "Historic trail to Native American effigy mounds with Mississippi River views.",
             "Harpers Ferry", "Allamakee County", "Iowa", "Northeast Iowa", "United States", True, "free", True, True, False, False, 
             True, False, "year-round", "none", "dirt", True, False, "National Park Service", 
             "https://www.nps.gov/efmo/", "563-873-3491"),
             
            (66, "Backbone State Park", 5.1, 140, "moderate", True, "loop", "bluff,river,limestone", 
             42.6167, -91.4833, "Iowa's first state park with dramatic limestone bluffs and Maquoketa River.",
             "Strawberry Point", "Delaware County", "Iowa", "Northeast Iowa", "United States", True, "paid", True, True, True, True, 
             True, False, "year-round", "none", "dirt", True, True, "Iowa Department of Natural Resources", 
             "https://www.iowadnr.gov/Places-to-Go/State-Parks/Iowa-State-Parks/ParkDetails/ParkID/610137", "563-924-2527"),
             
            # MISSOURI - Driving Range from Chicago (4-6 hours)
            
            (67, "Ha Ha Tonka State Park Castle Trail", 1.5, 85, "moderate", True, "out and back", "castle ruins,bluff,springs", 
             37.9833, -92.7667, "Trail to historic castle ruins with Ozark bluff-top views.",
             "Camdenton", "Camden County", "Missouri", "Lake of the Ozarks", "United States", True, "free", True, True, True, False, 
             False, False, "year-round", "none", "dirt", True, False, "Missouri State Parks", 
             "https://mostateparks.com/park/ha-ha-tonka-state-park", "573-346-2986"),
             
            (68, "Elephant Rocks State Park", 1.2, 35, "easy", True, "loop", "granite,boulders,unique geology", 
             37.5833, -90.6833, "Unique trail through massive pink granite boulders resembling elephants.",
             "Belleview", "Iron County", "Missouri", "Southeast Missouri", "United States", True, "free", True, True, True, False, 
             False, False, "year-round", "wheelchair", "paved", True, True, "Missouri State Parks", 
             "https://mostateparks.com/park/elephant-rocks-state-park", "573-546-3454"),
             
            (69, "Johnson's Shut-Ins State Park", 2.8, 55, "moderate", True, "loop", "shut-ins,swimming,granite", 
             37.5500, -90.8833, "Trail to natural water slides and pools in granite shut-ins.",
             "Middle Brook", "Reynolds County", "Missouri", "Southeast Missouri", "United States", True, "free", True, True, True, False, 
             False, False, "year-round", "none", "dirt", True, True, "Missouri State Parks", 
             "https://mostateparks.com/park/johnsons-shut-ins-state-park", "573-546-2450"),
             
            (70, "Mark Twain National Forest Bell Mountain", 9.2, 520, "hard", True, "out and back", "mountain,forest,wilderness", 
             37.4167, -90.5833, "Challenging climb to highest point in the Missouri Ozarks.",
             "Potosi", "Washington County", "Missouri", "Ozark Mountains", "United States", True, "free", False, False, False, False, 
             False, True, "year-round", "none", "dirt", True, False, "U.S. Forest Service", 
             "https://www.fs.usda.gov/main/mtnf/", "573-364-4621"),
        ]
        
        try:
            with PerformanceTimer("seed_trails", request_id) as timer:
                with self.get_connection() as conn:
                    cursor = conn.cursor()
                    
                    # Clear existing data
                    cursor.execute("DELETE FROM trails")
                    cursor.execute("DELETE FROM trails_fts")
                    logger.debug("Cleared existing trail data")
                    
                    # Insert trail data with enhanced fields
                    cursor.executemany("""
                        INSERT INTO trails (
                            id, name, distance_km, elevation_gain_m, difficulty, dogs_allowed, route_type, features, 
                            latitude, longitude, description, city, county, state, region, country, 
                            parking_available, parking_type, restrooms, water_available, picnic_areas, camping_available, 
                            entry_fee, permit_required, seasonal_access, accessibility, surface_type, trail_markers, 
                            loop_trail, managing_agency, website_url, phone_number
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, trails_data)
                
                # Populate FTS5 table with enhanced searchable fields
                cursor.execute("""
                    INSERT INTO trails_fts(rowid, name, description, features, city, county, state, region, managing_agency, surface_type, parking_type)
                    SELECT id, name, description, features, city, county, state, region, managing_agency, surface_type, parking_type FROM trails
                """)
                
                conn.commit()
                
                log_database_operation(request_id, "seed", "trails", timer.duration_ms, len(trails_data))
                logger.info(f"Database seeded with {len(trails_data)} trails")
                return len(trails_data)
                
        except Exception as e:
            logger.error(f"Failed to seed database: {e}")
            return 0
    
    def get_trail_by_id(self, trail_id: int, request_id: str = "get_trail") -> Optional[Dict[str, Any]]:
        """Get full trail details by ID"""
        logger.debug(f"Getting trail details for ID: {trail_id}")
        
        try:
            with PerformanceTimer("get_trail_by_id", request_id) as timer:
                with self.get_connection() as conn:
                    cursor = conn.cursor()
                    
                    cursor.execute("SELECT * FROM trails WHERE id = ?", (trail_id,))
                    row = cursor.fetchone()
                    
                log_database_operation(request_id, "select", "trails", timer.duration_ms, 1 if row else 0)
                
                if not row:
                    logger.warning(f"Trail with ID {trail_id} not found")
                    return None
                
                result = {
                    'id': row['id'],
                    'name': row['name'],
                    'distance_miles': km_to_miles(row['distance_km']),
                    'elevation_gain_m': row['elevation_gain_m'],
                    'difficulty': row['difficulty'],
                    'dogs_allowed': bool(row['dogs_allowed']),
                    'route_type': row['route_type'],
                    'features': row['features'].split(','),
                    'latitude': row['latitude'],
                    'longitude': row['longitude'],
                    'description': row['description'],
                    
                    # Enhanced location information
                    'city': row['city'],
                    'county': row['county'],
                    'state': row['state'],
                    'region': row['region'],
                    'country': row['country'],
                    
                    # Amenities and access information
                    'parking_available': bool(row['parking_available']) if row['parking_available'] is not None else None,
                    'parking_type': row['parking_type'],
                    'restrooms': bool(row['restrooms']) if row['restrooms'] is not None else None,
                    'water_available': bool(row['water_available']) if row['water_available'] is not None else None,
                    'picnic_areas': bool(row['picnic_areas']) if row['picnic_areas'] is not None else None,
                    'camping_available': bool(row['camping_available']) if row['camping_available'] is not None else None,
                    
                    # Access and permit information
                    'entry_fee': bool(row['entry_fee']) if row['entry_fee'] is not None else None,
                    'permit_required': bool(row['permit_required']) if row['permit_required'] is not None else None,
                    'seasonal_access': row['seasonal_access'],
                    'accessibility': row['accessibility'],
                    
                    # Trail characteristics
                    'surface_type': row['surface_type'],
                    'trail_markers': bool(row['trail_markers']) if row['trail_markers'] is not None else None,
                    'loop_trail': bool(row['loop_trail']) if row['loop_trail'] is not None else None,
                    
                    # Contact and website
                    'managing_agency': row['managing_agency'],
                    'website_url': row['website_url'],
                    'phone_number': row['phone_number']
                }
                
                logger.debug(f"Retrieved trail: {result['name']}")
                return result
                
        except Exception as e:
            logger.error(f"Failed to get trail by ID {trail_id}: {e}")
            return None
    
    def get_all_trails(self, limit: int = 100, area_filter: str = None, request_id: str = "get_all") -> List[Dict[str, Any]]:
        """
        Get all trails from the database, optionally filtered by area
        
        Args:
            limit: Maximum number of trails to return
            area_filter: Optional area name to filter by (e.g., 'Chicago', 'Illinois')
            request_id: Request ID for logging
            
        Returns:
            List of trail dictionaries
        """
        logger.info(f"Getting all trails (limit: {limit}, area: {area_filter}) (Request: {request_id})")
        
        try:
            with PerformanceTimer("get_all_trails", request_id) as timer:
                with self.get_connection() as conn:
                    cursor = conn.cursor()
                    
                    # Build query with optional area filter
                    base_sql = """
                        SELECT t.*, 1.0 as rank_score 
                        FROM trails t 
                        WHERE 1=1
                    """
                    params = []
                    
                    # Apply area filter if provided
                    if area_filter:
                        # Look for area name in trail name, description, features, city, county, state, or region
                        area_filter_lower = area_filter.lower()
                        base_sql += """ AND (
                            LOWER(t.name) LIKE ? OR 
                            LOWER(t.description) LIKE ? OR 
                            LOWER(t.features) LIKE ? OR
                            LOWER(t.city) LIKE ? OR
                            LOWER(t.county) LIKE ? OR
                            LOWER(t.state) LIKE ? OR
                            LOWER(t.region) LIKE ?
                        )"""
                        area_pattern = f"%{area_filter_lower}%"
                        params.extend([area_pattern, area_pattern, area_pattern, area_pattern, area_pattern, area_pattern, area_pattern])
                        logger.debug(f"Added area filter: {area_filter}")
                    
                    # Order by difficulty (easy first), then distance
                    base_sql += """ 
                        ORDER BY 
                            CASE WHEN t.difficulty = 'easy' THEN 1 
                                 WHEN t.difficulty = 'moderate' THEN 2 
                                 WHEN t.difficulty = 'hard' THEN 3 
                                 ELSE 4 END,
                            t.distance_km ASC 
                        LIMIT ?
                    """
                    params.append(limit)
                    
                    logger.debug(f"All trails query SQL: {base_sql} (Request: {request_id})")
                    logger.debug(f"All trails query params: {params} (Request: {request_id})")
                    
                    cursor.execute(base_sql, params)
                    rows = cursor.fetchall()
                    
                    results = []
                    for row in rows:
                        result = {
                            'id': row['id'],
                            'name': row['name'],
                            'distance_miles': km_to_miles(row['distance_km']),
                            'distance_km': row['distance_km'],
                            'elevation_gain_m': row['elevation_gain_m'],
                            'difficulty': row['difficulty'],
                            'dogs_allowed': bool(row['dogs_allowed']),
                            'route_type': row['route_type'],
                            'features': row['features'].split(',') if row['features'] else [],
                            'latitude': row['latitude'],
                            'longitude': row['longitude'],
                            'description': row['description'],
                            'rank_score': row['rank_score'],
                            
                            # Enhanced location information
                            'city': row['city'],
                            'county': row['county'],
                            'state': row['state'],
                            'region': row['region'],
                            'country': row['country'],
                            
                            # Amenities and access information
                            'parking_available': bool(row['parking_available']) if row['parking_available'] is not None else None,
                            'parking_type': row['parking_type'],
                            'restrooms': bool(row['restrooms']) if row['restrooms'] is not None else None,
                            'water_available': bool(row['water_available']) if row['water_available'] is not None else None,
                            'picnic_areas': bool(row['picnic_areas']) if row['picnic_areas'] is not None else None,
                            'camping_available': bool(row['camping_available']) if row['camping_available'] is not None else None,
                            
                            # Access and permit information
                            'entry_fee': bool(row['entry_fee']) if row['entry_fee'] is not None else None,
                            'permit_required': bool(row['permit_required']) if row['permit_required'] is not None else None,
                            'seasonal_access': row['seasonal_access'],
                            'accessibility': row['accessibility'],
                            
                            # Trail characteristics
                            'surface_type': row['surface_type'],
                            'trail_markers': bool(row['trail_markers']) if row['trail_markers'] is not None else None,
                            'loop_trail': bool(row['loop_trail']) if row['loop_trail'] is not None else None,
                            
                            # Contact and website
                            'managing_agency': row['managing_agency'],
                            'website_url': row['website_url'],
                            'phone_number': row['phone_number']
                        }
                        results.append(result)
                    
                    log_database_operation(request_id, "get_all_trails", timer.duration_ms, len(results))
                    logger.info(f"Retrieved {len(results)} trails in {timer.duration_ms}ms (Request: {request_id})")
                    
                    return results
                    
        except Exception as e:
            logger.error(f"Failed to get all trails: {e} (Request: {request_id})")
            raise

# Global database manager instance
db_manager = DatabaseManager(pool_size=DB_POOL_SIZE)
