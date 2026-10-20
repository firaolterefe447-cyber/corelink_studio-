# CoreLink Studio - Separate Django Project

This is a standalone Django project for the CoreLink Studio website, deployed on studio.corelink.et.

## Project Structure

```
studio_project/
├── config/              # Django project configuration
│   ├── settings.py     # Studio-specific settings
│   ├── urls.py         # URL routing (studio at root)
│   ├── wsgi.py         # WSGI application
│   └── asgi.py         # ASGI application
├── studio/             # Studio app (copied from main project)
├── core/               # Core app (minimal - TimeStampedModel only)
├── manage.py           # Django management script
├── passenger_wsgi.py   # Passenger WSGI entry point for cPanel
└── requirements.txt    # Python dependencies
```

## Deployment Instructions

### 1. Upload to Server

Upload the entire `studio_project` folder to `/home/corelink/studio_project` on your server.

### 2. Create Virtual Environment

```bash
cd /home/corelink/studio_project
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```bash
DEBUG=False
SECRET_KEY=your-production-secret-key
DB_NAME=corelink_corelink_db
DB_USER=corelink_firaol
DB_PASSWORD=your-database-password
DB_HOST=localhost
DB_PORT=5432
```

### 5. Run Migrations

```bash
python manage.py migrate
```

### 6. Collect Static Files

```bash
python manage.py collectstatic
```

### 7. Configure cPanel Python App

1. Go to cPanel → Setup Python App
2. Create a new Python application:
   - Python version: 3.11 or 3.12
   - Application root: `/home/corelink/studio_project`
   - Application URL: `studio.corelink.et`
   - Application startup file: `passenger_wsgi.py`
   - Application entry point: `application`
3. Configure the virtual environment path to `/home/corelink/studio_project/venv`
4. Click "Restart"

### 8. Configure Domain Document Root

1. Go to cPanel → Domains
2. Edit `studio.corelink.et`
3. Change document root to: `/home/corelink/studio_project`

### 9. Configure Cloudflare DNS

Ensure Cloudflare has an A record:
- Name: studio
- Type: A
- IPv4 address: 91.204.209.4
- Proxy: Orange cloud (enabled) or gray (disabled)

## SEO Benefits

This separate project approach provides:
- ✅ Separate domain indexed by Google
- ✅ Unique content on studio.corelink.et
- ✅ No redirects (better for SEO)
- ✅ Studio can have its own sitemap
- ✅ Studio can have its own SEO metadata

## Database

This project uses:
- **SQLite for local development** (no database password needed)
- **PostgreSQL for production** (same database as main platform)

This allows:
- Shared studio data (services, projects, testimonials)
- No data duplication
- Easy local testing

## Differences from Main Project

- Only includes studio and core apps (minimal dependencies)
- Uses default Django User model (not CustomUser)
- Simplified middleware (no auth verification, no API)
- Studio app at root URL (not /studio/)
- Separate Python app in cPanel
- Separate virtual environment
- SQLite for local development

## Maintenance

To update the studio app:
1. Make changes in the main project's studio app
2. Copy updated files to `/home/corelink/studio_project/studio/`
3. Restart the Python app in cPanel
