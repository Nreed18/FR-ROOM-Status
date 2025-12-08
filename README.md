# Room Availability Display for TRMNL E-ink

This system displays real-time conference room availability on TRMNL E-ink displays by parsing ICS calendar feeds from Microsoft 365, Google Calendar, or any other calendar system that provides ICS export.

## Architecture Overview

```
ICS Calendar Feed (Microsoft 365/Google)
           ↓
Python Flask Middleware Service
(Parses ICS, determines status)
           ↓
JSON API Response
           ↓
TRMNL Device (polls every N minutes)
           ↓
E-ink Display
```

## Files Included

1. **room_availability_service.py** - Flask service that fetches and parses ICS feeds
2. **trmnl_room_template_full.liquid** - Full-screen TRMNL template
3. **trmnl_room_template_compact.liquid** - Compact template for smaller layouts
4. **requirements.txt** - Python dependencies

## Setup Instructions

### Step 1: Get Your ICS Calendar URL

#### For Microsoft 365 (Outlook):
1. Open Outlook on the web
2. Go to Calendar
3. Right-click on the room/resource calendar
4. Select "Settings" or "Sharing and permissions"
5. Look for "Publish this calendar" or "ICS"
6. Copy the ICS/iCal URL

#### For Google Calendar:
1. Go to Google Calendar settings
2. Select the calendar
3. Scroll to "Integrate calendar"
4. Copy the "Secret address in iCal format"

### Step 2: Deploy the Middleware Service

You need to host the Python service somewhere that TRMNL can reach. Here are several options:

#### Option A: Deploy to Heroku (Recommended for beginners)

```bash
# Install Heroku CLI, then:
heroku login
heroku create your-room-display
git init
git add .
git commit -m "Initial commit"
git push heroku main
```

Create a `Procfile`:
```
web: gunicorn room_availability_service:app
```

#### Option B: Deploy to Railway.app

1. Sign up at railway.app
2. Click "New Project" → "Deploy from GitHub"
3. Connect your repository
4. Railway will auto-detect Flask and deploy
5. Add these environment variables:
   - `TIMEZONE` (optional, defaults to America/Chicago)

#### Option C: Self-Host on Your Server

```bash
# On your server (Ubuntu/Debian):
sudo apt update
sudo apt install python3 python3-pip

# Install dependencies
pip3 install -r requirements.txt

# Run with gunicorn
gunicorn -b 0.0.0.0:5000 room_availability_service:app

# Or use systemd for production (see below)
```

#### Option D: Run on Digital Ocean App Platform

1. Create new app
2. Link to your GitHub repository
3. Digital Ocean auto-detects Flask
4. Deploy!

### Step 3: Create Systemd Service (for self-hosting)

Create `/etc/systemd/system/room-display.service`:

```ini
[Unit]
Description=Room Availability Service
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/room-display
Environment="PATH=/opt/room-display/venv/bin"
ExecStart=/opt/room-display/venv/bin/gunicorn -b 0.0.0.0:5000 room_availability_service:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable room-display
sudo systemctl start room-display
sudo systemctl status room-display
```

### Step 4: Test Your Service

Test the endpoint:
```bash
curl "http://your-server:5000/room-status?ics_url=YOUR_ICS_URL&room_name=Conference%20Room%201"
```

You should get JSON like:
```json
{
  "room_name": "Conference Room 1",
  "current_time": "2:45 PM",
  "current_date": "Wednesday, June 4, 2025",
  "status": "AVAILABLE",
  "available_until": "3:00 PM",
  "next_booking": {
    "title": "Team Meeting",
    "start_time": "3:00 PM",
    "end_time": "4:00 PM"
  }
}
```

### Step 5: Configure TRMNL Private Plugin

1. Log into your TRMNL account at usetrmnl.com
2. Navigate to **Plugins → Private Plugin**
3. Click **"Create Private Plugin"**
4. Configure:

**Plugin Settings:**
- **Name**: Room Availability - [Room Name]
- **Strategy**: Select **"Polling"**

**Polling URL:**
```
https://your-server.com/room-status?ics_url=YOUR_ICS_URL&room_name=Conference%20Room%201
```

Replace:
- `your-server.com` with your deployed service URL
- `YOUR_ICS_URL` with your URL-encoded ICS feed URL
- `Conference%20Room%201` with your room name (URL encoded)

**Form Fields (Optional):**
If you want to make it configurable without editing the URL:

