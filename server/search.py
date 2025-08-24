"""
Search and filtering logic for the CBOE Trail Search API
"""
import re
import logging
import time
from typing import List, Dict, Any, Optional

from models import ParsedFilters
from config import CHICAGO_LAT, CHICAGO_LNG, DEFAULT_RADIUS_MILES, MAX_RESULTS, TOP_RESULTS_LIMIT
from database import db_manager
from utils import (
    geo_distance, 
    log_request, 
    log_search_query, 
    log_filter_application, 
    truncate_description,
    PerformanceTimer,
    km_to_miles,
    miles_to_km
)

logger = logging.getLogger("trail_search.search")

class TextParser:
    """Simplified parser - AI does the heavy lifting now"""
    
    def __init__(self):
        logger.debug("Initialized simplified TextParser - AI handles parsing")
    
    def parse_user_input(self, text: str, request_id: str = "parse") -> ParsedFilters:
        """Minimal parser - returns empty filters since AI does the real parsing"""
        logger.info(f"Minimal parsing for: '{text}' - AI handles extraction (Request: {request_id})")
        
        # Return basic empty filters - AI will provide all the real data
        filters = ParsedFilters()
        
        # Only do very basic Chicago location detection as fallback
        text_lower = text.lower()
        if 'chicago' in text_lower and not any([
            'milwaukee', 'madison', 'indianapolis', 'detroit', 'st. louis'
        ]):
            filters.center_lat = CHICAGO_LAT
            filters.center_lng = CHICAGO_LNG
            filters.radius_miles = DEFAULT_RADIUS_MILES
            logger.debug(f"Set Chicago as default location (Request: {request_id})")
        
        logger.info(f"Minimal parsed filters: {filters.model_dump()} (Request: {request_id})")
        return filters

