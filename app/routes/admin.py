from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_user, logout_user, login_required, current_user
from app.extensions import db, limiter
from app.models import (
    AdminUser, Package, Destination, Service, Vehicle, FixedDeparture,
    Enquiry, Customer, Guide, Testimonial, GalleryImage, BlogPost,
    ContactMessage, SiteSetting, ActivityLog, VehicleEnquiry
)
from datetime import datetime
from functools import wraps
from slugify import slugify

admin_bp = Blueprint('admin', __name__)


def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('admin.login'))
            if current_user.role not in roles and current_user.role != 'super_admin':
                abort(403)
            return f(*args, **kwargs)
        return wrapped
    return decorator


def log_activity(action, entity=None, entity_id=None, details=None):
    try:
        log = ActivityLog(
            admin_id=current_user.id if current_user.is_authenticated else None,
            admin_name=current_user.name if current_user.is_authenticated else None,
            action=action,
            entity=entity,
            entity_id=entity_id,
            details=details,
            ip_address=request.remote_addr
        )
        db.session.add(log)
        db.session.commit()
    except Exception:
        db.session.rollback()


@admin_bp.route('/login', methods=['GET', 'POST'])
@limiter.limit("10 per minute")
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin.dashboard'))
    error = None
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        remember = bool(request.form.get('remember'))
        user = AdminUser.query.filter_by(email=email, is_active=True).first()
        if user and user.check_password(password):
            login_user(user, remember=remember)
            user.last_login = datetime.utcnow()
            db.session.commit()
            log_activity('login')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('admin.dashboard'))
        error = 'Invalid email or password.'
    return render_template('admin/login.html', error=error)


@admin_bp.route('/logout')
@login_required
def logout():
    log_activity('logout')
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('admin.login'))


@admin_bp.route('/')
@admin_bp.route('/dashboard')
@login_required
def dashboard():
    stats = {
        'packages': Package.query.count(),
        'destinations': Destination.query.count(),
        'enquiries_new': Enquiry.query.filter_by(status='New').count(),
        'enquiries_total': Enquiry.query.count(),
        'customers': Customer.query.count(),
        'departures': FixedDeparture.query.filter(
            FixedDeparture.departure_date >= datetime.utcnow().date(),
            FixedDeparture.status.in_(['Open', 'Filling Fast', 'Almost Full'])
        ).count(),
        'gallery': GalleryImage.query.count(),
        'messages': ContactMessage.query.filter_by(status='New').count(),
    }
    recent_enquiries = Enquiry.query.order_by(Enquiry.created_at.desc()).limit(8).all()
    recent_logs = ActivityLog.query.order_by(ActivityLog.created_at.desc()).limit(10).all()
    return render_template('admin/dashboard.html', stats=stats, recent_enquiries=recent_enquiries, recent_logs=recent_logs)


# ── Packages CRUD ──────────────────────────────────────────
@admin_bp.route('/packages')
@login_required
def packages_list():
    q = request.args.get('q', '')
    status = request.args.get('status', '')
    query = Package.query
    if q:
        query = query.filter(Package.title.ilike(f'%{q}%'))
    if status:
        query = query.filter_by(status=status)
    packages = query.order_by(Package.updated_at.desc()).all()
    return render_template('admin/packages/list.html', packages=packages, q=q, status=status)


