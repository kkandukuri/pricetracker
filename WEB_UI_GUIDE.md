# Web UI Guide - Price Tracker

A modern, user-friendly web interface for scraping and tracking product prices with real-time progress monitoring.

## 🌟 Features

✅ **Upload Files** - Upload .txt or .csv files with product URLs
✅ **Real-Time Progress** - Watch scraping progress live with automatic updates
✅ **Background Processing** - Jobs continue even if you close the browser
✅ **Resume Monitoring** - Return anytime to check job status
✅ **Auto CSV Export** - Download results when complete
✅ **Multiple Jobs** - Run multiple scraping jobs simultaneously
✅ **Error Tracking** - See which URLs failed and why
✅ **Statistics Dashboard** - Track total products and job status

---

## 🚀 Quick Start

### Step 1: Install Dependencies

```bash
cd /home/user/pricetracker
pip install -r requirements.txt
```

### Step 2: Start the Web Server

```bash
python web_app.py
```

You'll see:
```
================================================================================
Price Tracker Web UI
================================================================================

Starting web server...
Open your browser and go to: http://localhost:5000

Press Ctrl+C to stop the server
================================================================================
```

### Step 3: Open in Browser

Visit: **http://localhost:5000**

---

## 📖 Using the Web Interface

### 1. Dashboard Overview

When you open the web UI, you'll see:

**Statistics Cards:**
- 📊 Total Products - All products in database
- ⏳ Running Jobs - Currently scraping
- ✅ Completed Jobs - Finished successfully

### 2. Upload URLs

**File Upload Section:**

1. **Select File**: Choose a .txt or .csv file
   - `.txt` format: One URL per line
   - `.csv` format: Must have 'url' column

2. **Set Delay**: Time between requests (seconds)
   - Recommended: 5+ seconds
   - Higher = safer, lower = faster (but risk blocking)

3. **Selenium Option**: Check if site uses JavaScript
   - Use for Instacart, modern React sites
   - Slower but handles dynamic content

4. **Click "Start Scraping"**

**Example URL file:**
```txt
https://distacart.com/products/product1
https://distacart.com/products/product2
https://distacart.com/products/product3
```

### 3. Monitor Progress

Once started, you'll see a job card with:

**Job Information:**
- 📄 Filename
- 🟢 Status (Queued → Running → Completed)
- 📊 Progress bar (real-time updates)
- ✓ Success count
- ✗ Failed count
- Current URL being scraped

**Status Colors:**
- 🟡 Yellow = Queued (waiting to start)
- 🔵 Blue = Running (actively scraping)
- 🟢 Green = Completed (success!)
- 🔴 Red = Failed (error occurred)

### 4. Close Browser & Return

**Important**: You can safely close your browser!

- Job continues running in the background
- Server keeps processing URLs
- Return anytime to check progress
- Jobs are saved to disk

**To check later:**
1. Open http://localhost:5000
2. Scroll to "Scraping Jobs" section
3. See current status and progress

### 5. Download Results

When job completes:
1. Job status turns 🟢 Green "COMPLETED"
2. "📥 Download CSV" button appears
3. Click to download your results

**CSV includes:**
- URL, NAME, Description, ShortDescription
- Price, color, Size
- Category, childCategory
- Image URLs

---

## 💡 Usage Examples

### Example 1: Simple Bulk Scraping

```bash
# 1. Start web server
python web_app.py

# 2. In browser (http://localhost:5000):
#    - Upload: urls.txt
#    - Delay: 5 seconds
#    - Selenium: unchecked
#    - Click: Start Scraping

# 3. Watch progress in real-time
# 4. Download CSV when complete
```

### Example 2: JavaScript-Heavy Sites

```bash
# 1. Start server
python web_app.py

# 2. In browser:
#    - Upload: instacart_urls.txt
#    - Delay: 10 seconds
#    - Selenium: ✅ CHECKED
#    - Click: Start Scraping

# 3. Job processes with Selenium
# 4. Download results
```

