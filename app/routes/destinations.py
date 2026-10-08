from flask import Blueprint, render_template
from app.models import Destination, Package

destinations_bp = Blueprint('destinations', __name__)


@destinations_bp.route('/')
def list_destinations():
    destinations = Destination.query.filter_by(status='published').order_by(Destination.sort_order, Destination.name).all()
    return render_template('destinations/list.html', destinations=destinations)


@destinations_bp.route('/<slug>')
def destination_detail(slug):
    destination = Destination.query.filter_by(slug=slug, status='published').first_or_404()
    packages = Package.query.filter(
        Package.status == 'published',
        Package.destination.ilike(f'%{destination.name.split("/")[0].strip()}%')
    ).limit(6).all()
    related = Destination.query.filter(
        Destination.status == 'published',
        Destination.id != destination.id
    ).order_by(Destination.sort_order).limit(4).all()
    return render_template('destinations/detail.html',
                           destination=destination,
                           packages=packages,
                           related=related)
