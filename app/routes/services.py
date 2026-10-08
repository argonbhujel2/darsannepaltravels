from flask import Blueprint, render_template
from app.models import Service

services_bp = Blueprint('services', __name__)


@services_bp.route('/')
def list_services():
    services = Service.query.filter_by(status='published').order_by(Service.sort_order).all()
    return render_template('services/list.html', services=services)


@services_bp.route('/<slug>')
def service_detail(slug):
    service = Service.query.filter_by(slug=slug, status='published').first_or_404()
    others = Service.query.filter(Service.status == 'published', Service.id != service.id).limit(6).all()
    return render_template('services/detail.html', service=service, others=others)
