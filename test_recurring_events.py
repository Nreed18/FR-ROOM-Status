import unittest
from datetime import datetime, date
from icalendar import Calendar

from room_availability_service import parse_events_with_recurrence, TIMEZONE


SIMPLE_RECURRING_ICS = b"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Test Calendar//EN
BEGIN:VEVENT
UID:test-event@example.com
DTSTAMP:20241201T200000Z
SUMMARY:Recurring Test Event
DTSTART;TZID=America/Chicago:20241201T141500
DTEND;TZID=America/Chicago:20241201T151500
RRULE:FREQ=DAILY;COUNT=3
END:VEVENT
END:VCALENDAR
"""


RRULE_WITH_UTC_UNTIL = b"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Test Calendar//EN
BEGIN:VEVENT
UID:utc-until-event@example.com
DTSTAMP:20251201T200000Z
SUMMARY:UTC Until Recurrence
DTSTART;TZID=America/Chicago:20251028T141500
DTEND;TZID=America/Chicago:20251028T150000
RRULE:FREQ=WEEKLY;UNTIL=20251223T201500Z;INTERVAL=2;BYDAY=TU;WKST=SU
END:VEVENT
END:VCALENDAR
"""


class RecurringEventParsingTests(unittest.TestCase):
    def test_events_respect_local_date_boundaries(self):
        """Recurring events should not shift to the previous day when expanded."""
        cal = Calendar.from_ical(SIMPLE_RECURRING_ICS)
        # Second occurrence: 2024-12-02 at 2:15 PM America/Chicago
        now = TIMEZONE.localize(datetime(2024, 12, 2, 10, 0, 0))

        events = parse_events_with_recurrence(cal, now, start_date=date(2024, 12, 2), end_date=date(2024, 12, 2))

        self.assertEqual(len(events), 1)
        event = events[0]
        self.assertEqual(event["summary"], "Recurring Test Event")
        self.assertEqual(event["start"].astimezone(TIMEZONE), TIMEZONE.localize(datetime(2024, 12, 2, 14, 15)))
        self.assertEqual(event["end"].astimezone(TIMEZONE), TIMEZONE.localize(datetime(2024, 12, 2, 15, 15)))

    def test_rrule_until_in_utc_still_expands(self):
        """RRULE UNTIL values in UTC should still expand for local dates."""
        cal = Calendar.from_ical(RRULE_WITH_UTC_UNTIL)
        now = TIMEZONE.localize(datetime(2025, 12, 9, 10, 0, 0))

        events = parse_events_with_recurrence(cal, now, start_date=date(2025, 12, 9), end_date=date(2025, 12, 9))

        self.assertEqual(len(events), 1)
        event = events[0]
        self.assertEqual(event["summary"], "UTC Until Recurrence")
        self.assertEqual(event["start"], TIMEZONE.localize(datetime(2025, 12, 9, 14, 15)))
        self.assertEqual(event["end"], TIMEZONE.localize(datetime(2025, 12, 9, 15, 0)))


if __name__ == "__main__":
    unittest.main()
