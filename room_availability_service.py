#!/usr/bin/env python3
"""
Room Availability Service for TRMNL E-ink Display
Parses ICS calendar feeds and returns current room status
Now with support for recurring events (RRULE)!
"""

from flask import Flask, jsonify, request
from icalendar import Calendar
from icalendar.prop import vRecur
from datetime import datetime, timedelta, date
import pytz
import requests
from typing import List, Dict, Optional
import recurring_ical_events
import os
from dateutil.rrule import rruleset, rrulestr

app = Flask(__name__)

# Configuration - can be overridden by environment variable
TIMEZONE_STR = os.environ.get('TIMEZONE', 'America/Chicago')
TIMEZONE = pytz.timezone(TIMEZONE_STR)
USE_PROXY_FOR_ICS = os.environ.get('USE_PROXY_FOR_ICS', 'true').lower() not in ('false', '0', 'no')


def fetch_ics_feed(ics_url: str) -> Calendar:
    """Fetch and parse ICS calendar from URL"""
    try:
        if USE_PROXY_FOR_ICS:
            response = requests.get(ics_url, timeout=10)
        else:
            session = requests.Session()
            session.trust_env = False  # Ignore http/https proxy env vars that can block the feed
            response = session.get(ics_url, timeout=10)
        response.raise_for_status()
        cal = Calendar.from_ical(response.content)
        return cal
    except Exception as e:
        raise Exception(f"Failed to fetch ICS feed: {str(e)}")


def parse_events_with_recurrence(
    cal: Calendar, now: datetime, start_date: Optional[date] = None, end_date: Optional[date] = None
) -> List[Dict]:
    """
    Parse calendar events including recurring events
    Uses recurring-ical-events to expand RRULE entries

    start_date/end_date allow callers (e.g., /debug) to inspect a wider range of days
    instead of just the current date. Dates are inclusive.
    """
    events = []

    # Compute the date range in local timezone
    start_date = start_date or now.date()
    end_date = end_date or start_date
    range_start = TIMEZONE.localize(datetime.combine(start_date, datetime.min.time()))
    range_end = TIMEZONE.localize(datetime.combine(end_date, datetime.max.time()))

    def _normalize_dt(dt_value: object, default_end: bool = False) -> datetime:
        """Convert ical date/datetime to timezone-aware datetime in the service timezone."""
        if isinstance(dt_value, datetime):
            if dt_value.tzinfo is None:
                return TIMEZONE.localize(dt_value)
            return dt_value.astimezone(TIMEZONE)
        if isinstance(dt_value, date):
            base_dt = datetime.combine(dt_value, datetime.max.time() if default_end else datetime.min.time())
            return TIMEZONE.localize(base_dt)
        raise ValueError("Unsupported date value")

    # Build a lookup for exception overrides (RECURRENCE-ID components)
    overrides: Dict[str, Dict[datetime, object]] = {}
    for component in cal.walk('VEVENT'):
        recurrence_id = component.get('RECURRENCE-ID')
        if recurrence_id:
            uid = str(component.get('UID'))
            rec_dt = _normalize_dt(recurrence_id.dt)
            overrides.setdefault(uid, {})[rec_dt] = component

    def _add_event(component, start_dt: datetime, end_dt: datetime):
        if start_dt <= range_end and end_dt >= range_start:
            events.append({
                'summary': str(component.get('SUMMARY', 'Booking')),
                'start': start_dt,
                'end': end_dt,
                'organizer': str(component.get('ORGANIZER', '')).replace('mailto:', '')
            })

    try:
        for component in cal.walk('VEVENT'):
            if component.get('RECURRENCE-ID'):
                # Handled via overrides when processing the master event
                continue

            start = component.get('DTSTART')
            end = component.get('DTEND')
            if not start or not end:
                continue

            start_dt = _normalize_dt(start.dt)
            end_dt = _normalize_dt(end.dt, default_end=True)
            duration = end_dt - start_dt

            rrule = component.get('RRULE')
            if not rrule:
                _add_event(component, start_dt, end_dt)
                continue

            # Expand recurring instances using dateutil to better handle UNTIL rules in UTC
            rule_params = dict(component.decoded('RRULE'))
            rrule_tz = start_dt.tzinfo or TIMEZONE
            start_for_rrule = start_dt

            # Convert timezone-aware start/UNTIL values to naive datetimes so dateutil keeps wall times across DST
            if start_dt.tzinfo:
                start_for_rrule = start_dt.replace(tzinfo=None)
                if 'UNTIL' in rule_params and rule_params['UNTIL']:
                    until_dt = rule_params['UNTIL'][0]
                    if isinstance(until_dt, datetime):
                        rule_params['UNTIL'] = [until_dt.astimezone(rrule_tz).replace(tzinfo=None)]
            rule_str = vRecur(rule_params).to_ical().decode()
            rrule_set = rruleset()
            rrule_set.rrule(rrulestr(rule_str, dtstart=start_for_rrule))

            # Apply exclusions
            exdates = component.get('EXDATE') or []
            if not isinstance(exdates, list):
                exdates = [exdates]
            for ex in exdates:
                for ex_dt in ex.dts:
                    exdate_dt = _normalize_dt(ex_dt.dt)
                    if start_dt.tzinfo:
                        exdate_dt = exdate_dt.replace(tzinfo=None)
                    rrule_set.exdate(exdate_dt)

            # Apply explicit additional dates
            rdates = component.get('RDATE') or []
            if not isinstance(rdates, list):
                rdates = [rdates]
            for rdate in rdates:
                for add_dt in rdate.dts:
                    rdate_dt = _normalize_dt(add_dt.dt)
                    if start_dt.tzinfo:
                        rdate_dt = rdate_dt.replace(tzinfo=None)
                    rrule_set.rdate(rdate_dt)

            uid = str(component.get('UID'))
            override_map = overrides.get(uid, {})

            query_start = range_start
            query_end = range_end
            if start_dt.tzinfo:
                query_start = range_start.astimezone(rrule_tz).replace(tzinfo=None)
                query_end = range_end.astimezone(rrule_tz).replace(tzinfo=None)

            for occurrence in rrule_set.between(query_start, query_end, inc=True):
                # Use overrides when present
                occurrence_key = occurrence
                if start_dt.tzinfo:
                    occurrence_key = rrule_tz.localize(occurrence)
                override_component = override_map.get(occurrence_key)
                if override_component:
                    if str(override_component.get('STATUS', '')).upper() == 'CANCELLED':
                        continue
                    occ_start = _normalize_dt(override_component.get('DTSTART').dt)
                    occ_end = _normalize_dt(override_component.get('DTEND').dt, default_end=True)
                    _add_event(override_component, occ_start, occ_end)
                else:
                    occ_start = occurrence if not start_dt.tzinfo else rrule_tz.localize(occurrence)
                    occ_start = occ_start.astimezone(TIMEZONE)
                    occ_end = occ_start + duration
                    _add_event(component, occ_start, occ_end)
    except Exception as e:
        app.logger.error(f"Error expanding recurring events: {str(e)}")
        return parse_events_fallback(cal, now, start_date=start_date, end_date=end_date)

    # Sort by start time
    events.sort(key=lambda x: x['start'])

    app.logger.info(f"Found {len(events)} events for today")
    for event in events:
        app.logger.info(f"  - {event['summary']}: {event['start'].strftime('%I:%M %p')} - {event['end'].strftime('%I:%M %p')}")

    return events