class TrailSearcher:
    """Handles trail search operations"""
    
    def __init__(self):
        self.text_parser = TextParser()
        logger.debug("Initialized TrailSearcher")
    
    def search_trails(self, query_text: str, filters: ParsedFilters, request_id: str = "search") -> List[Dict[str, Any]]:
        """Search trails using AI-provided filters - simplified approach"""
        logger.info(f"AI-driven search with query: '{query_text}' (Request: {request_id})")
        logger.info(f"AI-provided filters: {filters.model_dump()} (Request: {request_id})")
        
        try:
            with PerformanceTimer("ai_search", request_id) as timer:
                # Direct search with AI-provided filters
                raw_results = self._fts5_search(query_text, filters, request_id)
                logger.info(f"FTS5 search returned {len(raw_results)} results (Request: {request_id})")
                
                # Apply geographic filtering if specified
                filtered_results = self._apply_geographic_filter(raw_results, filters, request_id)
                logger.info(f"After geographic filtering: {len(filtered_results)} results (Request: {request_id})")
                
                # Format results with explanations
                formatted_results = self._format_results(filtered_results, filters, request_id)
                
                log_request(request_id, "ai_search", timer.duration_ms, len(formatted_results))
                logger.info(f"AI search completed: {len(formatted_results)} results (Request: {request_id})")
                
                return formatted_results
                
        except Exception as e:
            logger.error(f"AI search failed: {e} (Request: {request_id})")
            raise

    def _fts5_search(self, query_text: str, filters: ParsedFilters, request_id: str) -> List[Dict[str, Any]]:
        """Perform direct SQL search using AI-extracted filters - no FTS5 needed"""
        logger.info(f"Direct SQL search using AI filters (Request: {request_id})")
        
        with PerformanceTimer("direct_sql_search", request_id) as timer:
            with db_manager.get_connection() as conn:
                cursor = conn.cursor()
                
                # Build simple SQL query using AI-extracted parameters
                base_sql = "SELECT t.*, 1.0 as rank_score FROM trails t WHERE 1=1"
                params = []
                
                logger.info(f"Direct SQL search - Building query from AI filters (Request: {request_id})")
                
                # Apply filters directly from AI extraction
                if filters.distance_cap_miles:
                    base_sql += " AND t.distance_km <= ?"
                    params.append(miles_to_km(filters.distance_cap_miles))
                    logger.debug(f"Added max distance filter: <= {filters.distance_cap_miles} miles ({miles_to_km(filters.distance_cap_miles):.2f} km)")
                
                if filters.distance_min_miles:
                    base_sql += " AND t.distance_km >= ?"
                    params.append(miles_to_km(filters.distance_min_miles))
                    logger.debug(f"Added min distance filter: >= {filters.distance_min_miles} miles ({miles_to_km(filters.distance_min_miles):.2f} km)")
                
                if filters.elevation_cap_m:
                    base_sql += " AND t.elevation_gain_m <= ?"
                    params.append(filters.elevation_cap_m)
                    logger.debug(f"Added elevation filter: <= {filters.elevation_cap_m} m")
                
                if filters.dogs_allowed is not None:
                    base_sql += " AND t.dogs_allowed = ?"
                    params.append(filters.dogs_allowed)
                    logger.debug(f"Added dog policy filter: {filters.dogs_allowed}")
                
                if filters.route_type:
                    base_sql += " AND t.route_type = ?"
                    params.append(filters.route_type)
                    logger.debug(f"Added route type filter: {filters.route_type}")
                
                # Location filters
                if filters.city:
                    base_sql += " AND LOWER(t.city) LIKE ?"
                    params.append(f"%{filters.city.lower()}%")
                    logger.debug(f"Added city filter: {filters.city}")
                
                if filters.county:
                    base_sql += " AND LOWER(t.county) LIKE ?"
                    params.append(f"%{filters.county.lower()}%")
                    logger.debug(f"Added county filter: {filters.county}")
                
                if filters.state:
                    base_sql += " AND LOWER(t.state) LIKE ?"
                    params.append(f"%{filters.state.lower()}%")
                    logger.debug(f"Added state filter: {filters.state}")
                
                if filters.region:
                    base_sql += " AND LOWER(t.region) LIKE ?"
                    params.append(f"%{filters.region.lower()}%")
                    logger.debug(f"Added region filter: {filters.region}")
                
                # Amenity filters
                if filters.parking_available is not None:
                    base_sql += " AND t.parking_available = ?"
                    params.append(filters.parking_available)
                    logger.debug(f"Added parking availability filter: {filters.parking_available}")
                
                if filters.parking_type:
                    base_sql += " AND t.parking_type = ?"
                    params.append(filters.parking_type)
                    logger.debug(f"Added parking type filter: {filters.parking_type}")
                
                if filters.restrooms is not None:
                    base_sql += " AND t.restrooms = ?"
                    params.append(filters.restrooms)
                    logger.debug(f"Added restrooms filter: {filters.restrooms}")
                
                if filters.water_available is not None:
                    base_sql += " AND t.water_available = ?"
                    params.append(filters.water_available)
                    logger.debug(f"Added water availability filter: {filters.water_available}")
                
                if filters.picnic_areas is not None:
                    base_sql += " AND t.picnic_areas = ?"
                    params.append(filters.picnic_areas)
                    logger.debug(f"Added picnic areas filter: {filters.picnic_areas}")
                
                if filters.camping_available is not None:
                    base_sql += " AND t.camping_available = ?"
                    params.append(filters.camping_available)
                    logger.debug(f"Added camping availability filter: {filters.camping_available}")
                
                # Access and permit filters
                if filters.entry_fee is not None:
                    base_sql += " AND t.entry_fee = ?"
                    params.append(filters.entry_fee)
                    logger.debug(f"Added entry fee filter: {filters.entry_fee}")
                
                if filters.permit_required is not None:
                    base_sql += " AND t.permit_required = ?"
                    params.append(filters.permit_required)
                    logger.debug(f"Added permit required filter: {filters.permit_required}")
                
                if filters.seasonal_access:
                    base_sql += " AND t.seasonal_access = ?"
                    params.append(filters.seasonal_access)
                    logger.debug(f"Added seasonal access filter: {filters.seasonal_access}")
                
                if filters.accessibility:
                    base_sql += " AND t.accessibility = ?"
                    params.append(filters.accessibility)
                    logger.debug(f"Added accessibility filter: {filters.accessibility}")
                
                # Trail characteristics
                if filters.surface_type:
                    base_sql += " AND t.surface_type = ?"
                    params.append(filters.surface_type)
                    logger.debug(f"Added surface type filter: {filters.surface_type}")
                
                if filters.trail_markers is not None:
                    base_sql += " AND t.trail_markers = ?"
                    params.append(filters.trail_markers)
                    logger.debug(f"Added trail markers filter: {filters.trail_markers}")
                
                if filters.loop_trail is not None:
                    base_sql += " AND t.loop_trail = ?"
                    params.append(filters.loop_trail)
                    logger.debug(f"Added loop trail filter: {filters.loop_trail}")
                
                if filters.managing_agency:
                    base_sql += " AND LOWER(t.managing_agency) LIKE ?"
                    params.append(f"%{filters.managing_agency.lower()}%")
                    logger.debug(f"Added managing agency filter: {filters.managing_agency}")
                
                # Difficulty filter - when specified, only show trails of that difficulty
                if filters.difficulty:
                    base_sql += " AND t.difficulty = ?"
                    params.append(filters.difficulty)
                    logger.debug(f"Added difficulty filter: {filters.difficulty}")
                
                # Feature matching with variations (at least one must match)
                if filters.features:
                    feature_conditions = []
                    for feature in filters.features:
                        # Handle common variations
                        variations = [feature]
                        if feature.lower() in ['view', 'views']:
                            variations.extend(['overlook', 'vista', 'bluff'])
                        elif feature.lower() in ['scenic']:
                            variations.extend(['view', 'views', 'overlook', 'vista', 'bluff'])
                        elif feature.lower() in ['waterfall', 'waterfalls']:
                            variations.extend(['waterfall', 'waterfalls', 'falls'])
                        elif feature.endswith('s') and len(feature) > 3:
                            variations.append(feature[:-1])  # singular
                        elif not feature.endswith('s'):
                            variations.append(feature + 's')  # plural
                        
                        for variation in variations:
                            feature_conditions.append("t.features LIKE ?")
                            params.append(f"%{variation}%")
                        
                        logger.debug(f"Added feature filter: {feature} (variations: {variations})")
                    
                    if feature_conditions:
                        base_sql += " AND (" + " OR ".join(feature_conditions) + ")"
                
                # Order by difficulty preference, then distance
                difficulty_order = "CASE WHEN t.difficulty = 'easy' THEN 1 WHEN t.difficulty = 'moderate' THEN 2 WHEN t.difficulty = 'hard' THEN 3 ELSE 4 END"
                
                if filters.difficulty:
                    if filters.difficulty == "hard":
                        # Prefer hard, then moderate, then easy
                        difficulty_order = "CASE WHEN t.difficulty = 'hard' THEN 1 WHEN t.difficulty = 'moderate' THEN 2 WHEN t.difficulty = 'easy' THEN 3 ELSE 4 END"
                    elif filters.difficulty == "easy":
                        # Prefer easy, then moderate, then hard
                        difficulty_order = "CASE WHEN t.difficulty = 'easy' THEN 1 WHEN t.difficulty = 'moderate' THEN 2 WHEN t.difficulty = 'hard' THEN 3 ELSE 4 END"
                    # moderate stays with the default order
                
                base_sql += f" ORDER BY {difficulty_order}, t.distance_km ASC, t.elevation_gain_m ASC LIMIT ?"
                params.append(MAX_RESULTS)
                
                logger.info(f"Direct SQL search - Final SQL: {base_sql} (Request: {request_id})")
                logger.info(f"Direct SQL search - Final params: {params} (Request: {request_id})")
                
                cursor.execute(base_sql, params)
                rows = cursor.fetchall()
                
                results = [dict(row) for row in rows]
                
        logger.debug(f"Direct SQL search returned {len(results)} results in {timer.duration_ms}ms")
        
        return results
    
    def _extract_fts_terms(self, query_text: str, filters: ParsedFilters) -> str:
        """Use AI-extracted filters to build optimized FTS5 search terms"""
        terms = []
        
        # Use AI-extracted structured data as primary search terms
        if filters.difficulty:
            terms.append(filters.difficulty.lower())
        
        if filters.route_type:
            terms.append(filters.route_type.lower())
        
        if filters.features:
            terms.extend([feature.lower() for feature in filters.features])
        
        # Add key terms from original query as fallback for broader matching
        # Focus on descriptive words that AI might not have categorized
        clean_query = re.sub(r'[^\w\s]', ' ', query_text.lower())
        query_words = [word for word in clean_query.split() 
                      if len(word) > 2 and word not in ['trail', 'hike', 'hiking', 'miles', 'under', 'with']]
        
        # Add meaningful query words that aren't already captured in filters
        existing_terms = set(terms)
        for word in query_words:
            if word not in existing_terms:
                terms.append(word)
        
        # If AI extracted good terms, use them; otherwise fall back to original query
        if len(terms) >= 2:  # AI found meaningful terms
            return ' '.join(terms)
        else:  # Fallback to original query if AI extraction was minimal
            return query_text.lower()
    
    def _apply_geographic_filter(self, results: List[Dict[str, Any]], filters: ParsedFilters, request_id: str) -> List[Dict[str, Any]]:
        """Apply geographic radius filter if specified"""
        if not (filters.radius_miles and filters.center_lat and filters.center_lng):
            return results
        
        logger.debug(f"Applying geographic filter: {filters.radius_miles} miles from ({filters.center_lat}, {filters.center_lng})")
        
        with PerformanceTimer("geographic_filter", request_id) as timer:
            filtered_results = []
            for trail in results:
                distance_miles = geo_distance(
                    filters.center_lat, filters.center_lng,
                    trail['latitude'], trail['longitude']
                )
                
                if distance_miles <= filters.radius_miles:
                    trail['distance_from_center'] = distance_miles
                    filtered_results.append(trail)
            
            log_filter_application(
                request_id, "geographic", len(results), 
                len(filtered_results), f"{filters.radius_miles} miles radius"
            )
            
            logger.debug(f"Geographic filter: {len(results)} -> {len(filtered_results)} results")
            
            return filtered_results
    
    def _format_results(self, results: List[Dict[str, Any]], filters: ParsedFilters, request_id: str) -> List[Dict[str, Any]]:
        """Format results with explanations and limit to top results"""
        logger.debug(f"Formatting {len(results)} results")
        
        formatted_results = []
        for row in results:
            # Generate "why" explanation
            why_parts = self._generate_explanation(row, filters)
            
            formatted_result = {
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
                'description_snippet': truncate_description(row['description']),
                'score': row.get('rank_score', 0),
                'why': "Matches: " + ", ".join(why_parts) if why_parts else "Matches search criteria",
                
                # Enhanced location information
                'city': row.get('city'),
                'county': row.get('county'),
                'state': row.get('state'),
                'region': row.get('region'),
                'country': row.get('country'),
                
                # Amenities and access information
                'parking_available': bool(row.get('parking_available')) if row.get('parking_available') is not None else None,
                'parking_type': row.get('parking_type'),
                'restrooms': bool(row.get('restrooms')) if row.get('restrooms') is not None else None,
                'water_available': bool(row.get('water_available')) if row.get('water_available') is not None else None,
                'picnic_areas': bool(row.get('picnic_areas')) if row.get('picnic_areas') is not None else None,
                'camping_available': bool(row.get('camping_available')) if row.get('camping_available') is not None else None,
                
                # Access and permit information
                'entry_fee': bool(row.get('entry_fee')) if row.get('entry_fee') is not None else None,
                'permit_required': bool(row.get('permit_required')) if row.get('permit_required') is not None else None,
                'seasonal_access': row.get('seasonal_access'),
                'accessibility': row.get('accessibility'),
                
                # Trail characteristics
                'surface_type': row.get('surface_type'),
                'trail_markers': bool(row.get('trail_markers')) if row.get('trail_markers') is not None else None,
                'loop_trail': bool(row.get('loop_trail')) if row.get('loop_trail') is not None else None,
                
                # Contact and website
                'managing_agency': row.get('managing_agency'),
                'website_url': row.get('website_url'),
                'phone_number': row.get('phone_number')
            }
            
            # Add distance from center if available
            if 'distance_from_center' in row:
                formatted_result['distance_from_center_miles'] = row['distance_from_center']
            
            formatted_results.append(formatted_result)
        
        # Return top results
        top_results = formatted_results[:TOP_RESULTS_LIMIT]
        logger.debug(f"Returning {len(top_results)} top results")
        
        return top_results
    
    def _generate_explanation(self, trail: Dict[str, Any], filters: ParsedFilters) -> List[str]:
        """Generate explanation for why trail matches criteria"""
        why_parts = []
        
        # Always explain what the trail offers, regardless of strict filter matching
        if trail['difficulty']:
            why_parts.append(f"{trail['difficulty']} difficulty")
        
        if trail['distance_km']:
            distance_miles = km_to_miles(trail['distance_km'])
            distance_text = f"{distance_miles:.1f} miles distance"
            if filters.distance_cap_miles and distance_miles <= filters.distance_cap_miles:
                distance_text += " (within your limit)"
            elif filters.distance_cap_miles:
                distance_text += f" (over your {filters.distance_cap_miles} mile preference)"
            why_parts.append(distance_text)
        
        if trail['elevation_gain_m'] is not None:
            elevation_text = f"{trail['elevation_gain_m']}m elevation"
            if filters.elevation_cap_m and trail['elevation_gain_m'] <= filters.elevation_cap_m:
                elevation_text += " (within limit)"
            elif filters.elevation_cap_m:
                elevation_text += f" (over your {filters.elevation_cap_m}m preference)"
            why_parts.append(elevation_text)
        
        # Show matching features prominently
        matching_features = []
        trail_features = trail['features'].split(',') if trail['features'] else []
        for feature in filters.features:
            if feature in trail_features:
                matching_features.append(feature)
        
        if matching_features:
            why_parts.append(f"has {', '.join(matching_features)}")
        
        # Show other notable features even if not specifically requested
        other_features = [f for f in trail_features if f not in filters.features and f.strip()]
        if other_features and len(other_features) <= 3:  # Don't overwhelm with too many features
            why_parts.append(f"also features {', '.join(other_features[:3])}")
        
        if filters.dogs_allowed is not None:
            if bool(trail['dogs_allowed']) == filters.dogs_allowed:
                why_parts.append("dog-friendly" if filters.dogs_allowed else "no dogs required")
            else:
                dog_status = "dogs allowed" if trail['dogs_allowed'] else "no dogs"
                why_parts.append(f"{dog_status} (differs from preference)")
        
        if trail['route_type']:
            route_text = f"{trail['route_type']} trail"
            if filters.route_type and trail['route_type'] == filters.route_type:
                route_text += " (matches preference)"
            elif filters.route_type:
                route_text += f" (you preferred {filters.route_type})"
            why_parts.append(route_text)
        
        return why_parts

# Global searcher instance
trail_searcher = TrailSearcher()
