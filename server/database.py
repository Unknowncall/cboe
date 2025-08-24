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
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """)
                    
                    # Create FTS5 table with weighted columns
                    cursor.execute("""
                        CREATE VIRTUAL TABLE IF NOT EXISTS trails_fts USING fts5(
                            name, description, features,
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
                
                conn.commit()
                conn.close()
                
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
        """Seed database with Chicago and Midwest trails"""
        logger.info("Seeding database with trail data")
        
        trails_data = [
            # Original trails
            (1, "Lakefront Trail Loop", 3.2, 5, "easy", True, "loop", "lake,boardwalk,urban", 41.8819, -87.6278, "Scenic loop along Lake Michigan with stunning skyline views and boardwalk sections."),
            (2, "Starved Rock Waterfall Trail", 4.8, 120, "moderate", True, "out and back", "waterfall,canyon,forest", 41.3186, -88.9951, "Beautiful trail leading to cascading waterfalls through wooded canyons."),
            (3, "Indiana Dunes Beach Trail", 2.1, 45, "easy", True, "loop", "dunes,beach,lake", 41.6532, -87.0921, "Short loop through impressive sand dunes with Lake Michigan access."),
            (4, "Kettle Moraine Prairie Path", 6.7, 85, "moderate", True, "loop", "prairie,wildflowers,hills", 42.9633, -88.5439, "Rolling prairie trail with seasonal wildflowers and glacial landscape features."),
            (5, "Chicago Riverwalk", 2.4, 0, "easy", False, "out and back", "urban,river,boardwalk", 41.8887, -87.6233, "Urban boardwalk along the Chicago River through downtown architecture."),
            (6, "Palos Forest Preserve", 8.2, 65, "moderate", True, "loop", "forest,creek,hills", 41.6611, -87.8167, "Peaceful forest trail with creek crossings and gentle elevation changes."),
            (7, "Devil's Lake State Park", 12.4, 380, "hard", True, "loop", "lake,bluffs,quartzite", 43.4221, -89.7251, "Challenging loop around pristine lake with dramatic quartzite bluffs."),
            (8, "Millennium Park Garden Walk", 1.8, 15, "easy", False, "loop", "garden,urban,art", 41.8826, -87.6220, "Easy urban walk through award-winning gardens and public art installations."),
            (9, "Warren Dunes Summit Trail", 5.3, 190, "moderate", True, "out and back", "dunes,beach,forest", 41.9089, -86.5986, "Moderate climb to the highest dune with panoramic lake views."),
            (10, "Fox River Trail", 7.9, 25, "easy", True, "out and back", "river,prairie,boardwalk", 42.3297, -88.3251, "Flat trail following the Fox River with prairie restoration areas."),
            (11, "Galena River Trail", 4.1, 55, "easy", True, "loop", "river,prairie,historic", 42.4167, -90.4290, "Gentle trail along historic river valley with interpretive features."),
            (12, "Chain O'Lakes Waterfall Hike", 3.6, 95, "moderate", False, "out and back", "waterfall,lake,forest", 42.4167, -88.1833, "Moderate hike to hidden waterfall with chain of pristine lakes."),
            (13, "Illinois Beach Dunes Walk", 2.8, 20, "easy", True, "loop", "dunes,beach,prairie", 42.4439, -87.8061, "Easy coastal walk through preserved dunes and beach prairie."),
            (14, "Busse Woods Loop", 6.1, 35, "easy", True, "loop", "lake,forest,boardwalk", 42.0431, -87.9673, "Popular family loop around lake with boardwalk sections and wildlife viewing."),
            (15, "Castle Rock Overlook", 9.7, 245, "hard", True, "out and back", "bluffs,forest,overlook", 41.3186, -88.9951, "Challenging hike to dramatic rock formation with valley views."),
            (16, "Montrose Beach Boardwalk", 1.4, 0, "easy", True, "out and back", "beach,boardwalk,urban", 41.9639, -87.6361, "Short accessible boardwalk along popular beach with city skyline views."),
            (17, "Matthiessen Falls Trail", 2.9, 75, "moderate", True, "loop", "waterfall,canyon,creek", 41.3186, -88.9751, "Spectacular trail through narrow canyon to multiple waterfalls."),
            (18, "Chicago Botanic Garden", 4.5, 25, "easy", False, "loop", "garden,lake,boardwalk", 42.1458, -87.7856, "Peaceful garden paths with themed areas and boardwalk over lagoons."),
            
            # Additional Chicago Area Trails
            (19, "North Shore Channel Trail", 10.2, 30, "easy", True, "out and back", "river,urban,prairie", 42.0333, -87.7000, "Long paved trail following the North Shore Channel through multiple suburbs."),
            (20, "Des Plaines River Trail", 14.5, 45, "easy", True, "out and back", "river,forest,prairie", 42.1500, -87.8500, "Extensive trail system following the Des Plaines River with diverse ecosystems."),
            (21, "Salt Creek Trail", 8.7, 55, "easy", True, "loop", "creek,forest,prairie", 41.8000, -87.9000, "Peaceful trail along Salt Creek with native prairie restorations."),
            (22, "Waterfall Glen Forest Preserve", 9.5, 85, "moderate", True, "loop", "forest,creek,hills", 41.7167, -87.9833, "Rolling terrain through oak woodlands with seasonal creek crossings."),
            (23, "Illinois Prairie Path", 16.8, 40, "easy", True, "out and back", "prairie,historic,urban", 41.8833, -88.0000, "Historic rail-to-trail conversion through prairie and suburban areas."),
            (24, "Tekakwitha Woods", 3.4, 65, "easy", True, "loop", "forest,creek,hills", 41.7500, -87.7500, "Quiet forest preserve with gentle hills and seasonal wildflowers."),
            (25, "Ned Brown Preserve", 5.2, 25, "easy", True, "loop", "lake,prairie,forest", 42.0667, -88.0333, "Multi-habitat preserve with lake views and prairie restoration."),
            (26, "Springbrook Prairie", 4.1, 20, "easy", True, "loop", "prairie,wildflowers,creek", 41.8167, -88.0833, "Restored tallgrass prairie with seasonal wildflower displays."),
            (27, "Sagawau Canyon", 2.8, 95, "moderate", True, "loop", "canyon,creek,forest", 41.6833, -87.8167, "Short but scenic canyon trail with rock formations."),
            (28, "Blackwell Forest Preserve", 6.9, 45, "easy", True, "loop", "lake,forest,prairie", 41.8167, -88.1000, "Large preserve with multiple trail options around lake."),
            
            # Wisconsin Trails (accessible from Chicago)
            (29, "Geneva Lake Shore Path", 21.1, 60, "moderate", False, "loop", "lake,historic,beach", 42.5917, -88.5417, "Complete loop around pristine glacial lake with historic estates."),
            (30, "Kettle Moraine Ice Age Trail", 18.2, 250, "hard", True, "out and back", "hills,forest,prairie", 42.9000, -88.4000, "Challenging trail through glacial landscape with significant elevation."),
            (31, "Parfrey's Glen", 1.6, 120, "moderate", True, "out and back", "canyon,creek,forest", 43.4167, -89.7000, "Short but spectacular gorge hike to hidden waterfall."),
            (32, "Blue Mound State Park", 7.3, 180, "moderate", True, "loop", "prairie,overlook,hills", 43.0333, -89.8333, "Prairie and woodland trail to the highest point in southern Wisconsin."),
            (33, "Mirror Lake State Park", 5.4, 85, "easy", True, "loop", "lake,forest,beach", 43.5833, -89.8167, "Easy loop around pristine lake with sandstone formations."),
            (34, "Governor Dodge State Park", 11.7, 220, "hard", True, "loop", "bluffs,forest,creek", 43.0167, -90.1167, "Rugged trail through blufflands with panoramic views."),
            (35, "Pewit's Nest", 1.2, 80, "moderate", True, "out and back", "canyon,waterfall,creek", 43.4500, -89.9000, "Short gorge walk to dramatic sandstone canyon and waterfall."),
            
            # Michigan Trails
            (36, "Saugatuck Dunes State Park", 4.3, 120, "moderate", True, "loop", "dunes,beach,forest", 42.6500, -86.2000, "Coastal dunes trail with Lake Michigan overlooks."),
            (37, "Holland State Park Beach Trail", 2.7, 15, "easy", True, "out and back", "beach,dunes,lighthouse", 42.7667, -86.2083, "Easy beach walk to historic lighthouse."),
            (38, "Sleeping Bear Dunes", 8.9, 300, "hard", True, "out and back", "dunes,beach,overlook", 44.8833, -86.0333, "Challenging climb up massive sand dunes with spectacular views."),
            (39, "Silver Lake Sand Dunes", 3.5, 150, "moderate", True, "loop", "dunes,lake,beach", 43.6833, -86.4833, "Loop through impressive sand dune ecosystem."),
            (40, "Grand Mere State Park", 2.4, 45, "easy", True, "loop", "dunes,beach,prairie", 41.9667, -86.6167, "Short coastal trail through dune succession habitats."),
            
            # Iowa and Illinois Extended
            (41, "Maquoketa Caves State Park", 6.2, 140, "moderate", True, "loop", "caves,bluffs,forest", 42.0667, -90.6667, "Unique trail system through limestone caves and bluffs."),
            (42, "Pikes Peak State Park Iowa", 4.8, 180, "moderate", True, "out and back", "bluffs,river,overlook", 43.2167, -91.1333, "Mississippi River bluff trail with dramatic overlooks."),
            (43, "Backbone State Park", 7.1, 160, "moderate", True, "loop", "bluffs,creek,forest", 42.4167, -91.4667, "Rugged trail along narrow limestone ridge."),
            (44, "White Pines Forest State Park", 3.9, 35, "easy", True, "loop", "forest,creek,historic", 41.8167, -89.6500, "Gentle trail through rare white pine forest."),
            (45, "Cahokia Mounds", 5.2, 95, "moderate", False, "loop", "historic,prairie,overlook", 38.6500, -90.0667, "Historic trail over ancient Native American mounds."),
            
            # Indiana Trails
            (46, "Indiana Dunes National Park", 7.8, 110, "moderate", True, "loop", "dunes,beach,forest", 41.6333, -87.0833, "Comprehensive dunes experience with diverse ecosystems."),
            (47, "Turkey Run State Park", 8.4, 130, "moderate", True, "loop", "canyon,creek,forest", 39.9333, -87.2000, "Sandstone canyon trail with dramatic rock formations."),
            (48, "Shades State Park", 6.7, 120, "moderate", True, "loop", "canyon,creek,bluffs", 39.9833, -87.1333, "Deep ravines and sandstone formations along Sugar Creek."),
            (49, "Brown County State Park", 12.3, 280, "hard", True, "loop", "hills,forest,overlook", 39.1667, -86.2500, "Challenging hilly terrain through Indiana's largest state park."),
            (50, "Falls of the Ohio", 2.6, 20, "easy", True, "out and back", "river,historic,fossil", 38.2833, -85.7667, "Easy walk along Ohio River with 390-million-year-old fossil beds."),
            
            # Missouri Trails (accessible for longer trips)
            (51, "Ha Ha Tonka State Park", 9.1, 200, "moderate", True, "loop", "bluffs,lake,historic", 37.9667, -92.7500, "Ozark bluffs trail with castle ruins and spring-fed lake."),
            (52, "Elephant Rocks State Park", 1.8, 30, "easy", True, "loop", "rocks,forest,historic", 37.6000, -90.6333, "Easy walk among giant pink granite boulders."),
            (53, "Johnson's Shut-Ins", 3.4, 75, "moderate", True, "loop", "creek,rocks,forest", 37.5333, -90.8833, "Unique rock formations with natural water slides."),
            
            # Minnesota Trails
            (54, "Minnehaha Falls", 2.1, 40, "easy", True, "loop", "waterfall,creek,urban", 44.9167, -93.2117, "Urban waterfall hike in Minneapolis with limestone gorge."),
            (55, "Gooseberry Falls State Park", 5.8, 95, "moderate", True, "loop", "waterfall,lake,forest", 47.1333, -91.4667, "Lake Superior coastal trail with multiple waterfalls."),
            (56, "Split Rock Lighthouse", 3.7, 85, "moderate", True, "out and back", "lighthouse,lake,bluffs", 47.2000, -91.3667, "Scenic coastal hike to historic lighthouse on Lake Superior."),
            (57, "Pipestone National Monument", 2.3, 25, "easy", True, "loop", "prairie,historic,creek", 44.0167, -96.3167, "Sacred quarry site with prairie restoration and cultural significance."),
            
            # Urban Chicago Trails
            (58, "606 Trail (Bloomingdale)", 2.7, 15, "easy", True, "out and back", "urban,art,elevated", 41.9100, -87.6800, "Elevated linear park on former railway with city views."),
            (59, "North Branch Trail", 20.3, 50, "easy", True, "out and back", "river,forest,urban", 42.0500, -87.7500, "Long trail following North Branch Chicago River."),
            (60, "Burnham Greenway", 11.2, 25, "easy", True, "out and back", "urban,lake,prairie", 41.7000, -87.5500, "Connects multiple parks and natural areas in south Chicago."),
            (61, "Major Taylor Trail", 6.8, 30, "easy", True, "out and back", "urban,prairie,historic", 41.7500, -87.6000, "Trail honoring cycling champion through south side neighborhoods."),
            (62, "Big Marsh Park", 4.1, 20, "easy", True, "loop", "prairie,urban,wetlands", 41.6833, -87.5500, "Former industrial site restored to prairie and wetlands."),
            
            # Easy Family Trails
            (63, "Morton Arboretum", 3.8, 35, "easy", False, "loop", "garden,forest,lake", 41.8167, -88.0667, "Beautiful arboretum with themed tree collections and lake views."),
            (64, "Brookfield Zoo Nature Trail", 2.2, 15, "easy", False, "loop", "urban,garden,zoo", 41.8333, -87.8167, "Educational nature trail within zoo grounds."),
            (65, "Garfield Park Conservatory", 1.3, 5, "easy", False, "loop", "garden,urban,historic", 41.8833, -87.7167, "Indoor and outdoor garden trails in historic conservatory."),
            (66, "Oak Brook Forest Preserve", 4.6, 40, "easy", True, "loop", "forest,creek,prairie", 41.8333, -87.9500, "Gentle family trail through mixed habitats."),
            (67, "Cantigny Park", 3.2, 25, "easy", True, "loop", "garden,historic,prairie", 41.8667, -88.1667, "Historic estate grounds with formal gardens and prairie."),
            
            # Challenging Trails
            (68, "Starved Rock Eagle Cliff", 11.8, 320, "hard", True, "out and back", "bluffs,forest,overlook", 41.3186, -88.9951, "Extended challenging hike to highest overlook in park."),
            (69, "Illinois Beach Ridge Trail", 8.9, 75, "moderate", True, "out and back", "beach,dunes,forest", 42.4500, -87.8000, "Long beach hike through dune succession habitats."),
            (70, "Kankakee River State Park", 13.4, 180, "hard", True, "loop", "river,bluffs,forest", 41.2000, -87.9667, "Challenging river bluff trail with rock canyon sections."),
            (71, "Apple River Canyon", 7.2, 220, "hard", True, "loop", "canyon,creek,bluffs", 42.4833, -90.0833, "Steep canyon trail with limestone formations and waterfalls."),
            (72, "Castle Rock State Park", 15.6, 380, "hard", True, "loop", "bluffs,forest,overlook", 41.9500, -89.0500, "Extensive trail system with dramatic sandstone formations."),
            
            # Waterfall and Canyon Trails
            (73, "LaSalle Canyon", 3.6, 85, "moderate", True, "out and back", "waterfall,canyon,forest", 41.3186, -88.9951, "Narrow canyon hike to seasonal waterfall."),
            (74, "Wildcat Canyon", 2.4, 95, "moderate", True, "out and back", "waterfall,canyon,creek", 41.3186, -88.9951, "Short but steep canyon trail to hidden falls."),
            (75, "Ottawa Canyon", 4.1, 110, "moderate", True, "loop", "canyon,waterfall,bluffs", 41.3500, -88.8500, "Scenic canyon with multiple seasonal waterfalls."),
            (76, "French Canyon", 1.8, 65, "easy", True, "out and back", "waterfall,canyon,moss", 41.3186, -88.9951, "Short accessible hike to moss-covered waterfall."),
            (77, "Tonty Canyon", 2.7, 75, "moderate", True, "out and back", "waterfall,canyon,creek", 41.3186, -88.9951, "Moderate canyon hike with year-round stream."),
            
            # Lake and River Trails
            (78, "Chain O'Lakes State Park", 8.3, 45, "easy", True, "loop", "lake,prairie,forest", 42.4167, -88.1833, "Multi-lake trail system with diverse wildlife viewing."),
            (79, "Moraine Hills State Park", 10.2, 65, "moderate", True, "loop", "lake,prairie,hills", 42.3833, -88.2333, "Glacial landscape with kettle lakes and prairie."),
            (80, "Volo Bog State Natural Area", 2.8, 15, "easy", True, "loop", "bog,boardwalk,rare plants", 42.3333, -88.1667, "Unique bog ecosystem with rare plants and boardwalk."),
            (81, "McHenry Dam Trail", 3.4, 20, "easy", True, "out and back", "river,dam,urban", 42.3333, -88.2667, "Riverside trail along Fox River with historic dam."),
            (82, "Glacial Park", 6.7, 55, "moderate", True, "loop", "prairie,wetlands,hills", 42.3500, -88.3167, "Restored prairie and wetlands with glacial kames."),
            
            # Historic and Cultural Trails
            (83, "Illinois & Michigan Canal Trail", 24.5, 60, "easy", True, "out and back", "historic,canal,urban", 41.6000, -88.0000, "Historic canal towpath through multiple communities."),
            (84, "Lewis and Clark Trail", 8.9, 85, "moderate", True, "out and back", "river,historic,bluffs", 38.8167, -90.2500, "Historic expedition route along Missouri River bluffs."),
            (85, "Black Hawk State Historic Site", 4.2, 75, "moderate", True, "loop", "historic,bluffs,forest", 41.5000, -90.5833, "Trail through historic Sauk and Fox village site."),
            (86, "Fort Sheridan Forest Preserve", 5.1, 85, "moderate", True, "loop", "historic,lake,bluffs", 42.2167, -87.8000, "Former military base with lake bluff trails."),
            
            # Seasonal and Wildflower Trails
            (87, "Nachusa Grasslands", 7.8, 40, "easy", True, "loop", "prairie,wildflowers,bison", 41.8833, -89.3333, "Restored prairie with free-roaming bison herd."),
            (88, "Midewin National Tallgrass Prairie", 12.1, 75, "moderate", True, "loop", "prairie,wildflowers,bison", 41.3167, -88.0000, "Massive prairie restoration with bison and diverse wildflowers."),
            (89, "Bluff Spring Fen", 2.6, 25, "easy", True, "loop", "fen,wildflowers,boardwalk", 41.7000, -87.8500, "Rare fen ecosystem with spring wildflowers and boardwalk."),
            (90, "Orland Grassland", 4.3, 30, "easy", True, "loop", "prairie,wildflowers,birds", 41.5833, -87.8500, "Restored grassland with excellent birding and wildflowers."),
            
            # Winter and Multi-Season Trails
            (91, "Deer Grove Forest Preserve", 6.4, 45, "easy", True, "loop", "forest,creek,winter", 42.1167, -88.0333, "Year-round trail with winter skiing and summer hiking."),
            (92, "Pratt's Wayne Woods", 7.2, 55, "moderate", True, "loop", "forest,prairie,winter", 41.9167, -88.2500, "Multi-season trail with cross-country skiing in winter."),
            (93, "Herrick Lake Forest Preserve", 5.8, 35, "easy", True, "loop", "lake,forest,winter", 41.8333, -88.1167, "Four-season trail with winter activities and summer fishing."),
            (94, "West DuPage Woods", 4.7, 40, "easy", True, "loop", "forest,creek,winter", 41.8667, -88.0833, "Peaceful forest preserve with year-round trail access."),
            (95, "Churchill Woods Forest Preserve", 3.9, 30, "easy", True, "loop", "forest,prairie,winter", 41.9000, -88.0167, "Mixed habitat preserve with winter and summer trails."),
            
            # Accessible and Paved Trails
            (96, "Great Western Trail", 18.2, 40, "easy", True, "out and back", "paved,prairie,urban", 41.9000, -88.4000, "Long paved trail through multiple suburbs and prairie."),
            (97, "Prairie Trail", 26.1, 50, "easy", True, "out and back", "paved,prairie,lake", 42.2000, -88.2000, "Extensive paved trail connecting multiple communities."),
            (98, "Fox River Trail", 40.3, 60, "easy", True, "out and back", "paved,river,urban", 42.3000, -88.3000, "Long paved trail following Fox River through many towns."),
            (99, "Old Plank Road Trail", 22.1, 35, "easy", True, "out and back", "paved,prairie,historic", 41.5500, -87.9000, "Historic route converted to paved recreational trail."),
            (100, "Constitution Trail", 45.2, 80, "easy", True, "out and back", "paved,prairie,urban", 40.5167, -88.9833, "Very long paved trail connecting Bloomington-Normal area.")
        ]
        
        try:
            with PerformanceTimer("seed_trails", request_id) as timer:
                with self.get_connection() as conn:
                    cursor = conn.cursor()
                    
                    # Clear existing data
                    cursor.execute("DELETE FROM trails")
                    cursor.execute("DELETE FROM trails_fts")
                    logger.debug("Cleared existing trail data")
                    
                    # Insert trail data
                    cursor.executemany("""
                        INSERT INTO trails (id, name, distance_km, elevation_gain_m, difficulty, dogs_allowed, route_type, features, latitude, longitude, description)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, trails_data)
                
                # Populate FTS5 table
                cursor.execute("""
                    INSERT INTO trails_fts(rowid, name, description, features)
                    SELECT id, name, description, features FROM trails
                """)
                
                conn.commit()
                conn.close()
                
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
                    'description': row['description']
                }
                
                logger.debug(f"Retrieved trail: {result['name']}")
                return result
                
        except Exception as e:
            logger.error(f"Failed to get trail by ID {trail_id}: {e}")
            return None

# Global database manager instance
db_manager = DatabaseManager(pool_size=DB_POOL_SIZE)
