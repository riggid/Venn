import numpy as np
import pandas as pd
from typing import List, Dict
import re
import os
from .latlong_api import LatLongAPI

# --- CONFIGURATION ---
API_KEY = os.getenv("LATLONG_API_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJUb2tlbklEIjoiMzNmMjY3MTgtMjRiOC00NTFlLWJlMGYtOGZmMzA1ZDI3ZDk5IiwiQ2xpZW50SUQiOiI2YTA3ZDNkMC01MTNkLTRjMTMtYjRjMi04NTdiY2YzNDJiNWIiLCJCdW5pdElEIjozMCwiQXBwTmFtZSI6InBlcyBoYWNrYXRob24gbWFwcy1yZWltYWdpbmVkIiwiQXBwSUQiOjE4Mzk1LCJUaW1lU3RhbXAiOiIyMDI1LTExLTI4IDE3OjEyOjUyIiwiZXhwIjoxNzY0NTIyNzcyfQ.q5AqBLmiB3KlPMt58O5N767uBJ6qNxGmt6X2aYWtrbI")

# Initialize API
latlong = LatLongAPI(API_KEY)

# 🌍 API CALL COUNTER & CACHE
api_cache: Dict[str, float] = {}
api_counter = 0
MAX_API_CALLS = 45

def get_cache_key(origin: tuple, dest: tuple) -> str:
    return f"{origin[0]:.6f}_{origin[1]:.6f}_{dest[0]:.6f}_{dest[1]:.6f}"

def parse_time_to_seconds(time_str: str) -> int:
    """Parse time strings like '25 mins' or '1 hour 15 mins' to seconds"""
    if not time_str: return 900 # Default penalty
    time_str = str(time_str).lower().replace(',', '')
    hours = re.search(r'(\d+)\s*hour', time_str)
    mins = re.search(r'(\d+)\s*(?:min|minutes?)', time_str)
    total_min = 0
    if hours: 
        total_min += int(hours.group(1)) * 60
    if mins: 
        total_min += int(mins.group(1))
    return total_min * 60

def get_travel_times(point: tuple, user_dataset: pd.DataFrame) -> np.ndarray:
    """Get travel times with caching"""
    global api_counter
    lat, lng = point
    times = []
    
    for _, row in user_dataset.iterrows():
        user_lat, user_lng = row['lat'], row['lng']
        cache_key = get_cache_key((lat, lng), (user_lat, user_lng))
        
        if cache_key in api_cache:
            times.append(api_cache[cache_key])
        else:
            api_counter += 1
            if api_counter > MAX_API_CALLS:
                print(f"⚠️ API limit reached!")
                times.append(900)
                continue
            
            # --- INTEGRATION WITH LATLONG API ---
            # Using the wrapper method instead of direct requests
            result = latlong.get_route_data((lat, lng), (user_lat, user_lng))
            
            if isinstance(result, dict) and 'time' in result:
                total_sec = parse_time_to_seconds(result['time'])
            else:
                total_sec = 900 # Penalty if route not found
            
            api_cache[cache_key] = total_sec
            times.append(total_sec)
    
    return np.array(times) / 60  # Return in minutes

def find_weighted_centroid(user_dataset: pd.DataFrame) -> tuple:
    """Find a better starting point by analyzing the user distribution"""
    lats = user_dataset['lat'].values
    lngs = user_dataset['lng'].values
    
    # Try 5 strategic starting points
    candidates = [
        (np.mean(lats), np.mean(lngs)),  # Geometric center
        (np.median(lats), np.median(lngs)),  # Median center
    ]
    
    # Add weighted centers (pull towards outliers)
    lat_range = np.max(lats) - np.min(lats)
    lng_range = np.max(lngs) - np.min(lngs)
    
    candidates.extend([
        (np.mean(lats) + 0.2 * lat_range, np.mean(lngs)),  # North bias
        (np.mean(lats) - 0.2 * lat_range, np.mean(lngs)),  # South bias
        (np.mean(lats), np.mean(lngs) + 0.2 * lng_range),  # East bias
        (np.mean(lats), np.mean(lngs) - 0.2 * lng_range),  # West bias
    ])
    
    print(f"🔍 Testing {len(candidates)} strategic starting points...")
    
    best_point = candidates[0]
    best_score = float('inf')
    
    for i, candidate in enumerate(candidates):
        times = get_travel_times(candidate, user_dataset)
        std_dev = np.std(times)
        max_time = np.max(times)
        
        # Heavily penalize std deviation and max time
        score = std_dev * 50 + max_time * 2
        
        print(f"  Point {i+1}: Std={std_dev:.1f}min, Max={max_time:.0f}min, Score={score:.0f}")
        
        if score < best_score:
            best_score = score
            best_point = candidate
    
    print(f"✅ Best starting point: ({best_point[0]:.5f}, {best_point[1]:.5f})")
    return best_point