@admin_bp.route('/packages/new', methods=['GET', 'POST'])
@login_required
def package_new():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        if not title:
            flash('Title is required.', 'danger')
            return render_template('admin/packages/form.html', package=None)
        slug = request.form.get('slug') or slugify(title)
        from app.utils.uploads import upload_file
        featured_image = request.form.get('featured_image', '').strip() or None
        fimg = request.files.get('featured_image_file')
        if fimg and fimg.filename:
            uploaded = upload_file(fimg, folder='packages')
            if uploaded:
                featured_image = uploaded
        pkg = Package(
            title=title,
            slug=slug,
            short_description=request.form.get('short_description'),
            full_description=request.form.get('full_description'),
            destination=request.form.get('destination'),
            duration=request.form.get('duration'),
            duration_days=request.form.get('duration_days', type=int),
            starting_price=request.form.get('starting_price'),
            price_type=request.form.get('price_type', 'On Request'),
            travel_type=request.form.get('travel_type'),
            difficulty=request.form.get('difficulty'),
            featured_image=featured_image,
            highlights=request.form.get('highlights'),
            included=request.form.get('included'),
            excluded=request.form.get('excluded'),
            best_time=request.form.get('best_time'),
            status=request.form.get('status', 'draft'),
            featured=bool(request.form.get('featured')),
            seo_title=request.form.get('seo_title'),
            seo_description=request.form.get('seo_description'),
        )
        db.session.add(pkg)
        db.session.commit()
        log_activity('create', 'package', pkg.id, title)
        flash('Package created.', 'success')
        return redirect(url_for('admin.packages_list'))
    return render_template('admin/packages/form.html', package=None)


