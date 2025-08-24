#!/usr/bin/env python3

import sys
sys.path.append('.')

from search import trail_searcher
from models import ParsedFilters

def test_search():
    print("=== Testing Progressive Search Relaxation ===")
    
    # Parse the problematic query
    text_parser = trail_searcher.text_parser
    filters = text_parser.parse_user_input('Easy loop under 8 km with waterfall near Chicago')
    
    print(f"Parsed filters:")
    print(f"  Difficulty: {filters.difficulty}")
    print(f"  Route type: {filters.route_type}")
    print(f"  Distance cap: {filters.distance_cap_km}")
    print(f"  Features: {filters.features}")
    print()
    
    # Check if multiple filters detected
    has_multiple = trail_searcher._has_multiple_filters(filters)
    print(f"Has multiple filters: {has_multiple}")
    
    # Test strict search
    print("\n=== Strict Search ===")
    strict_results = trail_searcher._fts5_search('Easy loop under 8 km with waterfall near Chicago', filters, 'test')
    print(f"Strict search results: {len(strict_results)}")
    
    # Test relaxed search manually
    print("\n=== Manual Relaxed Search ===")
    relaxed_filters = ParsedFilters(
        distance_cap_km=filters.distance_cap_km,
        elevation_cap_m=filters.elevation_cap_m,
        features=filters.features,
        center_lat=filters.center_lat,
        center_lng=filters.center_lng,
        radius_miles=filters.radius_miles
    )
    
    relaxed_results = trail_searcher._fts5_search('waterfall', relaxed_filters, 'test')
    print(f"Relaxed search results: {len(relaxed_results)}")
    
    if relaxed_results:
        for result in relaxed_results[:2]:
            print(f"  - {result['name']}: {result['difficulty']}, {result['route_type']}, {result['distance_miles']:.1f}mi")
    
    # Test the full search method
    print("\n=== Full Search Method ===")
    try:
        final_results = trail_searcher.search_trails('Easy loop under 8 km with waterfall near Chicago', filters, 'test')
        print(f"Final search results: {len(final_results)}")
        
        if final_results:
            for result in final_results[:2]:
                print(f"  - {result['name']}")
                print(f"    {result['difficulty']}, {result['route_type']}, {result['distance_miles']:.1f}mi")
                print(f"    Features: {result['features']}")
                print(f"    Why: {result['why']}")
                print()
    except Exception as e:
        print(f"Error in full search: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_search()
