"""
Test script to verify the Flask application works correctly
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def test_home():
    """Test home page"""
    print("Testing home page...")
    response = requests.get(f"{BASE_URL}/")
    assert response.status_code == 200
    print("✓ Home page works!")

def test_stats():
    """Test statistics endpoint"""
    print("\nTesting statistics endpoint...")
    response = requests.get(f"{BASE_URL}/api/stats")
    assert response.status_code == 200
    data = response.json()
    print(f"✓ Stats loaded: {data}")

def test_podium_prediction():
    """Test podium prediction"""
    print("\nTesting podium prediction...")
    payload = {
        "grid": 1,
        "qualifying_position": 1,
        "driver_standing_pos": 1,
        "driver_points_cum": 350,
        "driver_wins_cum": 8,
        "constructor_standing_pos": 1,
        "constructor_points_cum": 600,
        "constructor_wins_cum": 12
    }
    response = requests.post(
        f"{BASE_URL}/api/predict-podium",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    assert response.status_code == 200
    data = response.json()
    print(f"✓ Podium prediction: {data}")

def test_multiclass_prediction():
    """Test multiclass prediction"""
    print("\nTesting multiclass prediction...")
    payload = {
        "grid": 5,
        "qualifying_position": 5,
        "driver_standing_pos": 5,
        "driver_points_cum": 100
    }
    response = requests.post(
        f"{BASE_URL}/api/predict-result-class",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    assert response.status_code == 200
    data = response.json()
    print(f"✓ Multiclass prediction: {data}")

def test_position_prediction():
    """Test position prediction"""
    print("\nTesting position prediction...")
    payload = {
        "grid": 10,
        "qualifying_position": 10,
        "driver_standing_pos": 8,
        "constructor_standing_pos": 5
    }
    response = requests.post(
        f"{BASE_URL}/api/predict-position",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    assert response.status_code == 200
    data = response.json()
    print(f"✓ Position prediction: {data}")

def test_clustering():
    """Test clustering endpoint"""
    print("\nTesting clustering...")
    response = requests.get(f"{BASE_URL}/api/get-clusters")
    assert response.status_code == 200
    data = response.json()
    print(f"✓ Clustering data loaded: {len(data.get('data', []))} points")

def test_race_prediction():
    """Test race prediction"""
    print("\nTesting race prediction...")
    payload = {
        "drivers": [
            {"name": "Max Verstappen", "grid": 1, "driver_points_cum": 350},
            {"name": "Lewis Hamilton", "grid": 2, "driver_points_cum": 300},
            {"name": "Charles Leclerc", "grid": 3, "driver_points_cum": 250}
        ]
    }
    response = requests.post(
        f"{BASE_URL}/api/predict-race",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    assert response.status_code == 200
    data = response.json()
    print(f"✓ Race prediction: {len(data.get('predictions', []))} drivers")

def run_all_tests():
    """Run all tests"""
    print("=" * 50)
    print("F1 ML Application Test Suite")
    print("=" * 50)
    print("\nMake sure the Flask app is running on http://localhost:5000")
    print("Run: python app.py")
    print("\nStarting tests...\n")
    
    try:
        test_home()
        test_stats()
        test_podium_prediction()
        test_multiclass_prediction()
        test_position_prediction()
        test_clustering()
        test_race_prediction()
        
        print("\n" + "=" * 50)
        print("✓ All tests passed!")
        print("=" * 50)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to Flask app")
        print("Make sure the app is running: python app.py")
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")

if __name__ == "__main__":
    run_all_tests()
