#!/usr/bin/env python3
"""
Web UI for Price Tracker
Flask-based web interface with background job processing
"""
import os
import json
import uuid
import threading
import time
from datetime import datetime
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename

from src.tracker import PriceTracker
from upc_price_lookup import UPCPriceLookup


# Configuration
UPLOAD_FOLDER = 'uploads'
DOWNLOAD_FOLDER = 'downloads'
JOBS_FILE = 'data/jobs.json'
ALLOWED_EXTENSIONS = {'txt', 'csv'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create directories
Path(UPLOAD_FOLDER).mkdir(exist_ok=True)
Path(DOWNLOAD_FOLDER).mkdir(exist_ok=True)
Path('data').mkdir(exist_ok=True)

# Job storage
jobs = {}
jobs_lock = threading.Lock()

# UPC job storage
upc_jobs = {}
upc_jobs_lock = threading.Lock()


def load_jobs():
    """Load jobs from disk."""
    global jobs
    if Path(JOBS_FILE).exists():
        with open(JOBS_FILE, 'r') as f:
            jobs = json.load(f)


def save_jobs():
    """Save jobs to disk."""
    with open(JOBS_FILE, 'w') as f:
        json.dump(jobs, f, indent=2, default=str)


def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def read_urls_from_file(filepath):
    """Read URLs from uploaded file."""
    urls = []

    if filepath.endswith('.csv'):
        import csv
        with open(filepath, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                url = row.get('url', '').strip()
                if url and not url.startswith('#'):
                    urls.append(url)
    else:
        with open(filepath, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    urls.append(line)

    return urls


def scrape_job(job_id, urls, delay, use_selenium):
    """
    Background job to scrape URLs.

    Args:
        job_id: Unique job identifier
        urls: List of URLs to scrape
        delay: Delay between requests in seconds
        use_selenium: Whether to use Selenium
    """
    with jobs_lock:
        jobs[job_id]['status'] = 'running'
        jobs[job_id]['started_at'] = datetime.now().isoformat()
        save_jobs()

    tracker = PriceTracker(config_path='config/sites.json')

    success_count = 0
    failed_count = 0
    errors = []

    try:
        for i, url in enumerate(urls, 1):
            # Update progress
            with jobs_lock:
                jobs[job_id]['current'] = i
                jobs[job_id]['current_url'] = url
                save_jobs()

            # Scrape URL
            try:
                existing = tracker.db.get_product_by_url(url)
                if existing:
                    success_count += 1
                    with jobs_lock:
                        jobs[job_id]['success'] = success_count
                        save_jobs()
                else:
                    product = tracker.track_product(url, use_selenium=use_selenium)
                    if product:
                        success_count += 1
                    else:
                        failed_count += 1
                        errors.append({'url': url, 'error': 'Failed to scrape'})

                    with jobs_lock:
                        jobs[job_id]['success'] = success_count
                        jobs[job_id]['failed'] = failed_count
                        save_jobs()

            except Exception as e:
                failed_count += 1
                errors.append({'url': url, 'error': str(e)})
                with jobs_lock:
                    jobs[job_id]['failed'] = failed_count
                    save_jobs()

            # Delay between requests (except for last URL)
            if i < len(urls):
                time.sleep(delay)

        # Export to CSV
        output_file = f"{app.config['DOWNLOAD_FOLDER']}/{job_id}.csv"

        from export_csv import export_to_csv
        export_to_csv(output_file, include_images=True, include_metadata=False)

        # Mark as completed
        with jobs_lock:
            jobs[job_id]['status'] = 'completed'
            jobs[job_id]['completed_at'] = datetime.now().isoformat()
            jobs[job_id]['download_file'] = f"{job_id}.csv"
            jobs[job_id]['errors'] = errors
            save_jobs()

    except Exception as e:
        with jobs_lock:
            jobs[job_id]['status'] = 'failed'
            jobs[job_id]['error'] = str(e)
            save_jobs()

    finally:
        tracker.close()


@app.route('/')
def index():
    """Render product scraper page."""
    return render_template('scraper.html')


@app.route('/upc')
def upc_lookup():
    """Render UPC lookup page."""
    return render_template('upc_lookup.html')


@app.route('/products')
def products():
    """Render products page."""
    return render_template('products.html')


@app.route('/config')
def site_config():
    """Render site configuration page."""
    return render_template('site_config.html')


@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Handle file upload and start scraping job."""

    # Check if file is present
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Use .txt or .csv'}), 400

    # Get parameters
    delay = float(request.form.get('delay', 3))
    use_selenium = request.form.get('selenium') == 'true'

    # Save uploaded file
    filename = secure_filename(file.filename)
    job_id = str(uuid.uuid4())
    upload_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{job_id}_{filename}")
    file.save(upload_path)

    # Read URLs
    try:
        urls = read_urls_from_file(upload_path)
    except Exception as e:
        return jsonify({'error': f'Failed to read URLs: {str(e)}'}), 400

    if not urls:
        return jsonify({'error': 'No valid URLs found in file'}), 400

    # Create job
    with jobs_lock:
        jobs[job_id] = {
            'id': job_id,
            'filename': filename,
            'status': 'queued',
            'total': len(urls),
            'current': 0,
            'success': 0,
            'failed': 0,
            'current_url': '',
            'created_at': datetime.now().isoformat(),
            'started_at': None,
            'completed_at': None,
            'delay': delay,
            'use_selenium': use_selenium,
            'download_file': None,
            'errors': []
        }
        save_jobs()

    # Start background job
    thread = threading.Thread(
        target=scrape_job,
        args=(job_id, urls, delay, use_selenium),
        daemon=True
    )
    thread.start()

    return jsonify({
        'job_id': job_id,
        'total_urls': len(urls),
        'message': 'Job started successfully'
    })


@app.route('/api/jobs')
def get_jobs():
    """Get all jobs."""
    with jobs_lock:
        return jsonify(list(jobs.values()))


@app.route('/api/jobs/<job_id>')
def get_job(job_id):
    """Get specific job status."""
    with jobs_lock:
        if job_id not in jobs:
            return jsonify({'error': 'Job not found'}), 404
        return jsonify(jobs[job_id])


@app.route('/api/jobs/<job_id>/cancel', methods=['POST'])
def cancel_job(job_id):
    """Cancel a running job."""
    with jobs_lock:
        if job_id not in jobs:
            return jsonify({'error': 'Job not found'}), 404

        if jobs[job_id]['status'] == 'running':
            jobs[job_id]['status'] = 'cancelled'
            save_jobs()
            return jsonify({'message': 'Job cancelled'})
        else:
            return jsonify({'error': 'Job is not running'}), 400


@app.route('/api/download/<job_id>')
def download_csv(job_id):
    """Download CSV file for completed job."""
    with jobs_lock:
        if job_id not in jobs:
            return jsonify({'error': 'Job not found'}), 404

        job = jobs[job_id]

        if job['status'] != 'completed':
            return jsonify({'error': 'Job not completed yet'}), 400

        if not job['download_file']:
            return jsonify({'error': 'No file available'}), 404

        file_path = os.path.join(app.config['DOWNLOAD_FOLDER'], job['download_file'])

        if not os.path.exists(file_path):
            return jsonify({'error': 'File not found'}), 404

        return send_file(
            file_path,
            as_attachment=True,
            download_name=f"products_{job_id}.csv"
        )


@app.route('/api/stats')
def get_stats():
    """Get overall statistics."""
    from src.database import Database

    db = Database()
    try:
        products = db.get_all_products()

        stats = {
            'total_products': len(products),
            'total_jobs': len(jobs),
            'running_jobs': sum(1 for j in jobs.values() if j['status'] == 'running'),
            'completed_jobs': sum(1 for j in jobs.values() if j['status'] == 'completed'),
            'failed_jobs': sum(1 for j in jobs.values() if j['status'] == 'failed')
        }

        return jsonify(stats)
    finally:
        db.close()


@app.route('/api/upc/lookup', methods=['POST'])
def upc_lookup_single():
    """Look up a single UPC code."""
    data = request.get_json()
    upc = data.get('upc')

    if not upc:
        return jsonify({'error': 'UPC code required'}), 400

    rate_limit = int(data.get('rate_limit', 20))
    country = data.get('country', 'US')
    currency = data.get('currency', 'USD')

    try:
        lookup = UPCPriceLookup(rate_limit=rate_limit, country_code=country, currency=currency)
        result = lookup.lookup_upc(upc)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/products/all')
def get_all_products():
    """Get all products from database."""
    from src.database import Database

    db = Database()
    try:
        products = db.get_all_products()

        products_data = []
        for p in products:
            products_data.append({
                'id': p.id,
                'url': p.url,
                'name': p.name,
                'description': p.description[:100] + '...' if len(p.description) > 100 else p.description,
                'price': p.current_price,
                'currency': p.currency,
                'upc': p.upc,
                'site': p.site_name,
                'images': p.image_urls[:1] if p.image_urls else [],
                'created_at': str(p.created_at),
                'updated_at': str(p.updated_at)
            })

        return jsonify(products_data)
    finally:
        db.close()


@app.route('/api/sites/config', methods=['GET'])
def get_sites_config():
    """Get current sites configuration."""
    config_path = Path('config/sites.json')

    if not config_path.exists():
        return jsonify({'error': 'Configuration file not found'}), 404

    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        return jsonify(config)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/sites/config', methods=['POST'])
def update_sites_config():
    """Update sites configuration."""
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No configuration data provided'}), 400

    config_path = Path('config/sites.json')

    try:
        # Backup existing config
        if config_path.exists():
            backup_path = Path(f'config/sites.json.backup.{int(time.time())}')
            import shutil
            shutil.copy(config_path, backup_path)

        # Write new config
        with open(config_path, 'w') as f:
            json.dump(data, f, indent=2)

        return jsonify({'success': True, 'message': 'Configuration updated successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/sites/test', methods=['POST'])
def test_selector():
    """Test a CSS selector against a URL."""
    data = request.get_json()

    url = data.get('url')
    selector = data.get('selector')
    field_type = data.get('field_type', 'text')

    if not url or not selector:
        return jsonify({'error': 'URL and selector required'}), 400

    try:
        import requests
        from bs4 import BeautifulSoup

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'lxml')

        # Try to find elements
        elements = soup.select(selector)

        if not elements:
            return jsonify({
                'found': False,
                'count': 0,
                'message': f'No elements found matching selector: {selector}'
            })

        # Extract values based on field type
        results = []
        for i, elem in enumerate(elements[:5]):  # Limit to first 5
            if field_type == 'image':
                value = elem.get('src') or elem.get('data-src') or elem.get('data-lazy-src')
            else:
                value = elem.get_text(strip=True)

            results.append({
                'index': i + 1,
                'value': value[:200] if value else '(empty)',  # Limit length
                'tag': elem.name,
                'classes': elem.get('class', [])
            })

        return jsonify({
            'found': True,
            'count': len(elements),
            'results': results,
            'message': f'Found {len(elements)} element(s)'
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    # Load existing jobs
    load_jobs()

    print("="*80)
    print("Price Tracker Web UI")
    print("="*80)
    print("\nStarting web server...")
    print("Open your browser and go to: http://localhost:5000")
    print("\nPress Ctrl+C to stop the server")
    print("="*80)
    print()

    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)
