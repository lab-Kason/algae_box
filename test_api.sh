#!/bin/bash
# Algae Box API Test Script

echo "=== Testing Algae Box API ==="
echo ""

echo "1. Health Check:"
curl -s http://localhost:5001/api/health | python3 -m json.tool
echo ""

echo "2. List Algae Species:"
curl -s http://localhost:5001/api/species | python3 -m json.tool
echo ""

echo "3. List Tanks:"
curl -s http://localhost:5001/api/tanks | python3 -m json.tool
echo ""

echo "4. Create New Tank:"
curl -s -X POST http://localhost:5001/api/tanks \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Tank 1",
    "algae_type": "Chlorella",
    "volume_liters": 50,
    "notes": "Test tank for Chlorella cultivation"
  }' | python3 -m json.tool
echo ""

echo "5. Get Tank Details (Tank ID 1):"
curl -s http://localhost:5001/api/tanks/1 | python3 -m json.tool
echo ""

echo "6. Get Recommendations (Tank ID 1):"
curl -s http://localhost:5001/api/recommendations/1 | python3 -m json.tool
echo ""

echo "=== All tests complete ==="
