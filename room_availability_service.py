#!/usr/bin/env python3
"""
Room Availability Service for TRMNL E-ink Display
Parses ICS calendar feeds and returns current room status
"""

from flask import Flask, jsonify, request
from icalendar import Calendar
from datetime import datetime, timedelta
import pytz
import requests
from typing import List, Dict, Optional

app = Flask(__name__)

# Configuration - set your timezone
TIMEZONE = pytz.timezone('America/Chicago')  # Adjust for your location


def fetch_ics_feed(ics_url: str) -> Calendar:
    """Fetch and parse ICS calendar from URL"""
    try:
        response = requests.get(ics_url, timeout=10)
        response.raise_for_status()
        cal = Calendar.from_ical(response.content)
        return cal
    except Exception as e:
        raise Exception(f"Failed to fetch ICS feed: {str(e)}")


def parse_events(cal: Calendar, now: datetime) -> List[Dict]:
    """Parse calendar events and return relevant booking information"""
    events = []
    
    for component in cal.walk('VEVENT'):
        try:
            # Get event details
            summary = str(component.get('SUMMARY', 'Booking'))
            start = component.get('DTSTART').dt
            end = component.get('DTEND').dt
            
            # Convert to datetime if date only
            if not isinstance(start, datetime):
                start = datetime.combine(start, datetime.min.time())
                start = TIMEZONE.localize(start)
            if not isinstance(end, datetime):
                end = datetime.combine(end, datetime.max.time())
                end = TIMEZONE.localize(end)
            
            # Ensure timezone aware
            if start.tzinfo is None:
                start = TIMEZONE.localize(start)
            if end.tzinfo is None:
                end = TIMEZONE.localize(end)
            
            # Convert to local timezone
            start = start.astimezone(TIMEZONE)
            end = end.astimezone(TIMEZONE)
            
            # Only include events from today and future
            if end >= now:
                events.append({
                    'summary': summary,
                    'start': start,
                    'end': end,
                    'organizer': str(component.get('ORGANIZER', '')).replace('mailto:', '')
                })
        except Exception as e:
            # Skip problematic events
            continue
    
    # Sort by start time
    events.sort(key=lambda x: x['start'])
    return events


def determine_room_status(events: List[Dict], now: datetime) -> Dict:
    """Determine current room status and next booking"""
    
    # Find current event
    current_event = None
    for event in events:
        if event['start'] <= now <= event['end']:
            current_event = event
            break
    
    # Find next event
    next_event = None
    for event in events:
        if event['start'] > now:
            next_event = event
            break
    
    if current_event:
        # Room is occupied
        return {
            'status': 'OCCUPIED',
            'status_text': 'OCCUPIED',
            'current_booking': {
                'title': current_event['summary'],
                'organizer': current_event['organizer'],
                'start_time': current_event['start'].strftime('%-I:%M %p'),
                'end_time': current_event['end'].strftime('%-I:%M %p'),
                'minutes_remaining': int((current_event['end'] - now).total_seconds() / 60)
            },
            'available_until': None,
            'next_booking': next_event
        }
    elif next_event:
        # Room is available until next booking
        minutes_until = int((next_event['start'] - now).total_seconds() / 60)
        
        return {
            'status': 'AVAILABLE',
            'status_text': f"AVAILABLE",
            'available_until': next_event['start'].strftime('%-I:%M %p'),
            'minutes_available': minutes_until,
            'current_booking': None,
            'next_booking': {
                'title': next_event['summary'],
                'organizer': next_event['organizer'],
                'start_time': next_event['start'].strftime('%-I:%M %p'),
                'end_time': next_event['end'].strftime('%-I:%M %p')
            }
        }
    else:
        # No more bookings today
        return {
            'status': 'AVAILABLE',
            'status_text': 'AVAILABLE',
            'available_until': 'End of Day',
            'minutes_available': None,
            'current_booking': None,
            'next_booking': None
        }


@app.route('/room-status')
def room_status():
    """
    Main endpoint that TRMNL will poll
    Expected parameters:
    - ics_url: URL to the ICS calendar feed
    - room_name: Optional room name to display
    """
    
    ics_url = request.args.get('ics_url')
    room_name = request.args.get('room_name', 'Conference Room')
    
    if not ics_url:
        return jsonify({'error': 'ics_url parameter required'}), 400
    
    try:
        # Get current time in configured timezone
        now = datetime.now(TIMEZONE)
        
        # Fetch and parse calendar
        cal = fetch_ics_feed(ics_url)
        events = parse_events(cal, now)
        
        # Determine room status
        status = determine_room_status(events, now)
        
        # Build response for TRMNL
        response = {
            'room_name': room_name,
            'current_time': now.strftime('%-I:%M %p'),
            'current_date': now.strftime('%A, %B %-d, %Y'),
            'status': status['status'],
            'status_text': status['status_text'],
            'available_until': status['available_until'],
            'minutes_available': status['minutes_available'],
            'current_booking': status['current_booking'],
            'next_booking': status['next_booking'],
            'last_updated': now.isoformat()
        }
        
        return jsonify(response)
    
    except Exception as e:
        return jsonify({
            'error': str(e),
            'room_name': room_name,
            'status': 'ERROR',
            'current_time': datetime.now(TIMEZONE).strftime('%-I:%M %p')
        }), 500


@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'timestamp': datetime.now(TIMEZONE).isoformat()})


if __name__ == '__main__':
    # For development
    app.run(host='0.0.0.0', port=5000, debug=True)
