from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models import Enquiry, Customer, Package
from app.extensions import db
from datetime import datetime
import random
import string

enquiries_bp = Blueprint('enquiries', __name__)


def generate_ref():
    return 'DN' + ''.join(random.choices(string.digits, k=8))


@enquiries_bp.route('/plan', methods=['GET', 'POST'])
def plan_trip():
    packages = Package.query.filter_by(status='published').order_by(Package.title).all()
    success = False
    ref_id = None
    enquiry_data = None

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        phone = request.form.get('phone', '').strip()
        email = request.form.get('email', '').strip()
        destination = request.form.get('destination', '').strip()
        package_id = request.form.get('package_id', type=int)
        travel_date_str = request.form.get('travel_date', '')
        return_date_str = request.form.get('return_date', '')
        travelers = request.form.get('travelers', 1, type=int) or 1
        adults = request.form.get('adults', 1, type=int) or 1
        children = request.form.get('children', 0, type=int) or 0
        travel_type = request.form.get('travel_type', '')
        pickup = request.form.get('pickup_location', '')
        accommodation = request.form.get('accommodation_pref', '')
        transportation = request.form.get('transportation_pref', '')
        message = request.form.get('message', '')

        errors = []
        if not name:
            errors.append('Name is required.')
        if not phone or len(phone) < 7:
            errors.append('Valid phone number is required.')

        if errors:
            return render_template('enquiry.html', packages=packages, errors=errors, form=request.form)

        # Find or create customer
        customer = Customer.query.filter_by(phone=phone).first()
        if not customer:
            customer = Customer(name=name, phone=phone, email=email)
            db.session.add(customer)
            db.session.flush()
        else:
            customer.name = name
            if email:
                customer.email = email

        package_title = None
        if package_id:
            pkg = Package.query.get(package_id)
            if pkg:
                package_title = pkg.title

        travel_date = None
        return_date = None
        try:
            if travel_date_str:
                travel_date = datetime.strptime(travel_date_str, '%Y-%m-%d').date()
            if return_date_str:
                return_date = datetime.strptime(return_date_str, '%Y-%m-%d').date()
        except ValueError:
            pass

        ref_id = generate_ref()
        while Enquiry.query.filter_by(reference_id=ref_id).first():
            ref_id = generate_ref()

        enquiry = Enquiry(
            reference_id=ref_id,
            customer_id=customer.id,
            name=name,
            phone=phone,
            email=email,
            destination=destination,
            package_id=package_id,
            package_title=package_title,
            travel_date=travel_date,
            return_date=return_date,
            travelers=travelers,
            adults=adults,
            children=children,
            travel_type=travel_type,
            pickup_location=pickup,
            accommodation_pref=accommodation,
            transportation_pref=transportation,
            message=message,
            status='New'
        )
        db.session.add(enquiry)
        db.session.commit()
        success = True
        enquiry_data = enquiry

    return render_template('enquiry.html',
                           packages=packages,
                           success=success,
                           ref_id=ref_id,
                           enquiry=enquiry_data)