def compute_equal_time_location(dataset: pd.DataFrame) -> dict:
    """Find optimal meeting location using intelligent search"""
    global api_cache, api_counter
    api_cache.clear()
    api_counter = 0
    
    user_locations = dataset[['lat', 'lng']].values
    n_users = len(user_locations)
    
    lats, lngs = user_locations[:, 0], user_locations[:, 1]
    
    print("🎯 INTELLIGENT EQUAL-TIME LOCATION FINDER")
    print("=" * 60)
    print(f"Users: {n_users} | Max API calls: {MAX_API_CALLS}")
    print()
    
    # PHASE 1: Find best starting point
    print("📍 PHASE 1: Finding optimal starting region")
    print("-" * 60)
    best_start = find_weighted_centroid(dataset)
    initial_calls = api_counter
    print(f"API calls used: {initial_calls}/{MAX_API_CALLS}")
    print()
    
    # PHASE 2: Dense local search around best point
    remaining = MAX_API_CALLS - api_counter - n_users  # Reserve for final
    grid_size = min(12, remaining // n_users)  # Use remaining budget
    
    candidate_spots = []  # Track all candidates for alternative suggestions
    
    if grid_size >= 9:
        print(f"📍 PHASE 2: Dense {grid_size}-point local search")
        print("-" * 60)
        
        # Create dense grid around best starting point
        if grid_size == 9:
            offsets = [(-1,-1), (-1,0), (-1,1), (0,-1), (0,0), (0,1), (1,-1), (1,0), (1,1)]
        elif grid_size == 12:
            offsets = [
                (-1,-1), (-1,0), (-1,1),
                (0,-2), (0,-1), (0,0), (0,1), (0,2),
                (1,-1), (1,0), (1,1), (2,0)
            ]
        else:
            offsets = [(0,0)]  # Fallback
        
        # Adaptive step size based on user spread
        lat_spread = np.max(lats) - np.min(lats)
        lng_spread = np.max(lngs) - np.min(lngs)
        step_lat = max(0.005, lat_spread * 0.15)  # 15% of spread, min 0.005°
        step_lng = max(0.005, lng_spread * 0.15)
        
        print(f"Search radius: {step_lat:.4f}° lat, {step_lng:.4f}° lng")
        
        best_point = best_start
        best_score = float('inf')
        best_std = float('inf')
        
        for i, (dlat, dlng) in enumerate(offsets):
            candidate = (
                best_start[0] + dlat * step_lat,
                best_start[1] + dlng * step_lng
            )
            
            times = get_travel_times(candidate, dataset)
            std_dev = np.std(times)
            max_time = np.max(times)
            min_time = np.min(times)
            avg_time = np.mean(times)
            
            # Score: minimize std dev primarily, then max time
            score = std_dev * 50 + max_time * 2
            
            # Store candidate spot
            candidate_spots.append({
                'lat': candidate[0],
                'lng': candidate[1],
                'score': score,
                'equality_score': std_dev,
                'avg_time': avg_time,
                'max_time': max_time,
                'min_time': min_time,
                'time_spread': max_time - min_time
            })
            
            print(f"  {i+1:2d}/{grid_size}: Std={std_dev:.1f}min, Range={min_time:.0f}-{max_time:.0f}min, Score={score:.0f}")
            
            if score < best_score:
                best_score = score
                best_point = candidate
                best_std = std_dev
                print(f"       ⭐ New best!")
        
        print(f"\n✅ Best point found: ({best_point[0]:.6f}, {best_point[1]:.6f})")
        print(f"   Std deviation: {best_std:.2f} minutes")
    else:
        best_point = best_start
        print(f"⚠️ Limited API budget, using best starting point")
    
    phase2_calls = api_counter - initial_calls
    print(f"API calls used: {phase2_calls}/{MAX_API_CALLS - initial_calls - n_users}")
    print()
    
    # FINAL VALIDATION
    print("🎯 FINAL VALIDATION")
    print("-" * 60)
    final_times = get_travel_times(best_point, dataset)
    
    user_times_df = pd.DataFrame({
        'user_id': dataset['user_id'],
        'lat': user_locations[:, 0],
        'lng': user_locations[:, 1],
        'travel_time_min': final_times.round(1)
    })
    
    equality_score = np.std(final_times)
    avg_time = np.mean(final_times)
    max_time = np.max(final_times)
    min_time = np.min(final_times)
    time_spread = max_time - min_time
    
    print(f"\n{'='*60}")
    print(f"✅ OPTIMIZATION COMPLETE!")
    print(f"📊 Total API calls: {api_counter}/{MAX_API_CALLS}")
    print(f"📍 Optimal meeting point: ({best_point[0]:.6f}, {best_point[1]:.6f})")
    print(f"\n⚖️  FAIRNESS METRICS:")
    print(f"   • Standard deviation: {equality_score:.2f} minutes")
    print(f"   • Time spread: {time_spread:.1f} min (range: {min_time:.0f}-{max_time:.0f})")
    print(f"   • Average time: {avg_time:.1f} minutes")
    
    # Analyze if it's geometrically impossible to do better
    pairwise_far = []
    for i in range(n_users):
        for j in range(i+1, n_users):
            dist = np.sqrt((lats[i]-lats[j])**2 + (lngs[i]-lngs[j])**2)
            pairwise_far.append(dist)
    max_spread = max(pairwise_far)
    
    if equality_score > 8:
        print(f"\n💡 INSIGHT: High inequality (>{equality_score:.1f}min) suggests users are")
        print(f"   geographically spread out (max distance: {max_spread:.3f}°).")
        print(f"   This may be the best achievable balance given the locations.")
    
    print(f"\n👥 INDIVIDUAL TRAVEL TIMES:")
    for _, row in user_times_df.iterrows():
        deviation = row['travel_time_min'] - avg_time
        symbol = "+" if deviation > 0 else ""
        print(f"   {row['user_id']:10s}: {row['travel_time_min']:5.1f} min ({symbol}{deviation:+.1f})")
    
    # Sort candidates by score to get top alternatives
    alternative_spots = sorted(candidate_spots, key=lambda x: x['score'])[:5]
    
    return {
        'equal_point': best_point,
        'travel_times_min': final_times,
        'equality_score': equality_score,
        'avg_time_min': avg_time,
        'time_spread': time_spread,
        'user_times': user_times_df,
        'n_api_calls': api_counter,
        'alternative_spots': alternative_spots
    }

if __name__ == "__main__":
    dataset = pd.DataFrame({
        'user_id': ['Priya', 'Rahul', 'Sneha', 'Vikram'],
        'lat': [12.9279, 12.9650, 13.0169, 12.9241],
        'lng': [77.6276, 77.6400, 77.6858, 77.5511]
    })
    
    print("📍 USER LOCATIONS:")
    print(dataset[['user_id', 'lat', 'lng']].to_string(index=False))
    
    # Show geographic spread
    lat_spread = max(dataset['lat']) - min(dataset['lat'])
    lng_spread = max(dataset['lng']) - min(dataset['lng'])
    print(f"\n📏 Geographic spread: {lat_spread:.4f}° lat × {lng_spread:.4f}° lng")
    print(f"   (~{lat_spread*111:.1f}km × {lng_spread*111*np.cos(np.radians(12.97)):.1f}km)")
    print()
    
    result = compute_equal_time_location(dataset)