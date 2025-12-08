#!/usr/bin/env python3
"""
Test script for Room Availability Service
Run this to verify your service is working correctly
"""

import requests
import json
import sys
from urllib.parse import quote

def test_health(base_url):
    """Test the health endpoint"""
    print("\n=== Testing Health Endpoint ===")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_room_status(base_url, ics_url, room_name="Test Room"):
    """Test the room status endpoint"""
    print("\n=== Testing Room Status Endpoint ===")
    print(f"ICS URL: {ics_url}")
    print(f"Room Name: {room_name}")
    
    try:
        # URL encode the parameters
        encoded_ics = quote(ics_url, safe='')
        encoded_room = quote(room_name, safe='')
        
        url = f"{base_url}/room-status?ics_url={encoded_ics}&room_name={encoded_room}"
        print(f"\nRequest URL: {url}\n")
        
        response = requests.get(url, timeout=15)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ Success! Response:\n")
            print(json.dumps(data, indent=2))
            
            # Validate response structure
            print("\n=== Validating Response Structure ===")
            required_fields = ['room_name', 'status', 'current_time', 'current_date']
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                print(f"⚠️  Warning: Missing fields: {', '.join(missing_fields)}")
            else:
                print("✅ All required fields present")
            
            # Check status
            print(f"\nRoom Status: {data.get('status')}")
            if data.get('status') == 'AVAILABLE':
                print(f"Available Until: {data.get('available_until', 'N/A')}")
                if data.get('next_booking'):
                    print(f"Next Booking: {data['next_booking'].get('title')}")
                    print(f"  Start: {data['next_booking'].get('start_time')}")
            elif data.get('status') == 'OCCUPIED':
                if data.get('current_booking'):
                    print(f"Current Meeting: {data['current_booking'].get('title')}")
                    print(f"  Until: {data['current_booking'].get('end_time')}")
            
            return True
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_invalid_request(base_url):
    """Test error handling"""
    print("\n=== Testing Error Handling ===")
    try:
        response = requests.get(f"{base_url}/room-status", timeout=5)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 400:
            print("✅ Correctly returns 400 for missing parameters")
            return True
        else:
            print(f"⚠️  Expected 400, got {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("=" * 60)
    print("Room Availability Service Test Suite")
    print("=" * 60)
    
    # Configuration
    base_url = input("\nEnter service URL (default: http://localhost:5000): ").strip()
    if not base_url:
        base_url = "http://localhost:5000"
    
    print(f"\nUsing base URL: {base_url}")
    
    # Test health endpoint
    health_ok = test_health(base_url)
    
    if not health_ok:
        print("\n❌ Health check failed. Is the service running?")
        sys.exit(1)
    
    # Test error handling
    test_invalid_request(base_url)
    
    # Test with real ICS URL
    print("\n" + "=" * 60)
    ics_url = input("\nEnter ICS calendar URL to test: ").strip()
    
    if not ics_url:
        print("\n⚠️  No ICS URL provided. Skipping room status test.")
        print("To test the full functionality, run again with an ICS URL.")
        sys.exit(0)
    
    room_name = input("Enter room name (default: Test Room): ").strip()
    if not room_name:
        room_name = "Test Room"
    
    # Test room status
    status_ok = test_room_status(base_url, ics_url, room_name)
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"Health Check: {'✅ PASS' if health_ok else '❌ FAIL'}")
    print(f"Room Status:  {'✅ PASS' if status_ok else '❌ FAIL'}")
    
    if health_ok and status_ok:
        print("\n🎉 All tests passed! Your service is ready to use.")
        print("\nNext steps:")
        print("1. Deploy your service to production")
        print("2. Configure TRMNL Private Plugin with polling URL:")
        print(f"   {base_url}/room-status?ics_url=YOUR_ICS_URL&room_name=YOUR_ROOM_NAME")
        print("3. Copy the Liquid template to TRMNL markup editor")
        print("4. Add to your TRMNL playlist")
    else:
        print("\n⚠️  Some tests failed. Please review the output above.")
    
    print("\n" + "=" * 60)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user.")
        sys.exit(0)