### Example 3: Multiple Jobs

```bash
# 1. Start server
python web_app.py

# 2. Upload first file:
#    - beauty_products.txt
#    - Delay: 5 seconds

# 3. Upload second file (while first is running):
#    - electronics.txt
#    - Delay: 5 seconds

# Both jobs run simultaneously!
# Each has its own progress bar
# Download each separately when done
```

### Example 4: Close & Resume

```bash
# Day 1 - 5:00 PM:
python web_app.py
# Upload: large_list_1000_urls.txt
# Close browser, go home

# Day 2 - 9:00 AM:
# Open: http://localhost:5000
# Job still running! See progress
# Or already completed, download CSV
```

---

## 🔧 Advanced Usage

### Run on Network

Allow access from other devices on your network:

```bash
# Server already configured to listen on 0.0.0.0
# Just find your IP address:
ip addr show  # Linux
ifconfig      # macOS

# Then access from other devices:
# http://YOUR_IP:5000
# Example: http://192.168.1.100:5000
```

### Custom Port

Edit `web_app.py` line 272:
```python
app.run(host='0.0.0.0', port=8080, debug=True, threaded=True)
```

Then access: `http://localhost:8080`

### Production Deployment

For production use (not development):

```bash
# Install gunicorn
pip install gunicorn

# Run with gunicorn (production server)
gunicorn -w 4 -b 0.0.0.0:5000 web_app:app

# Or with nginx reverse proxy for better performance
```

### Auto-Start on Server Boot

Create systemd service:

```bash
sudo nano /etc/systemd/system/pricetracker-web.service
```

Add:
```ini
[Unit]
Description=Price Tracker Web UI
After=network.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/home/user/pricetracker
ExecStart=/usr/bin/python3 /home/user/pricetracker/web_app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable pricetracker-web
sudo systemctl start pricetracker-web
```

---

## 📊 Understanding Job Status

### Job Lifecycle

```
1. Queued     → Waiting to start (just uploaded)
2. Running    → Actively scraping URLs
3. Completed  → Finished successfully
4. Failed     → Error occurred
5. Cancelled  → User cancelled
```

### Progress Information

**Real-time updates every 2 seconds:**
- Current/Total URLs processed
- Success/Failed counts
- Current URL being scraped
- Progress percentage
- Estimated time remaining

### Error Handling

If some URLs fail:
- Job continues to completion
- Shows error details for each failed URL
- Still generates CSV with successful products
- Can retry failed URLs later

---

## 🐛 Troubleshooting

### Issue: Server won't start

**Error:** `Address already in use`

**Solution:**
```bash
# Find process using port 5000
lsof -i :5000

# Kill it
kill -9 <PID>

# Or use different port in web_app.py
```

### Issue: Can't access from other devices

**Solution:**
```bash
# Check firewall
sudo ufw allow 5000

# Verify server is listening on 0.0.0.0
netstat -tuln | grep 5000
```

### Issue: Job stuck in "Running"

**Possible causes:**
1. Server crashed - restart: `python web_app.py`
2. Very slow website - be patient
3. Network issues - check internet connection

**Check logs:**
```bash
# Server logs show in terminal where you ran python web_app.py
# Look for error messages
```

### Issue: CSV download fails

**Solution:**
```bash
# Check downloads folder exists
ls downloads/

# Check job completed successfully
# Look for green "COMPLETED" status

# Restart server if needed
```

### Issue: Browser shows old data

**Solution:**
```bash
# Hard refresh browser
# Ctrl+Shift+R (Linux/Windows)
# Cmd+Shift+R (macOS)

# Or clear browser cache
```

---

## 📱 Mobile Access

The web UI is mobile-responsive!

**On your phone:**
1. Find server IP address (see "Run on Network" above)
2. Connect phone to same WiFi network
3. Open browser on phone
4. Go to: `http://SERVER_IP:5000`
5. Upload files, monitor progress, download CSV!

