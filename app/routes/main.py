from flask import Blueprint, render_template, request, Response
from app.models import Package, Destination, Service, Testimonial, GalleryImage, BlogPost, FixedDeparture, SiteSetting
from app.extensions import db
from datetime import datetime

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def home():
    featured_packages = Package.query.filter_by(status='published', featured=True).order_by(Package.sort_order).limit(8).all()
    destinations = Destination.query.filter_by(status='published', featured=True).order_by(Destination.sort_order).limit(8).all()
    services = Service.query.filter_by(status='published').order_by(Service.sort_order).limit(12).all()
    testimonials = Testimonial.query.filter_by(status='published', featured=True).limit(6).all()
    gallery = GalleryImage.query.filter_by(status='published').order_by(GalleryImage.sort_order).limit(12).all()
    blog_posts = BlogPost.query.filter_by(status='published').order_by(BlogPost.published_date.desc()).limit(3).all()
    departures = FixedDeparture.query.filter(
        FixedDeparture.status.in_(['Open', 'Filling Fast', 'Almost Full']),
        FixedDeparture.departure_date >= datetime.utcnow().date()
    ).order_by(FixedDeparture.departure_date).limit(6).all()

    return render_template('home.html',
                           featured_packages=featured_packages,
                           destinations=destinations,
                           services=services,
                           testimonials=testimonials,
                           gallery=gallery,
                           blog_posts=blog_posts,
                           departures=departures)


@main_bp.route('/about')
def about():
    from app.models import Guide
    team = Guide.query.filter_by(status='active').order_by(Guide.sort_order).all()
    return render_template('about.html', team=team)


@main_bp.route('/contact', methods=['GET', 'POST'])
def contact():
    from app.models import ContactMessage
    from app.extensions import csrf
    success = False
    error = None
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        phone = request.form.get('phone', '').strip()
        email = request.form.get('email', '').strip()
        subject = request.form.get('subject', '').strip()
        message = request.form.get('message', '').strip()
        if not name or not message:
            error = 'Name and message are required.'
        else:
            msg = ContactMessage(name=name, phone=phone, email=email, subject=subject, message=message)
            db.session.add(msg)
            db.session.commit()
            success = True
    return render_template('contact.html', success=success, error=error)


@main_bp.route('/gallery')
def gallery():
    category = request.args.get('category', '')
    query = GalleryImage.query.filter_by(status='published')
    if category:
        query = query.filter_by(category=category)
    images = query.order_by(GalleryImage.sort_order).all()
    categories = db.session.query(GalleryImage.category).filter(
        GalleryImage.status == 'published',
        GalleryImage.category.isnot(None)
    ).distinct().all()
    categories = [c[0] for c in categories if c[0]]
    return render_template('gallery.html', images=images, categories=categories, active_category=category)


@main_bp.route('/search')
def search():
    q = request.args.get('q', '').strip()
    results = {'packages': [], 'destinations': [], 'blog': [], 'services': []}
    if q and len(q) >= 2:
        like = f'%{q}%'
        results['packages'] = Package.query.filter(
            Package.status == 'published',
            db.or_(Package.title.ilike(like), Package.destination.ilike(like), Package.short_description.ilike(like))
        ).limit(10).all()
        results['destinations'] = Destination.query.filter(
            Destination.status == 'published',
            db.or_(Destination.name.ilike(like), Destination.short_description.ilike(like))
        ).limit(10).all()
        results['blog'] = BlogPost.query.filter(
            BlogPost.status == 'published',
            db.or_(BlogPost.title.ilike(like), BlogPost.excerpt.ilike(like))
        ).limit(10).all()
        results['services'] = Service.query.filter(
            Service.status == 'published',
            db.or_(Service.title.ilike(like), Service.description.ilike(like))
        ).limit(10).all()
    return render_template('search.html', query=q, results=results)


@main_bp.route('/privacy-policy')
def privacy():
    return render_template('privacy.html')


@main_bp.route('/terms')
def terms():
    return render_template('terms.html')


@main_bp.route('/cancellation-policy')
def cancellation():
    return render_template('cancellation.html')


@main_bp.route('/sitemap.xml')
def sitemap():
    packages = Package.query.filter_by(status='published').all()
    destinations = Destination.query.filter_by(status='published').all()
    services = Service.query.filter_by(status='published').all()
    posts = BlogPost.query.filter_by(status='published').all()
    base = request.url_root.rstrip('/')
    xml = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    static_pages = ['', 'about', 'contact', 'packages', 'destinations', 'services',
                    'fixed-departures', 'blog', 'gallery', 'privacy-policy', 'terms', 'cancellation-policy']
    for p in static_pages:
        xml.append(f'<url><loc>{base}/{p}</loc><changefreq>weekly</changefreq><priority>0.8</priority></url>')
    for pkg in packages:
        xml.append(f'<url><loc>{base}/packages/{pkg.slug}</loc><changefreq>weekly</changefreq><priority>0.9</priority></url>')
    for d in destinations:
        xml.append(f'<url><loc>{base}/destinations/{d.slug}</loc><changefreq>weekly</changefreq><priority>0.8</priority></url>')
    for s in services:
        xml.append(f'<url><loc>{base}/services/{s.slug}</loc><changefreq>monthly</changefreq><priority>0.6</priority></url>')
    for post in posts:
        xml.append(f'<url><loc>{base}/blog/{post.slug}</loc><changefreq>monthly</changefreq><priority>0.6</priority></url>')
    xml.append('</urlset>')
    return Response('\n'.join(xml), mimetype='application/xml')


@main_bp.route('/robots.txt')
def robots():
    base = request.url_root.rstrip('/')
    content = f"""User-agent: *
Allow: /
Disallow: /admin
Disallow: /admin/
Disallow: /dashboard

Sitemap: {base}/sitemap.xml
"""
    return Response(content, mimetype='text/plain')
