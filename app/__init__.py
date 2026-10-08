import os
from flask import Flask
from config import config
from app.extensions import db, login_manager, migrate, csrf, limiter


def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
        # Vercel sets VERCEL=1 — use production config
        if os.environ.get('VERCEL') or os.environ.get('VERCEL_ENV'):
            config_name = 'production'

    # Vercel is read-only except /tmp — avoid creating ./instance
    instance_path = None
    if os.environ.get('VERCEL') or os.environ.get('VERCEL_ENV'):
        instance_path = '/tmp/darshan_instance'

    app = Flask(__name__,
                template_folder='templates',
                static_folder='static',
                instance_path=instance_path,
                instance_relative_config=False)
    app.config.from_object(config.get(config_name, config['default']))

    # Ensure upload folder exists (safe on read-only FS)
    try:
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    except OSError:
        pass
    if instance_path:
        try:
            os.makedirs(instance_path, exist_ok=True)
        except OSError:
            pass

    # Init extensions
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    limiter.init_app(app)

    # Register blueprints
    from app.routes.main import main_bp
    from app.routes.packages import packages_bp
    from app.routes.destinations import destinations_bp
    from app.routes.services import services_bp
    from app.routes.enquiries import enquiries_bp
    from app.routes.vehicles import vehicles_bp
    from app.routes.blog import blog_bp
    from app.routes.fixed_departures import fixed_departures_bp
    from app.routes.admin import admin_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(packages_bp, url_prefix='/packages')
    app.register_blueprint(destinations_bp, url_prefix='/destinations')
    app.register_blueprint(services_bp, url_prefix='/services')
    app.register_blueprint(enquiries_bp, url_prefix='/enquiries')
    app.register_blueprint(vehicles_bp, url_prefix='/vehicles')
    app.register_blueprint(blog_bp, url_prefix='/blog')
    app.register_blueprint(fixed_departures_bp, url_prefix='/fixed-departures')
    app.register_blueprint(admin_bp, url_prefix='/admin')

    # Context processors
    @app.context_processor
    def inject_globals():
        from app.models import SiteSetting
        from datetime import datetime
        settings = {}
        try:
            for s in SiteSetting.query.all():
                settings[s.key] = s.value
        except Exception:
            pass
        return {
            'site_settings': settings,
            'business_name': settings.get('business_name', 'Darshan Nepal Travel & Tours'),
            'business_address': settings.get('address', 'Urlabari, Koshi Province 56604, Nepal'),
            'business_phone': settings.get('phone', '9801708396'),
            'business_phones': settings.get('phones', '9801708396,9801708397,9841110276').split(','),
            'google_rating': settings.get('google_rating', '4.8'),
            'review_count': settings.get('review_count', '27'),
            'announcement': settings.get('announcement', ''),
            'current_year': datetime.now().year,
            'facebook_url': settings.get('facebook', 'https://www.facebook.com/'),
            'instagram_url': settings.get('instagram', 'https://www.instagram.com/'),
            'logo_url': settings.get('logo_url', ''),
            'favicon_url': settings.get('favicon_url', ''),
        }

    # Error handlers
    @app.errorhandler(404)
    def not_found(e):
        from flask import render_template
        return render_template('errors/404.html'), 404

    @app.errorhandler(403)
    def forbidden(e):
        from flask import render_template
        return render_template('errors/403.html'), 403

    @app.errorhandler(500)
    def server_error(e):
        from flask import render_template
        return render_template('errors/500.html'), 500

    # Create tables & seed if needed (skip hard fail on serverless cold start)
    with app.app_context():
        try:
            db.create_all()
            from app.utils.seed import seed_if_empty
            seed_if_empty()
        except Exception as e:
            app.logger.warning('DB init deferred: %s', e)

    return app