def parse_events_fallback(
    cal: Calendar, now: datetime, start_date: Optional[date] = None, end_date: Optional[date] = None
) -> List[Dict]:
    """
    Fallback parser without recurring event support
    Used if recurring-ical-events fails
    """
    events = []
    start_date = start_date or now.date()
    end_date = end_date or start_date
    date_range_start = TIMEZONE.localize(datetime.combine(start_date, datetime.min.time()))
    date_range_end = TIMEZONE.localize(datetime.combine(end_date, datetime.max.time()))

    for component in cal.walk('VEVENT'):
        try:
            # Skip recurring events (they won't work in fallback mode)
            if component.get('RRULE'):
                continue
                
            summary = str(component.get('SUMMARY', 'Booking'))
            start = component.get('DTSTART').dt
            end = component.get('DTEND').dt
            
            if isinstance(start, date) and not isinstance(start, datetime):
                start = datetime.combine(start, datetime.min.time())
                start = TIMEZONE.localize(start)
            if isinstance(end, date) and not isinstance(end, datetime):
                end = datetime.combine(end, datetime.max.time())
                end = TIMEZONE.localize(end)
            
            if start.tzinfo is None:
                start = TIMEZONE.localize(start)
            if end.tzinfo is None:
                end = TIMEZONE.localize(end)
            
            start = start.astimezone(TIMEZONE)
            end = end.astimezone(TIMEZONE)
            
            if start <= date_range_end and end >= date_range_start:
                events.append({
                    'summary': summary,
                    'start': start,
                    'end': end,
                    'organizer': str(component.get('ORGANIZER', '')).replace('mailto:', '')
                })
        except Exception as e:
            continue
    
    events.sort(key=lambda x: x['start'])
    return events


