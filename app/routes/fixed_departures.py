from flask import Blueprint, render_template
from app.models import FixedDeparture
from datetime import datetime

fixed_departures_bp = Blueprint('fixed_departures', __name__)


@fixed_departures_bp.route('/')
def list_departures():
    departures = FixedDeparture.query.filter(
        FixedDeparture.departure_date >= datetime.utcnow().date()
    ).order_by(FixedDeparture.departure_date).all()
    return render_template('fixed_departures/list.html', departures=departures)