```yaml
- keyname: ics_url
  label: Calendar ICS URL
  type: text
  required: true
- keyname: room_name
  label: Room Name
  type: text
  default: Conference Room
```

Then use this Polling URL:
```
https://your-server.com/room-status?ics_url={{ ics_url }}&room_name={{ room_name }}
```

5. **Edit Markup**: Copy and paste the contents of either:
   - `trmnl_room_template_full.liquid` (for full-screen display)
   - `trmnl_room_template_compact.liquid` (for smaller layouts)

6. **Refresh Interval**: Set to 5-15 minutes depending on your needs

7. Click **"Force Refresh"** to test

### Step 6: Add to Your TRMNL Playlist

1. Go to **Playlists**
2. Add your new "Room Availability" plugin
3. Set display duration and order
4. Save!

## Configuration Options

### Timezone

Edit the `TIMEZONE` setting in `room_availability_service.py`:

```python
TIMEZONE = pytz.timezone('America/Chicago')  # Your timezone
```

Common timezones:
- `America/New_York` - Eastern
- `America/Chicago` - Central
- `America/Denver` - Mountain
- `America/Los_Angeles` - Pacific
- `Europe/London` - UK
- `Europe/Paris` - Central Europe

### Customizing the Display

The Liquid templates are fully customizable. Key variables available:

```liquid
{{ IDX_0.room_name }}              - Room name
{{ IDX_0.current_time }}           - Current time (2:45 PM)
{{ IDX_0.current_date }}           - Current date
{{ IDX_0.status }}                 - AVAILABLE/OCCUPIED/ERROR
{{ IDX_0.available_until }}        - Time (3:00 PM)
{{ IDX_0.next_booking.title }}     - Next meeting title
{{ IDX_0.next_booking.start_time }} - Start time
{{ IDX_0.next_booking.end_time }}   - End time
{{ IDX_0.current_booking.* }}      - Same fields for current booking
```

### Multiple Rooms

To display multiple rooms, create separate Private Plugin instances for each room with different ICS URLs and room names.

## Troubleshooting

### Service returns error "Failed to fetch ICS feed"
- Check that the ICS URL is accessible from your server
- Verify the URL hasn't expired (some calendar systems rotate URLs)
- Check firewall rules

### Display shows "ERROR" status
- Check the service logs: `journalctl -u room-display -f`
- Test the endpoint directly with curl
- Verify the ICS URL is correct

### Times are wrong
- Check the `TIMEZONE` setting in the Python service
- Verify your ICS feed includes timezone information

### Display not updating
- Check TRMNL playlist refresh interval
- Force refresh from plugin settings
- Check that the TRMNL device is online

### "No more bookings today" showing incorrectly
- Verify calendar events have proper start/end times
- Check that events aren't marked as "all-day"
- Inspect the raw ICS feed

## Advanced Features

### Adding a QR Code for Quick Booking

Add to your Liquid template:

```liquid
<div style="position: absolute; top: 20px; right: 20px;">
  <img src="https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={{ IDX_0.booking_url }}" 
       style="width: 150px; height: 150px;" />
  <div style="font-size: 14px; text-align: center; margin-top: 5px;">
    Scan to Book
  </div>
</div>
```

Update your Python service to return `booking_url`.

### Email Notifications

Add webhook support to notify when rooms become available or when meetings are about to end.

### Integration with MS Teams/Zoom

Parse the calendar event descriptions to extract meeting links and display them.

## Security Considerations

1. **URL Protection**: Consider using authentication on your middleware service
2. **Rate Limiting**: Implement rate limiting on your Flask service
3. **HTTPS**: Always use HTTPS in production
4. **ICS URL Security**: Keep your ICS URLs private (they contain calendar data)

## Performance

- The service caches nothing by default (stateless)
- Each TRMNL request fetches fresh calendar data
- Consider adding caching for high-traffic scenarios:

```python
from flask_caching import Cache

cache = Cache(app, config={'CACHE_TYPE': 'simple', 'CACHE_DEFAULT_TIMEOUT': 300})

@cache.cached(timeout=300)  # Cache for 5 minutes
def fetch_ics_feed(ics_url):
    # ... existing code
```

## Support

For issues specific to:
- TRMNL: Check their docs at docs.usetrmnl.com or Discord
- Calendar integration: Verify ICS export settings
- Python service: Check application logs

## License

MIT License - Feel free to modify and adapt for your needs.

---

Built for Family Radio by Nicholas
