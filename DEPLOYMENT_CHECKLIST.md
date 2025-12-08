# Deployment Checklist

Use this checklist to ensure your room availability display is properly configured.

## ✅ Pre-Deployment

### Calendar Setup
- [ ] Obtained ICS/iCal URL from calendar system
- [ ] Verified ICS URL is publicly accessible
- [ ] Tested ICS URL loads calendar data (paste in browser)
- [ ] Room/resource calendar has proper timezone set
- [ ] Calendar events have start and end times (not all-day)

### Service Configuration
- [ ] Edited TIMEZONE in room_availability_service.py
- [ ] Tested timezone matches your location
- [ ] Reviewed requirements.txt dependencies
- [ ] Decided on deployment method (Railway/Docker/Systemd)

### Testing
- [ ] Ran test_service.py locally
- [ ] Service responds to /health endpoint
- [ ] Service returns valid JSON from /room-status
- [ ] Response includes expected fields (status, room_name, current_time)
- [ ] Times displayed correctly in your timezone

## 🚀 Deployment

### Service Deployment
- [ ] Deployed service to chosen platform
- [ ] Service is publicly accessible
- [ ] HTTPS enabled (recommended for production)
- [ ] Health check endpoint working
- [ ] Noted deployment URL

### TRMNL Configuration
- [ ] Logged into usetrmnl.com account
- [ ] Created new Private Plugin
- [ ] Set strategy to "Polling"
- [ ] Configured polling URL with ICS feed
- [ ] URL-encoded special characters in ICS URL
- [ ] Set room_name parameter
- [ ] Pasted Liquid template into markup editor
- [ ] Set refresh interval (5-15 minutes recommended)
- [ ] Clicked "Force Refresh" to test
- [ ] Reviewed generated display looks correct

### Playlist Setup
- [ ] Added plugin to TRMNL playlist
- [ ] Set appropriate display duration
- [ ] Ordered plugins as desired
- [ ] Saved playlist configuration

### Device Configuration
- [ ] TRMNL device is powered on
- [ ] Device connected to WiFi
- [ ] Device is syncing (check last update time)
- [ ] Room display showing on device

## 🔧 Production Readiness

### Security
- [ ] ICS URLs kept private (not committed to public repos)
- [ ] Service running behind reverse proxy (nginx/caddy)
- [ ] HTTPS/SSL configured
- [ ] Security headers configured (if using nginx)
- [ ] Rate limiting considered (if high traffic)
- [ ] Firewall rules reviewed

### Monitoring
- [ ] Logs configured and accessible
- [ ] Health check endpoint monitored
- [ ] Alert configured for service downtime
- [ ] Calendar feed availability monitored
- [ ] Device battery level monitored

### Documentation
- [ ] Service URL documented for team
- [ ] Deployment credentials secured
- [ ] Recovery procedures documented
- [ ] Team trained on troubleshooting

## 🎯 Post-Deployment

### Initial Verification (First 24 Hours)
- [ ] Display updated at configured interval
- [ ] Current bookings showing correctly
- [ ] Next booking information accurate
- [ ] Times displayed in correct timezone
- [ ] Status transitions (available→occupied) working
- [ ] Display readable from intended distance

### Week 1 Checks
- [ ] No service downtime reported
- [ ] Calendar sync working consistently
- [ ] E-ink display quality good (no ghosting)
- [ ] Battery life acceptable
- [ ] User feedback collected

### Ongoing Maintenance
- [ ] Weekly: Check service logs
- [ ] Weekly: Verify calendar sync
- [ ] Monthly: Review display accuracy
- [ ] Monthly: Check for service updates
- [ ] Quarterly: Review ICS URL validity

## 🚨 Troubleshooting Reference

### Display Shows "ERROR"
1. Test service URL directly in browser
2. Check service logs for errors
3. Verify ICS URL still accessible
4. Check timezone configuration
5. Force refresh from TRMNL

### Times Are Wrong
1. Verify TIMEZONE setting in service
2. Check calendar timezone settings
3. Test with curl to see raw response
4. Verify ICS feed includes timezone data

### Display Not Updating
1. Check TRMNL device is online
2. Verify playlist is active
3. Check refresh interval setting
4. Force refresh from plugin settings
5. Review TRMNL device logs

### Service Returns 400/500 Errors
1. Verify all required parameters present
2. Check ICS URL is properly URL-encoded
3. Review service application logs
4. Test ICS URL accessibility from server
5. Verify Python dependencies installed

## 📞 Support Resources

- **TRMNL Docs**: https://docs.usetrmnl.com
- **TRMNL Discord**: Check account page for invite
- **Python Flask**: https://flask.palletsprojects.com
- **icalendar Docs**: https://icalendar.readthedocs.io
- **Project README**: See README.md for detailed help

## ✨ Optional Enhancements

Consider adding:
- [ ] Multiple room displays (duplicate setup for each)
- [ ] QR codes for quick booking
- [ ] Custom branding/styling
- [ ] Email notifications
- [ ] Analytics/usage tracking
- [ ] Integration with meeting room booking system
- [ ] Backup/redundancy for critical rooms

---

## Notes Section

Use this space for your deployment-specific notes:

**Deployment Date**: _______________

**Deployment URL**: _______________

**Room Name**: _______________

**ICS URL Source**: _______________

**Team Contact**: _______________

**Additional Notes**:






---

Good luck with your deployment! 🚀
