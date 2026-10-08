from flask import Blueprint, render_template, request
from app.models import Vehicle, VehicleEnquiry
from app.extensions import db
from datetime import datetime
import random
import string

vehicles_bp = Blueprint('vehicles', __name__)


def generate_ref():
    return 'VH' + ''.join(random.choices(string.digits, k=8))


@vehicles_bp.route('/')
def list_vehicles():
    vehicles = Vehicle.query.filter_by(status='published').order_by(Vehicle.vehicle_type, Vehicle.name).all()
    return render_template('vehicles.html', vehicles=vehicles, success=False)


@vehicles_bp.route('/enquire', methods=['POST'])
def vehicle_enquire():
    vehicles = Vehicle.query.filter_by(status='published').all()
    name = request.form.get('name', '').strip()
    phone = request.form.get('phone', '').strip()
    email = request.form.get('email', '').strip()
    vehicle_type = request.form.get('vehicle_type', '')
    pickup = request.form.get('pickup', '')
    dropoff = request.form.get('dropoff', '')
    date_str = request.form.get('date', '')
    time = request.form.get('time', '')
    passengers = request.form.get('passengers', type=int)
    special = request.form.get('special_request', '')

    if not name or not phone:
        return render_template('vehicles.html', vehicles=vehicles, error='Name and phone are required.', success=False)

    date_val = None
    try:
        if date_str:
            date_val = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        pass

    ref = generate_ref()
    enq = VehicleEnquiry(
        reference_id=ref,
        name=name,
        phone=phone,
        email=email,
        vehicle_type=vehicle_type,
        pickup=pickup,
        dropoff=dropoff,
        date=date_val,
        time=time,
        passengers=passengers,
        special_request=special,
        status='New'
    )
    db.session.add(enq)
    db.session.commit()
    return render_template('vehicles.html', vehicles=vehicles, success=True, ref_id=ref)