@admin_bp.route('/packages/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def package_edit(id):
    pkg = Package.query.get_or_404(id)
    if request.method == 'POST':
        pkg.title = request.form.get('title', '').strip() or pkg.title
        pkg.slug = request.form.get('slug') or slugify(pkg.title)
        pkg.short_description = request.form.get('short_description')
        pkg.full_description = request.form.get('full_description')
        pkg.destination = request.form.get('destination')
        pkg.duration = request.form.get('duration')
        pkg.duration_days = request.form.get('duration_days', type=int)
        pkg.starting_price = request.form.get('starting_price')
        pkg.price_type = request.form.get('price_type', 'On Request')
        pkg.travel_type = request.form.get('travel_type')
        pkg.difficulty = request.form.get('difficulty')
        pkg.highlights = request.form.get('highlights')
        pkg.included = request.form.get('included')
        pkg.excluded = request.form.get('excluded')
        pkg.best_time = request.form.get('best_time')
        pkg.status = request.form.get('status', 'draft')
        pkg.featured = bool(request.form.get('featured'))
        pkg.seo_title = request.form.get('seo_title')
        pkg.seo_description = request.form.get('seo_description')
        from app.utils.uploads import upload_file
        fimg = request.files.get('featured_image_file')
        if fimg and fimg.filename:
            uploaded = upload_file(fimg, folder='packages')
            if uploaded:
                pkg.featured_image = uploaded
        elif request.form.get('featured_image'):
            pkg.featured_image = request.form.get('featured_image').strip()
        db.session.commit()
        log_activity('update', 'package', pkg.id, pkg.title)
        flash('Package updated.', 'success')
        return redirect(url_for('admin.packages_list'))
    return render_template('admin/packages/form.html', package=pkg)


@admin_bp.route('/packages/<int:id>/delete', methods=['POST'])
@login_required
def package_delete(id):
    pkg = Package.query.get_or_404(id)
    title = pkg.title
    db.session.delete(pkg)
    db.session.commit()
    log_activity('delete', 'package', id, title)
    flash('Package deleted.', 'success')
    return redirect(url_for('admin.packages_list'))


# ── Destinations ───────────────────────────────────────────
@admin_bp.route('/destinations')
@login_required
def destinations_list():
    items = Destination.query.order_by(Destination.sort_order).all()
    return render_template('admin/destinations/list.html', destinations=items)


@admin_bp.route('/destinations/new', methods=['GET', 'POST'])
@login_required
def destination_new():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        if not name:
            flash('Name required.', 'danger')
            return render_template('admin/destinations/form.html', destination=None)
        from app.utils.uploads import upload_file
        featured_image = request.form.get('featured_image', '').strip() or None
        fimg = request.files.get('featured_image_file')
        if fimg and fimg.filename:
            uploaded = upload_file(fimg, folder='destinations')
            if uploaded:
                featured_image = uploaded
        dest = Destination(
            name=name,
            slug=request.form.get('slug') or slugify(name),
            short_description=request.form.get('short_description'),
            description=request.form.get('description'),
            best_time=request.form.get('best_time'),
            featured_image=featured_image,
            status=request.form.get('status', 'published'),
            featured=bool(request.form.get('featured')),
        )
        db.session.add(dest)
        db.session.commit()
        log_activity('create', 'destination', dest.id, name)
        flash('Destination created.', 'success')
        return redirect(url_for('admin.destinations_list'))
    return render_template('admin/destinations/form.html', destination=None)


@admin_bp.route('/destinations/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def destination_edit(id):
    dest = Destination.query.get_or_404(id)
    if request.method == 'POST':
        dest.name = request.form.get('name', '').strip() or dest.name
        dest.slug = request.form.get('slug') or slugify(dest.name)
        dest.short_description = request.form.get('short_description')
        dest.description = request.form.get('description')
        dest.best_time = request.form.get('best_time')
        dest.status = request.form.get('status', 'published')
        dest.featured = bool(request.form.get('featured'))
        from app.utils.uploads import upload_file
        fimg = request.files.get('featured_image_file')
        if fimg and fimg.filename:
            uploaded = upload_file(fimg, folder='destinations')
            if uploaded:
                dest.featured_image = uploaded
        elif request.form.get('featured_image'):
            dest.featured_image = request.form.get('featured_image').strip()
        db.session.commit()
        log_activity('update', 'destination', dest.id, dest.name)
        flash('Destination updated.', 'success')
        return redirect(url_for('admin.destinations_list'))
    return render_template('admin/destinations/form.html', destination=dest)


@admin_bp.route('/destinations/<int:id>/delete', methods=['POST'])
@login_required
def destination_delete(id):
    dest = Destination.query.get_or_404(id)
    db.session.delete(dest)
    db.session.commit()
    log_activity('delete', 'destination', id)
    flash('Deleted.', 'success')
    return redirect(url_for('admin.destinations_list'))


# ── Enquiries ──────────────────────────────────────────────
@admin_bp.route('/enquiries')
@login_required
def enquiries_list():
    status = request.args.get('status', '')
    query = Enquiry.query
    if status:
        query = query.filter_by(status=status)
    enquiries = query.order_by(Enquiry.created_at.desc()).all()
    return render_template('admin/enquiries/list.html', enquiries=enquiries, status=status)


@admin_bp.route('/enquiries/<int:id>', methods=['GET', 'POST'])
@login_required
def enquiry_detail(id):
    enq = Enquiry.query.get_or_404(id)
    if request.method == 'POST':
        enq.status = request.form.get('status', enq.status)
        enq.internal_notes = request.form.get('internal_notes', enq.internal_notes)
        db.session.commit()
        log_activity('update', 'enquiry', enq.id, enq.reference_id)
        flash('Enquiry updated.', 'success')
        return redirect(url_for('admin.enquiry_detail', id=id))
    return render_template('admin/enquiries/detail.html', enquiry=enq)


# ── Customers ──────────────────────────────────────────────
@admin_bp.route('/customers')
@login_required
def customers_list():
    customers = Customer.query.order_by(Customer.created_at.desc()).all()
    return render_template('admin/customers/list.html', customers=customers)


# ── Services ───────────────────────────────────────────────
@admin_bp.route('/services')
@login_required
def services_list():
    services = Service.query.order_by(Service.sort_order).all()
    return render_template('admin/services/list.html', services=services)


@admin_bp.route('/services/new', methods=['GET', 'POST'])
@login_required
def service_new():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        if title:
            s = Service(title=title, slug=slugify(title), description=request.form.get('description'), status='published')
            db.session.add(s)
            db.session.commit()
            flash('Service created.', 'success')
            return redirect(url_for('admin.services_list'))
    return render_template('admin/services/form.html', service=None)


@admin_bp.route('/services/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def service_edit(id):
    s = Service.query.get_or_404(id)
    if request.method == 'POST':
        s.title = request.form.get('title') or s.title
        s.description = request.form.get('description')
        s.status = request.form.get('status', 'published')
        db.session.commit()
        flash('Updated.', 'success')
        return redirect(url_for('admin.services_list'))
    return render_template('admin/services/form.html', service=s)


@admin_bp.route('/services/<int:id>/delete', methods=['POST'])
@login_required
def service_delete(id):
    s = Service.query.get_or_404(id)
    db.session.delete(s)
    db.session.commit()
    flash('Deleted.', 'success')
    return redirect(url_for('admin.services_list'))


# ── Vehicles ───────────────────────────────────────────────
@admin_bp.route('/vehicles')
@login_required
def vehicles_list():
    vehicles = Vehicle.query.order_by(Vehicle.name).all()
    return render_template('admin/vehicles/list.html', vehicles=vehicles)


@admin_bp.route('/vehicles/new', methods=['GET', 'POST'])
@login_required
def vehicle_new():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        if name:
            v = Vehicle(
                name=name,
                vehicle_type=request.form.get('vehicle_type'),
                model=request.form.get('model'),
                capacity=request.form.get('capacity', type=int),
                price=request.form.get('price', 'On Request'),
                driver_included=bool(request.form.get('driver_included')),
                ac=bool(request.form.get('ac')),
                description=request.form.get('description'),
                status='published'
            )
            db.session.add(v)
            db.session.commit()
            flash('Vehicle added.', 'success')
            return redirect(url_for('admin.vehicles_list'))
    return render_template('admin/vehicles/form.html', vehicle=None)


@admin_bp.route('/vehicles/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def vehicle_edit(id):
    v = Vehicle.query.get_or_404(id)
    if request.method == 'POST':
        v.name = request.form.get('name') or v.name
        v.vehicle_type = request.form.get('vehicle_type')
        v.model = request.form.get('model')
        v.capacity = request.form.get('capacity', type=int)
        v.price = request.form.get('price')
        v.driver_included = bool(request.form.get('driver_included'))
        v.ac = bool(request.form.get('ac'))
        v.description = request.form.get('description')
        v.status = request.form.get('status', 'published')
        db.session.commit()
        flash('Updated.', 'success')
        return redirect(url_for('admin.vehicles_list'))
    return render_template('admin/vehicles/form.html', vehicle=v)


@admin_bp.route('/vehicles/<int:id>/delete', methods=['POST'])
@login_required
def vehicle_delete(id):
    v = Vehicle.query.get_or_404(id)
    db.session.delete(v)
    db.session.commit()
    flash('Deleted.', 'success')
    return redirect(url_for('admin.vehicles_list'))


# ── Fixed Departures ───────────────────────────────────────
@admin_bp.route('/departures')
@login_required
def departures_list():
    items = FixedDeparture.query.order_by(FixedDeparture.departure_date.desc()).all()
    return render_template('admin/departures/list.html', departures=items)


@admin_bp.route('/departures/new', methods=['GET', 'POST'])
@login_required
def departure_new():
    packages = Package.query.filter_by(status='published').all()
    if request.method == 'POST':
        package_id = request.form.get('package_id', type=int)
        dep_date = request.form.get('departure_date')
        if package_id and dep_date:
            d = FixedDeparture(
                package_id=package_id,
                departure_date=datetime.strptime(dep_date, '%Y-%m-%d').date(),
                return_date=datetime.strptime(request.form.get('return_date'), '%Y-%m-%d').date() if request.form.get('return_date') else None,
                available_seats=request.form.get('available_seats', type=int) or 0,
                total_seats=request.form.get('total_seats', type=int) or 0,
                price=request.form.get('price'),
                pickup_location=request.form.get('pickup_location'),
                status=request.form.get('status', 'Open'),
            )
            db.session.add(d)
            db.session.commit()
            flash('Departure created.', 'success')
            return redirect(url_for('admin.departures_list'))
    return render_template('admin/departures/form.html', departure=None, packages=packages)


@admin_bp.route('/departures/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def departure_edit(id):
    d = FixedDeparture.query.get_or_404(id)
    packages = Package.query.filter_by(status='published').all()
    if request.method == 'POST':
        d.package_id = request.form.get('package_id', type=int) or d.package_id
        if request.form.get('departure_date'):
            d.departure_date = datetime.strptime(request.form.get('departure_date'), '%Y-%m-%d').date()
        if request.form.get('return_date'):
            d.return_date = datetime.strptime(request.form.get('return_date'), '%Y-%m-%d').date()
        d.available_seats = request.form.get('available_seats', type=int)
        d.total_seats = request.form.get('total_seats', type=int)
        d.price = request.form.get('price')
        d.pickup_location = request.form.get('pickup_location')
        d.status = request.form.get('status', 'Open')
        db.session.commit()
        flash('Updated.', 'success')
        return redirect(url_for('admin.departures_list'))
    return render_template('admin/departures/form.html', departure=d, packages=packages)


@admin_bp.route('/departures/<int:id>/delete', methods=['POST'])
@login_required
def departure_delete(id):
    d = FixedDeparture.query.get_or_404(id)
    db.session.delete(d)
    db.session.commit()
    flash('Deleted.', 'success')
    return redirect(url_for('admin.departures_list'))


# ── Testimonials ───────────────────────────────────────────
@admin_bp.route('/testimonials')
@login_required
def testimonials_list():
    items = Testimonial.query.order_by(Testimonial.created_at.desc()).all()
    return render_template('admin/testimonials/list.html', testimonials=items)


@admin_bp.route('/testimonials/new', methods=['GET', 'POST'])
@login_required
def testimonial_new():
    if request.method == 'POST':
        t = Testimonial(
            name=request.form.get('name'),
            location=request.form.get('location'),
            review=request.form.get('review'),
            rating=request.form.get('rating', 5, type=int),
            package_title=request.form.get('package_title'),
            featured=bool(request.form.get('featured')),
            status=request.form.get('status', 'published'),
        )
        db.session.add(t)
        db.session.commit()
        flash('Testimonial added.', 'success')
        return redirect(url_for('admin.testimonials_list'))
    return render_template('admin/testimonials/form.html', testimonial=None)


@admin_bp.route('/testimonials/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def testimonial_edit(id):
    t = Testimonial.query.get_or_404(id)
    if request.method == 'POST':
        t.name = request.form.get('name') or t.name
        t.location = request.form.get('location')
        t.review = request.form.get('review')
        t.rating = request.form.get('rating', type=int) or t.rating
        t.featured = bool(request.form.get('featured'))
        t.status = request.form.get('status', 'published')
        db.session.commit()
        flash('Updated.', 'success')
        return redirect(url_for('admin.testimonials_list'))
    return render_template('admin/testimonials/form.html', testimonial=t)


@admin_bp.route('/testimonials/<int:id>/delete', methods=['POST'])
@login_required
def testimonial_delete(id):
    t = Testimonial.query.get_or_404(id)
    db.session.delete(t)
    db.session.commit()
    flash('Deleted.', 'success')
    return redirect(url_for('admin.testimonials_list'))


# ── Gallery ────────────────────────────────────────────────
@admin_bp.route('/gallery')
@login_required
def gallery_list():
    images = GalleryImage.query.order_by(GalleryImage.sort_order).all()
    return render_template('admin/gallery/list.html', images=images)


@admin_bp.route('/gallery/new', methods=['GET', 'POST'])
@login_required
def gallery_new():
    from app.utils.uploads import upload_file
    if request.method == 'POST':
        url = request.form.get('image_url', '').strip()
        f = request.files.get('image_file')
        if f and f.filename:
            uploaded = upload_file(f, folder='gallery')
            if uploaded:
                url = uploaded
        if url:
            img = GalleryImage(
                image_url=url,
                alt_text=request.form.get('alt_text'),
                caption=request.form.get('caption'),
                category=request.form.get('category'),
                status='published'
            )
            db.session.add(img)
            db.session.commit()
            flash('Image added.', 'success')
            return redirect(url_for('admin.gallery_list'))
        flash('Please upload a file or provide an image URL.', 'danger')
    return render_template('admin/gallery/form.html', image=None)


@admin_bp.route('/gallery/<int:id>/delete', methods=['POST'])
@login_required
def gallery_delete(id):
    img = GalleryImage.query.get_or_404(id)
    db.session.delete(img)
    db.session.commit()
    flash('Deleted.', 'success')
    return redirect(url_for('admin.gallery_list'))


# ── Blog ───────────────────────────────────────────────────
@admin_bp.route('/blog')
@login_required
def blog_list():
    posts = BlogPost.query.order_by(BlogPost.created_at.desc()).all()
    return render_template('admin/blog/list.html', posts=posts)


@admin_bp.route('/blog/new', methods=['GET', 'POST'])
@login_required
def blog_new():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        if title:
            post = BlogPost(
                title=title,
                slug=request.form.get('slug') or slugify(title),
                excerpt=request.form.get('excerpt'),
                content=request.form.get('content'),
                category=request.form.get('category'),
                tags=request.form.get('tags'),
                status=request.form.get('status', 'draft'),
                author=request.form.get('author', 'Darshan Nepal Travel'),
            )
            db.session.add(post)
            db.session.commit()
            flash('Post created.', 'success')
            return redirect(url_for('admin.blog_list'))
    return render_template('admin/blog/form.html', post=None)


@admin_bp.route('/blog/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def blog_edit(id):
    post = BlogPost.query.get_or_404(id)
    if request.method == 'POST':
        post.title = request.form.get('title') or post.title
        post.slug = request.form.get('slug') or slugify(post.title)
        post.excerpt = request.form.get('excerpt')
        post.content = request.form.get('content')
        post.category = request.form.get('category')
        post.tags = request.form.get('tags')
        post.status = request.form.get('status', 'draft')
        db.session.commit()
        flash('Updated.', 'success')
        return redirect(url_for('admin.blog_list'))
    return render_template('admin/blog/form.html', post=post)


@admin_bp.route('/blog/<int:id>/delete', methods=['POST'])
@login_required
def blog_delete(id):
    post = BlogPost.query.get_or_404(id)
    db.session.delete(post)
    db.session.commit()
    flash('Deleted.', 'success')
    return redirect(url_for('admin.blog_list'))


# ── Team ───────────────────────────────────────────────────
@admin_bp.route('/team')
@login_required
def team_list():
    team = Guide.query.order_by(Guide.sort_order).all()
    return render_template('admin/team/list.html', team=team)


@admin_bp.route('/team/new', methods=['GET', 'POST'])
@login_required
def team_new():
    if request.method == 'POST':
        g = Guide(
            name=request.form.get('name'),
            position=request.form.get('position'),
            bio=request.form.get('bio'),
            languages=request.form.get('languages'),
            specialization=request.form.get('specialization'),
            experience=request.form.get('experience'),
            status='active'
        )
        db.session.add(g)
        db.session.commit()
        flash('Team member added.', 'success')
        return redirect(url_for('admin.team_list'))
    return render_template('admin/team/form.html', member=None)


@admin_bp.route('/team/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def team_edit(id):
    g = Guide.query.get_or_404(id)
    if request.method == 'POST':
        g.name = request.form.get('name') or g.name
        g.position = request.form.get('position')
        g.bio = request.form.get('bio')
        g.languages = request.form.get('languages')
        g.specialization = request.form.get('specialization')
        g.experience = request.form.get('experience')
        g.status = request.form.get('status', 'active')
        db.session.commit()
        flash('Updated.', 'success')
        return redirect(url_for('admin.team_list'))
    return render_template('admin/team/form.html', member=g)


@admin_bp.route('/team/<int:id>/delete', methods=['POST'])
@login_required
def team_delete(id):
    g = Guide.query.get_or_404(id)
    db.session.delete(g)
    db.session.commit()
    flash('Deleted.', 'success')
    return redirect(url_for('admin.team_list'))


# ── Contact Messages ───────────────────────────────────────
@admin_bp.route('/messages')
@login_required
def messages_list():
    messages = ContactMessage.query.order_by(ContactMessage.created_at.desc()).all()
    return render_template('admin/messages.html', messages=messages)


@admin_bp.route('/messages/<int:id>/read', methods=['POST'])
@login_required
def message_read(id):
    msg = ContactMessage.query.get_or_404(id)
    msg.status = 'Read'
    db.session.commit()
    return redirect(url_for('admin.messages_list'))


# ── Settings ───────────────────────────────────────────────
@admin_bp.route('/settings', methods=['GET', 'POST'])
@login_required
@role_required('super_admin', 'admin')
def settings():
    from app.utils.uploads import upload_file
    if request.method == 'POST':
        keys = [
            'business_name', 'address', 'phone', 'phones', 'email',
            'facebook', 'instagram', 'google_rating', 'review_count',
            'announcement', 'hero_title', 'hero_description', 'hero_eyebrow',
            'default_seo_title', 'default_seo_description'
        ]
        for key in keys:
            val = request.form.get(key)
            if val is not None:
                setting = SiteSetting.query.filter_by(key=key).first()
                if setting:
                    setting.value = val
                else:
                    db.session.add(SiteSetting(key=key, value=val))

        # Logo upload
        logo_file = request.files.get('logo_file')
        if logo_file and logo_file.filename:
            url = upload_file(logo_file, folder='logos')
            if url:
                setting = SiteSetting.query.filter_by(key='logo_url').first()
                if setting:
                    setting.value = url
                else:
                    db.session.add(SiteSetting(key='logo_url', value=url))
        elif request.form.get('logo_url_text'):
            url = request.form.get('logo_url_text').strip()
            setting = SiteSetting.query.filter_by(key='logo_url').first()
            if setting:
                setting.value = url
            else:
                db.session.add(SiteSetting(key='logo_url', value=url))

        # Favicon upload
        fav_file = request.files.get('favicon_file')
        if fav_file and fav_file.filename:
            url = upload_file(fav_file, folder='logos')
            if url:
                setting = SiteSetting.query.filter_by(key='favicon_url').first()
                if setting:
                    setting.value = url
                else:
                    db.session.add(SiteSetting(key='favicon_url', value=url))
        elif request.form.get('favicon_url_text'):
            url = request.form.get('favicon_url_text').strip()
            setting = SiteSetting.query.filter_by(key='favicon_url').first()
            if setting:
                setting.value = url
            else:
                db.session.add(SiteSetting(key='favicon_url', value=url))

        # Helper to save uploaded image setting
        def save_image_setting(file_key, setting_key, url_key=None):
            f = request.files.get(file_key)
            if f and f.filename:
                url = upload_file(f, folder='general')
                if url:
                    setting = SiteSetting.query.filter_by(key=setting_key).first()
                    if setting:
                        setting.value = url
                    else:
                        db.session.add(SiteSetting(key=setting_key, value=url))
                    return
            if url_key:
                url_val = request.form.get(url_key, '').strip()
                if url_val:
                    setting = SiteSetting.query.filter_by(key=setting_key).first()
                    if setting:
                        setting.value = url_val
                    else:
                        db.session.add(SiteSetting(key=setting_key, value=url_val))

        save_image_setting('hero_image_file', 'hero_image', 'hero_image_url')
        save_image_setting('pilgrimage_image_file', 'pilgrimage_image', 'pilgrimage_image_url')
        save_image_setting('adventure_image_file', 'adventure_image', 'adventure_image_url')

        db.session.commit()
        log_activity('update', 'settings')
        flash('Settings saved.', 'success')
        return redirect(url_for('admin.settings'))
    settings_dict = {s.key: s.value for s in SiteSetting.query.all()}
    return render_template('admin/settings/form.html', settings=settings_dict)



@admin_bp.route('/logs')
@login_required
@role_required('super_admin', 'admin')
def activity_logs():
    logs = ActivityLog.query.order_by(ActivityLog.created_at.desc()).limit(100).all()
    return render_template('admin/logs.html', logs=logs)


@admin_bp.route('/media/upload', methods=['POST'])
@login_required
def media_upload():
    """AJAX/file-picker upload — returns JSON {url, error}."""
    from app.utils.uploads import upload_file
    from flask import jsonify
    f = request.files.get('file') or request.files.get('image')
    folder = request.form.get('folder', 'general')
    if folder not in ('general', 'gallery', 'packages', 'destinations', 'logos', 'vehicles', 'blog', 'team'):
        folder = 'general'
    if not f or not f.filename:
        return jsonify({'error': 'No file provided'}), 400
    url = upload_file(f, folder=folder)
    if not url:
        return jsonify({'error': 'Upload failed. Check file type (png, jpg, webp, gif, ico, svg).'}), 400
    log_activity('upload', 'media', details=url)
    return jsonify({'url': url})
