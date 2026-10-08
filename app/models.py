from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app.extensions import db, login_manager


def utcnow():
    return datetime.now(timezone.utc)


class AdminUser(UserMixin, db.Model):
    __tablename__ = 'admin_users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(50), default='admin')  # super_admin, admin, content_manager, booking_manager
    is_active = db.Column(db.Boolean, default=True)
    last_login = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=utcnow)
    updated_at = db.Column(db.DateTime, default=utcnow, onupdate=utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def has_permission(self, action):
        if self.role == 'super_admin':
            return True
        permissions = {
            'admin': ['view', 'create', 'edit', 'delete', 'publish'],
            'content_manager': ['view', 'create', 'edit', 'publish'],
            'booking_manager': ['view', 'edit'],
        }
        return action in permissions.get(self.role, [])


@login_manager.user_loader
def load_user(user_id):
    return AdminUser.query.get(int(user_id))


class Destination(db.Model):
    __tablename__ = 'destinations'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    slug = db.Column(db.String(160), unique=True, nullable=False, index=True)
    short_description = db.Column(db.String(300))
    description = db.Column(db.Text)
    why_visit = db.Column(db.Text)
    top_attractions = db.Column(db.Text)  # JSON or newline-separated
    things_to_do = db.Column(db.Text)
    best_time = db.Column(db.String(200))
    travel_tips = db.Column(db.Text)
    featured_image = db.Column(db.String(500))
    gallery = db.Column(db.Text)  # JSON list of image URLs
    map_embed = db.Column(db.Text)
    faq = db.Column(db.Text)  # JSON
    status = db.Column(db.String(20), default='published')  # draft, published
    featured = db.Column(db.Boolean, default=False)
    seo_title = db.Column(db.String(200))
    seo_description = db.Column(db.String(300))
    seo_keywords = db.Column(db.String(300))
    og_image = db.Column(db.String(500))
    sort_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=utcnow)
    updated_at = db.Column(db.DateTime, default=utcnow, onupdate=utcnow)

    packages = db.relationship('Package', backref='destination_rel', lazy='dynamic')
    images = db.relationship('DestinationImage', backref='destination', lazy='dynamic', cascade='all, delete-orphan')


class DestinationImage(db.Model):
    __tablename__ = 'destination_images'
    id = db.Column(db.Integer, primary_key=True)
    destination_id = db.Column(db.Integer, db.ForeignKey('destinations.id'), nullable=False)
    image_url = db.Column(db.String(500), nullable=False)
    alt_text = db.Column(db.String(200))
    caption = db.Column(db.String(300))
    sort_order = db.Column(db.Integer, default=0)


class Package(db.Model):
    __tablename__ = 'packages'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(220), unique=True, nullable=False, index=True)
    short_description = db.Column(db.String(400))
    full_description = db.Column(db.Text)
    destination = db.Column(db.String(150))
    destination_id = db.Column(db.Integer, db.ForeignKey('destinations.id'))
    duration = db.Column(db.String(50))  # e.g. "6 Days"
    duration_days = db.Column(db.Integer)
    starting_price = db.Column(db.String(50))
    price_type = db.Column(db.String(30), default='On Request')  # Starting From, Per Person, Per Group, On Request, Contact for Price
    travel_type = db.Column(db.String(50))  # Adventure, Trekking, Pilgrimage, Family, School, Team, Sightseeing, Cultural
    difficulty = db.Column(db.String(30))  # Easy, Moderate, Challenging
    featured_image = db.Column(db.String(500))
    highlights = db.Column(db.Text)  # newline or JSON
    included = db.Column(db.Text)
    excluded = db.Column(db.Text)
    best_time = db.Column(db.String(200))
    group_size = db.Column(db.String(50))
    pickup_location = db.Column(db.String(200))
    dropoff_location = db.Column(db.String(200))
    accommodation = db.Column(db.Text)
    transportation = db.Column(db.Text)
    meals = db.Column(db.Text)
    guide_info = db.Column(db.Text)
    important_info = db.Column(db.Text)
    terms = db.Column(db.Text)
    cancellation_policy = db.Column(db.Text)
    status = db.Column(db.String(20), default='published')
    featured = db.Column(db.Boolean, default=False)
    seo_title = db.Column(db.String(200))
    seo_description = db.Column(db.String(300))
    seo_keywords = db.Column(db.String(300))
    og_image = db.Column(db.String(500))
    sort_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=utcnow)
    updated_at = db.Column(db.DateTime, default=utcnow, onupdate=utcnow)

    itinerary_items = db.relationship('PackageItinerary', backref='package', lazy='dynamic',
                                      cascade='all, delete-orphan', order_by='PackageItinerary.day_number')
    images = db.relationship('PackageImage', backref='package', lazy='dynamic', cascade='all, delete-orphan')
    departures = db.relationship('FixedDeparture', backref='package', lazy='dynamic')