---

## 🔒 Security Considerations

**Development Use (Current Setup):**
- ✅ Fine for local use
- ✅ Fine for private networks
- ⚠️ NOT for public internet

**For Production:**
- Add authentication (username/password)
- Use HTTPS (SSL certificate)
- Add rate limiting
- Validate file uploads
- Add CSRF protection

---

## 📁 File Structure

```
pricetracker/
├── web_app.py              # Flask web server
├── templates/
│   └── index.html          # Main UI template
├── static/
│   ├── style.css           # Styles
│   └── app.js              # Frontend JavaScript
├── uploads/                # Uploaded URL files
├── downloads/              # Generated CSV files
└── data/
    └── jobs.json           # Job status persistence
```

---

## 🎯 Best Practices

### 1. File Upload
- ✅ Use descriptive filenames
- ✅ Test with 3-5 URLs first
- ✅ Use appropriate delays (5+ seconds)
- ✅ Check file format is correct

### 2. Monitoring
- ✅ Watch first few URLs to ensure scraping works
- ✅ Check for errors early
- ✅ Cancel and adjust if too many failures

### 3. Performance
- ✅ Don't run too many jobs simultaneously (2-3 max)
- ✅ Use higher delays for multiple jobs
- ✅ Close unused browser tabs

### 4. Data Management
- ✅ Download CSVs promptly
- ✅ Clean up old jobs periodically
- ✅ Keep URL files organized

---

## 💻 API Endpoints

The web UI uses these REST API endpoints:

```
POST   /api/upload              Upload file and start job
GET    /api/jobs                List all jobs
GET    /api/jobs/<job_id>       Get specific job status
POST   /api/jobs/<job_id>/cancel Cancel running job
GET    /api/download/<job_id>   Download CSV file
GET    /api/stats               Get overall statistics
```

**Use programmatically:**

```python
import requests

# Upload file
files = {'file': open('urls.txt', 'rb')}
data = {'delay': 5, 'selenium': False}
response = requests.post('http://localhost:5000/api/upload',
                        files=files, data=data)
job_id = response.json()['job_id']

# Check status
status = requests.get(f'http://localhost:5000/api/jobs/{job_id}')
print(status.json())

# Download when complete
csv_file = requests.get(f'http://localhost:5000/api/download/{job_id}')
with open('results.csv', 'wb') as f:
    f.write(csv_file.content)
```

---

## 🎨 Customization

### Change Colors

Edit `static/style.css`:

```css
/* Primary color gradient */
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);

/* Change to your preferred colors */
background: linear-gradient(135deg, #FF6B6B 0%, #4ECDC4 100%);
```

### Change Polling Interval

Edit `static/app.js` line 11:

```javascript
// Update every 2 seconds (current)
pollingInterval = setInterval(() => {
    loadStats();
    loadJobs();
}, 2000);

// Change to 5 seconds
}, 5000);
```

### Add Logo

Edit `templates/index.html`:

```html
<header>
    <img src="{{ url_for('static', filename='logo.png') }}" alt="Logo">
    <h1>🛒 E-Commerce Price Tracker</h1>
</header>
```

---

## ✅ Summary

**To use the Web UI:**

1. **Start server:**
   ```bash
   python web_app.py
   ```

2. **Open browser:**
   ```
   http://localhost:5000
   ```

3. **Upload file** with URLs

4. **Watch progress** in real-time

5. **Close browser** (optional - job continues!)

6. **Return later** to check status

7. **Download CSV** when complete

**Key Benefits:**
- ✨ Beautiful, modern interface
- 📊 Real-time progress updates
- 🔄 Background processing
- 💾 Persistent job tracking
- 📥 Easy CSV downloads
- 📱 Mobile-friendly

**Perfect for:**
- Bulk product scraping
- Long-running jobs
- Non-technical users
- Remote monitoring
- Team collaboration

Enjoy your web-based price tracker! 🚀
