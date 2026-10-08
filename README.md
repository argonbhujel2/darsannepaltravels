# Darshan Nepal Travel & Tours

Premium travel agency website for **Darshan Nepal Travel & Tours**, Urlabari, Koshi Province 56604, Nepal.

**Stack:** HTML5 · CSS3 · Vanilla JavaScript · Python · Flask · Jinja2 · SQLAlchemy · SQLite/PostgreSQL

No React, Next.js, Vue, Tailwind, Bootstrap, or other frontend frameworks.

---

## Quick Start

```bash
cd darshan-nepal
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python run.py
```

Open: **http://127.0.0.1:5000**

### Admin Login

- URL: **http://127.0.0.1:5000/admin/login**
- Email: `admin@darshannepal.com`
- Password: `Admin@Darshan2024`

**Change this password in production.**

---

## Features

### Public site
- Cinematic homepage with hero, smart search, featured packages, destinations
- Package listing & detail (filters, itinerary, sticky enquire)
- Destinations, services, vehicles, fixed departures
- Multi-step travel enquiry form
- Blog, gallery (lightbox), contact, about
- SEO: sitemap.xml, robots.txt, JSON-LD, meta tags, breadcrumbs
- Mobile-first responsive design, sticky Call / Enquire CTA
- Accessibility: semantic HTML, focus states, reduced motion

### Admin CMS
- Split-screen premium login (same brand palette)
- Dashboard with stats & quick actions
- Full CRUD: packages, destinations, services, vehicles, departures, blog, gallery, testimonials, team
- Enquiry & customer management with status workflow
- Contact messages, site settings, activity logs
- CSRF protection, password hashing, session auth, rate limiting

---

## Environment

| Variable | Description |
|----------|-------------|
| `SECRET_KEY` | Flask secret (required in production) |
| `DATABASE_URL` | `sqlite:///darshan_nepal.db` or `postgresql://...` |
| `FLASK_ENV` | `development` or `production` |
| `CLOUDINARY_*` | Optional media storage |

---

## Production

```bash
export FLASK_ENV=production
export SECRET_KEY=your-long-random-secret
export DATABASE_URL=postgresql://user:pass@host/darshan_nepal
gunicorn -w 4 -b 0.0.0.0:8000 "run:app"
```

Use Flask-Migrate for schema changes:

```bash
flask db init
flask db migrate -m "initial"
flask db upgrade
```

---

## Project structure

```
darshan-nepal/
├── app/
│   ├── __init__.py          # App factory
│   ├── models.py            # SQLAlchemy models
│   ├── extensions.py
│   ├── routes/              # Blueprints
│   ├── templates/           # Jinja2 (public + admin)
│   ├── static/css|js|images
│   └── utils/seed.py        # Initial data
├── config.py
├── run.py
├── requirements.txt
└── .env.example
```

---

## Business

**Darshan Nepal Travel & Tours**  
Urlabari, Koshi Province 56604, Nepal  
Phones: 9801708396 · 9801708397 · 9841110276  
Google: 4.8/5 from 27 reviews  

*Your trusted partner for discovering Nepal.*


---

## Deploy (Vercel + Cloudinary + PostgreSQL)

1. **Database** — Create a free Postgres on [Neon](https://neon.tech) or Supabase. Copy `DATABASE_URL`.
2. **Cloudinary** — Create account, get Cloud Name / API Key / API Secret (for logo, favicon, gallery uploads on serverless).
3. **Vercel** — Import this repo, set env vars:

```
SECRET_KEY=...
FLASK_ENV=production
DATABASE_URL=postgresql://...
CLOUDINARY_CLOUD_NAME=...
CLOUDINARY_API_KEY=...
CLOUDINARY_API_SECRET=...
```

4. Deploy. First request creates tables and seeds admin.

**Local without Cloudinary:** files save to `app/static/uploads/`.

**Admin branding:** Settings → upload Logo + Favicon → appears on site, admin panel, and login.
