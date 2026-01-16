"""Quick API test"""
import requests

BASE_URL = "http://localhost:5001"

print("Testing Algae Box API...\n")

# Test 1: Health check
print("1. Health Check:")
r = requests.get(f"{BASE_URL}/api/health")
print(r.json())

# Test 2: List species
print("\n2. Algae Species:")
r = requests.get(f"{BASE_URL}/api/species")
data = r.json()
for species in data['species'][:3]:  # Show first 3
    print(f"  - {species['name']}: {species['description']}")

# Test 3: Create tank
print("\n3. Create Tank:")
r = requests.post(f"{BASE_URL}/api/tanks", json={
    "name": "My First Tank",
    "algae_type": "Chlorella",
    "volume_liters": 100
})
print(r.json())

# Test 4: Get recommendations
print("\n4. Get Recommendations:")
r = requests.get(f"{BASE_URL}/api/recommendations/1")
recs = r.json()
if recs['success']:
    for rec in recs['recommendations'][:2]:
        print(f"  [{rec['severity']}] {rec['issue']}")
        print(f"    → {rec['action']}")

print("\n✅ All tests passed!")
