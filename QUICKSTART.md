# Quick Start Guide

Get your room display up and running in 10 minutes!

## 1. Get Your Calendar ICS URL

**Microsoft 365:**
- Open Outlook → Calendar
- Right-click room calendar → Settings
- Find "ICS" or "Publish" link → Copy URL

**Google Calendar:**
- Calendar Settings → Integrate calendar
- Copy "Secret address in iCal format"

## 2. Test Locally (Optional)

```bash
# Install dependencies
pip3 install -r requirements.txt

# Run the service
python3 room_availability_service.py

# In another terminal, test it
python3 test_service.py
```

Enter your service URL (http://localhost:5000) and ICS URL when prompted.

## 3. Deploy

### Easiest: Railway.app (Free Tier Available)

1. Go to railway.app and sign up
2. Click "New Project" → "Deploy from GitHub"
3. Connect your GitHub repo with these files
4. Railway auto-deploys!
5. Copy your deployment URL

### Docker:

```bash
docker-compose up -d
```

### Traditional Server:

```bash
# On Ubuntu/Debian server
sudo apt install python3-pip
pip3 install -r requirements.txt
gunicorn -b 0.0.0.0:5000 room_availability_service:app
```

## 4. Configure TRMNL

1. Log in to usetrmnl.com
2. Go to Plugins → Private Plugin → Create
3. Settings:
   - **Name**: Room Availability - [Your Room]
   - **Strategy**: Polling
   - **Polling URL**: 
     ```
     https://YOUR-DEPLOYMENT-URL.com/room-status?ics_url=YOUR_ICS_URL&room_name=Conference%20Room
     ```
   - **Refresh**: Every 5-15 minutes

4. Edit Markup → Paste `trmnl_room_template_full.liquid`
5. Click "Force Refresh" to test
6. Add to Playlist!

## 5. Done! 🎉

Your TRMNL display will now show:
- ✅ Current availability status
- 📅 Next booking information
- ⏰ Real-time updates

## Troubleshooting

**Display shows ERROR:**
- Test your polling URL in a browser
- Check ICS URL is accessible
- Verify room_name is URL-encoded

**Times are wrong:**
- Edit `TIMEZONE` in room_availability_service.py
- Redeploy the service

**Not updating:**
- Check TRMNL refresh interval
- Force refresh from plugin settings
- Verify device is online

## Next Steps

- Deploy multiple instances for different rooms
- Customize the Liquid template styling
- Add QR codes for quick booking
- Set up SSL/HTTPS for production

Need help? Check the full README.md for detailed instructions.