class PackageImage(db.Model):
    __tablename__ = 'package_images'
    id = db.Column(db.Integer, primary_key=True)
    package_id = db.Column(db.Integer, db.ForeignKey('packages.id'), nullable=False)
    image_url = db.Column(db.String(500), nullable=False)
    alt_text = db.Column(db.String(200))
    caption = db.Column(db.String(300))
    sort_order = db.Column(db.Integer, default=0)


class PackageItinerary(db.Model):
    __tablename__ = 'package_itineraries'
    id = db.Column(db.Integer, primary_key=True)
    package_id = db.Column(db.Integer, db.ForeignKey('packages.id'), nullable=False)
    day_number = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    meals = db.Column(db.String(100))
    accommodation = db.Column(db.String(200))
    transportation = db.Column(db.String(200))
    activities = db.Column(db.Text)
    image_url = db.Column(db.String(500))


class Service(db.Model):
    __tablename__ = 'services'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    slug = db.Column(db.String(160), unique=True, nullable=False, index=True)
    description = db.Column(db.Text)
    icon = db.Column(db.String(50))  # CSS class or emoji key
    featured_image = db.Column(db.String(500))
    status = db.Column(db.String(20), default='published')
    sort_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=utcnow)
    updated_at = db.Column(db.DateTime, default=utcnow, onupdate=utcnow)


class Vehicle(db.Model):
    __tablename__ = 'vehicles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    vehicle_type = db.Column(db.String(50))  # Car, Jeep, Van, Hiace, Bus, Tourist Bus
    model = db.Column(db.String(100))
    capacity = db.Column(db.Integer)
    image = db.Column(db.String(500))
    price = db.Column(db.String(50))
    price_type = db.Column(db.String(30), default='Per Day')
    driver_included = db.Column(db.Boolean, default=True)
    ac = db.Column(db.Boolean, default=False)
    availability = db.Column(db.String(20), default='available')
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='published')
    created_at = db.Column(db.DateTime, default=utcnow)
    updated_at = db.Column(db.DateTime, default=utcnow, onupdate=utcnow)


class VehicleEnquiry(db.Model):
    __tablename__ = 'vehicle_enquiries'
    id = db.Column(db.Integer, primary_key=True)
    reference_id = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120))
    vehicle_type = db.Column(db.String(50))
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id'))
    pickup = db.Column(db.String(200))
    dropoff = db.Column(db.String(200))
    date = db.Column(db.Date)
    time = db.Column(db.String(20))
    passengers = db.Column(db.Integer)
    special_request = db.Column(db.Text)
    status = db.Column(db.String(30), default='New')
    created_at = db.Column(db.DateTime, default=utcnow)


class FixedDeparture(db.Model):
    __tablename__ = 'fixed_departures'
    id = db.Column(db.Integer, primary_key=True)
    package_id = db.Column(db.Integer, db.ForeignKey('packages.id'), nullable=False)
    departure_date = db.Column(db.Date, nullable=False)
    return_date = db.Column(db.Date)
    available_seats = db.Column(db.Integer, default=0)
    total_seats = db.Column(db.Integer, default=0)
    price = db.Column(db.String(50))
    pickup_location = db.Column(db.String(200))
    booking_deadline = db.Column(db.Date)
    status = db.Column(db.String(30), default='Open')  # Open, Filling Fast, Almost Full, Sold Out, Completed, Cancelled
    created_at = db.Column(db.DateTime, default=utcnow)
    updated_at = db.Column(db.DateTime, default=utcnow, onupdate=utcnow)


class Customer(db.Model):
    __tablename__ = 'customers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False, index=True)
    email = db.Column(db.String(120))
    preferred_destinations = db.Column(db.Text)
    notes = db.Column(db.Text)  # internal only
    created_at = db.Column(db.DateTime, default=utcnow)
    updated_at = db.Column(db.DateTime, default=utcnow, onupdate=utcnow)

    enquiries = db.relationship('Enquiry', backref='customer', lazy='dynamic')


