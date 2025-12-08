# TRMNL Room Availability Display - Complete Project

## 🎯 Project Overview

This is a complete solution for displaying real-time conference room availability on TRMNL E-ink displays. It parses ICS calendar feeds (from Microsoft 365, Google Calendar, etc.) and shows:
- Current room status (AVAILABLE/OCCUPIED)
- Next booking information
- Meeting organizer and times
- Clean, professional display optimized for E-ink

## 📦 Files Included

### Core Application Files

1. **room_availability_service.py** (6.4 KB)
   - Flask web service that parses ICS feeds
   - Determines room availability status
   - Returns JSON for TRMNL to consume
   - Main application logic

2. **requirements.txt** (101 bytes)
   - Python dependencies
   - Flask, icalendar, pytz, requests, gunicorn

### TRMNL Templates

3. **trmnl_room_template_full.liquid** (5.2 KB)
   - Full-screen display template
   - Large, bold status indicators
   - Shows current and next bookings
   - Optimized for E-ink rendering

4. **trmnl_room_template_compact.liquid** (2.6 KB)
   - Smaller layout version
   - Use for half-screen or quadrant displays
   - Can combine with other TRMNL plugins

### Documentation

5. **README.md** (8.7 KB)
   - Complete setup guide
   - Deployment options (Heroku, Railway, Digital Ocean, self-hosted)
   - Troubleshooting section
   - Advanced features and customization

6. **QUICKSTART.md** (2.3 KB)
   - Get started in 10 minutes
   - Essential steps only
   - Perfect for rapid deployment

### Deployment Files

7. **Dockerfile** (602 bytes)
   - Container configuration
   - Production-ready with gunicorn
   - Health checks included

8. **docker-compose.yml** (687 bytes)
   - Quick Docker deployment
   - Includes health checks and restart policies
   - Optional nginx reverse proxy config

9. **.env.example** (392 bytes)
   - Environment configuration template
   - Timezone settings
   - Development/production options

10. **nginx.conf.example** (2.0 KB)
    - Reverse proxy configuration
    - SSL/HTTPS setup
    - Security headers
    - Rate limiting examples

11. **room-display.service.example** (1.7 KB)
    - Systemd service file
    - For traditional Linux deployments
    - Includes security hardening
    - Auto-restart on failure

### Testing

12. **test_service.py** (5.5 KB)
    - Interactive test suite
    - Validates service functionality
    - Tests ICS feed parsing
    - Checks response structure

## 🚀 Quick Start

1. **Get ICS URL** from your calendar system
2. **Deploy service** (Railway.app is easiest - just push to GitHub)
3. **Configure TRMNL**:
   - Create Private Plugin with Polling strategy
   - URL: `https://your-server.com/room-status?ics_url=YOUR_ICS&room_name=Room%201`
   - Copy liquid template to markup editor
4. **Add to playlist** and you're done!

## 💡 Use Cases

Perfect for:
- Conference room status displays
- Meeting room booking systems
- Office hotdesk availability
- Studio/equipment booking
- Any calendar-based resource management

## 🎨 Customization

Everything is customizable:
- Modify Liquid templates for different layouts
- Adjust colors and styling for your brand
- Add QR codes for quick booking
- Integrate with Teams/Zoom meeting links
- Multi-room deployments

## 📋 Requirements

**Server Side:**
- Python 3.8+
- Internet connection to fetch ICS feeds
- Minimal resources (runs on free tiers)

**Calendar:**
- Any system that exports ICS/iCal format
- Microsoft 365, Google Calendar, Apple Calendar, etc.
- Must have a public or accessible ICS URL

**Display:**
- TRMNL E-ink display device
- Active TRMNL account

## 🔒 Security Notes

- Keep ICS URLs private (they contain calendar data)
- Use HTTPS in production
- Consider authentication for your service
- Review nginx config for security headers

## 🛠️ Technology Stack

- **Backend**: Python 3 + Flask
- **Parsing**: icalendar library
- **Display**: Liquid templating (TRMNL)
- **Deployment**: Docker, gunicorn, systemd
- **Proxy**: Nginx (optional)

## 📊 Architecture

```
MS365/Google Calendar (ICS Feed)
            ↓
    [Your Flask Service]
    Parses ICS → JSON
            ↓
    [TRMNL API Polling]
    Every 5-15 minutes
            ↓
    [E-ink Display Update]
    Shows availability
```

## 🤝 Support

- Check README.md for detailed troubleshooting
- Test with test_service.py first
- TRMNL docs: docs.usetrmnl.com
- Python/Flask issues: Check application logs

## 📝 License

MIT License - Free to use and modify

## 🎉 Ready to Deploy!

All files are production-ready. Choose your deployment method:
- **Easiest**: Railway.app (auto-deploy from GitHub)
- **Flexible**: Docker Compose
- **Traditional**: Systemd service on Linux
- **Cloud**: Heroku, Digital Ocean, AWS

Start with QUICKSTART.md and you'll be up in 10 minutes!

---

Built for Family Radio
Nicholas - December 2025