def determine_room_status(events: List[Dict], now: datetime) -> Dict:
    """Determine current room status and next booking"""
    
    # Find current event - check if we're within the meeting time
    current_event = None
    for event in events:
        # Meeting is current if now is between start and end
        # Use a small buffer (1 minute) for clock skew
        start_buffer = event['start'] - timedelta(minutes=1)
        if start_buffer <= now < event['end']:
            current_event = event
            break
    
    # Find next event
    next_event = None
    for event in events:
        if event['start'] > now:
            next_event = event
            break
    
    # Determine status
    if current_event:
        # Room is currently occupied
        minutes_until_free = int((current_event['end'] - now).total_seconds() / 60)
        return {
            'status': 'OCCUPIED',
            'status_text': 'OCCUPIED',
            'available_until': None,
            'minutes_available': None,
            'current_booking': {
                'title': current_event['summary'],
                'start_time': current_event['start'].strftime('%-I:%M %p'),
                'end_time': current_event['end'].strftime('%-I:%M %p'),
                'organizer': current_event['organizer']
            },
            'next_booking': {
                'title': next_event['summary'],
                'start_time': next_event['start'].strftime('%-I:%M %p'),
                'end_time': next_event['end'].strftime('%-I:%M %p'),
                'organizer': next_event['organizer']
            } if next_event else None
        }
    elif next_event:
        # Room is available until next meeting
        minutes_until_next = int((next_event['start'] - now).total_seconds() / 60)
        return {
            'status': 'AVAILABLE',
            'status_text': 'AVAILABLE',
            'available_until': next_event['start'].strftime('%-I:%M %p'),
            'minutes_available': minutes_until_next,
            'current_booking': None,
            'next_booking': {
                'title': next_event['summary'],
                'start_time': next_event['start'].strftime('%-I:%M %p'),
                'end_time': next_event['end'].strftime('%-I:%M %p'),
                'organizer': next_event['organizer']
            }
        }
    else:
        # Room is available for rest of day
        return {
            'status': 'AVAILABLE',
            'status_text': 'AVAILABLE',
            'available_until': 'End of Day',
            'minutes_available': None,
            'current_booking': None,
            'next_booking': None
        }


@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'timezone': str(TIMEZONE),
        'timestamp': datetime.now(TIMEZONE).isoformat()
    })


@app.route('/debug')
def debug():
    """Debug endpoint to see parsed events"""
    ics_url = request.args.get('ics_url')
    if not ics_url:
        return jsonify({'error': 'ics_url parameter required'}), 400

    try:
        now = datetime.now(TIMEZONE)
        days = request.args.get('days', default='1')
        try:
            days_int = max(1, min(int(days), 30))  # Clamp between 1 and 30 days
        except ValueError:
            return jsonify({'error': 'days must be an integer'}), 400

        start_date = now.date()
        end_date = start_date + timedelta(days=days_int - 1)

        cal = fetch_ics_feed(ics_url)
        events = parse_events_with_recurrence(cal, now, start_date=start_date, end_date=end_date)

        debug_info = {
            'current_time': now.isoformat(),
            'current_time_display': now.strftime('%-I:%M %p'),
            'timezone': str(TIMEZONE),
            'range_start': start_date.isoformat(),
            'range_end': end_date.isoformat(),
            'events': []
        }

        for event in events[:20]:  # Show first 20 events in range
            debug_info['events'].append({
                'summary': event['summary'],
                'start_iso': event['start'].isoformat(),
                'start_display': event['start'].strftime('%Y-%m-%d %-I:%M %p'),
                'end_iso': event['end'].isoformat(),
                'end_display': event['end'].strftime('%Y-%m-%d %-I:%M %p'),
                'is_current': event['start'] <= now < event['end'],
                'is_future': event['start'] > now,
                'minutes_until': int((event['start'] - now).total_seconds() / 60)
            })

        return jsonify(debug_info)
    except Exception as e:
        app.logger.error(f"Debug error: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500


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
        events = parse_events_with_recurrence(cal, now)
        
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
        app.logger.error(f"Error: {str(e)}", exc_info=True)
        return jsonify({
            'error': str(e),
            'room_name': room_name,
            'status': 'ERROR',
            'current_time': datetime.now(TIMEZONE).strftime('%-I:%M %p')
        }), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