class Enquiry(db.Model):
    __tablename__ = 'enquiries'
    id = db.Column(db.Integer, primary_key=True)
    reference_id = db.Column(db.String(20), unique=True, nullable=False, index=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'))
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120))
    destination = db.Column(db.String(150))
    package_id = db.Column(db.Integer, db.ForeignKey('packages.id'))
    package_title = db.Column(db.String(200))
    travel_date = db.Column(db.Date)
    return_date = db.Column(db.Date)
    travelers = db.Column(db.Integer, default=1)
    adults = db.Column(db.Integer, default=1)
    children = db.Column(db.Integer, default=0)
    travel_type = db.Column(db.String(50))
    pickup_location = db.Column(db.String(200))
    accommodation_pref = db.Column(db.String(100))
    transportation_pref = db.Column(db.String(100))
    message = db.Column(db.Text)
    status = db.Column(db.String(30), default='New')  # New, Contacted, Following Up, Confirmed, Completed, Cancelled, Spam
    internal_notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=utcnow)
    updated_at = db.Column(db.DateTime, default=utcnow, onupdate=utcnow)

    package = db.relationship('Package', backref='enquiries')


class Guide(db.Model):
    __tablename__ = 'guides'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    position = db.Column(db.String(100))
    bio = db.Column(db.Text)
    photo = db.Column(db.String(500))
    languages = db.Column(db.String(200))
    specialization = db.Column(db.String(200))
    experience = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    status = db.Column(db.String(20), default='active')
    sort_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=utcnow)


class Testimonial(db.Model):
    __tablename__ = 'testimonials'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100))
    review = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, default=5)
    package_title = db.Column(db.String(200))
    review_date = db.Column(db.Date)
    profile_image = db.Column(db.String(500))
    verified = db.Column(db.Boolean, default=False)
    featured = db.Column(db.Boolean, default=False)
    status = db.Column(db.String(20), default='published')
    created_at = db.Column(db.DateTime, default=utcnow)


class GalleryImage(db.Model):
    __tablename__ = 'gallery_images'
    id = db.Column(db.Integer, primary_key=True)
    image_url = db.Column(db.String(500), nullable=False)
    alt_text = db.Column(db.String(200))
    caption = db.Column(db.String(300))
    category = db.Column(db.String(50))  # Mountains, Temples, Lakes, Trekking, etc.
    sort_order = db.Column(db.Integer, default=0)
    status = db.Column(db.String(20), default='published')
    created_at = db.Column(db.DateTime, default=utcnow)


class BlogPost(db.Model):
    __tablename__ = 'blog_posts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(220), unique=True, nullable=False, index=True)
    excerpt = db.Column(db.String(400))
    content = db.Column(db.Text)
    featured_image = db.Column(db.String(500))
    author = db.Column(db.String(100), default='Darshan Nepal Travel')
    category = db.Column(db.String(50))
    tags = db.Column(db.String(300))
    published_date = db.Column(db.DateTime, default=utcnow)
    status = db.Column(db.String(20), default='draft')
    seo_title = db.Column(db.String(200))
    seo_description = db.Column(db.String(300))
    og_image = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=utcnow)
    updated_at = db.Column(db.DateTime, default=utcnow, onupdate=utcnow)


class ContactMessage(db.Model):
    __tablename__ = 'contact_messages'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    subject = db.Column(db.String(200))
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='New')  # New, Read, Replied
    created_at = db.Column(db.DateTime, default=utcnow)


class SiteSetting(db.Model):
    __tablename__ = 'site_settings'
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False, index=True)
    value = db.Column(db.Text)
    updated_at = db.Column(db.DateTime, default=utcnow, onupdate=utcnow)


class SeoMetadata(db.Model):
    __tablename__ = 'seo_metadata'
    id = db.Column(db.Integer, primary_key=True)
    page_key = db.Column(db.String(100), unique=True, nullable=False)
    title = db.Column(db.String(200))
    description = db.Column(db.String(300))
    keywords = db.Column(db.String(300))
    og_image = db.Column(db.String(500))
    canonical = db.Column(db.String(300))


class ActivityLog(db.Model):
    __tablename__ = 'activity_logs'
    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('admin_users.id'))
    admin_name = db.Column(db.String(100))
    action = db.Column(db.String(50), nullable=False)
    entity = db.Column(db.String(50))
    entity_id = db.Column(db.Integer)
    details = db.Column(db.Text)
    ip_address = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=utcnow)

    admin = db.relationship('AdminUser', backref='activities')
