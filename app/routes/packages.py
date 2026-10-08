from flask import Blueprint, render_template, request, abort
from app.models import Package, Destination
from app.extensions import db

packages_bp = Blueprint('packages', __name__)


@packages_bp.route('/')
def list_packages():
    destination = request.args.get('destination', '')
    travel_type = request.args.get('type', '')
    q = request.args.get('q', '')
    page = request.args.get('page', 1, type=int)
    per_page = 12

    query = Package.query.filter_by(status='published')
    if destination:
        query = query.filter(Package.destination.ilike(f'%{destination}%'))
    if travel_type:
        query = query.filter(Package.travel_type.ilike(f'%{travel_type}%'))
    if q:
        query = query.filter(db.or_(
            Package.title.ilike(f'%{q}%'),
            Package.short_description.ilike(f'%{q}%'),
            Package.destination.ilike(f'%{q}%')
        ))

    pagination = query.order_by(Package.sort_order, Package.title).paginate(page=page, per_page=per_page, error_out=False)
    destinations = db.session.query(Package.destination).filter(Package.status == 'published').distinct().all()
    destinations = sorted([d[0] for d in destinations if d[0]])
    travel_types = ['Adventure', 'Trekking', 'Pilgrimage', 'Family', 'School', 'Team', 'Sightseeing', 'Cultural']

    return render_template('packages/list.html',
                           packages=pagination.items,
                           pagination=pagination,
                           destinations=destinations,
                           travel_types=travel_types,
                           filters={'destination': destination, 'type': travel_type, 'q': q})


@packages_bp.route('/<slug>')
def package_detail(slug):
    package = Package.query.filter_by(slug=slug, status='published').first_or_404()
    related = Package.query.filter(
        Package.status == 'published',
        Package.id != package.id,
        db.or_(
            Package.travel_type == package.travel_type,
            Package.destination == package.destination
        )
    ).limit(4).all()
    return render_template('packages/detail.html', package=package, related=related)
