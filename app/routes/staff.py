from functools import wraps
from flask import Blueprint, render_template, redirect, flash, request, url_for, abort
from app import db
from flask_login import current_user, login_required
from app.forms import UserDetailsForm, ChangePasswordForm
from app.models.staff import Staff
from app.models.trek import Trek
from app.models.booking import Booking

staff_bp = Blueprint('staff', __name__)

def staff_login_required(func):
    @wraps(func)

    def decorated_view(*args, **kwargs):
        if not current_user.is_authenticated:
            return login_required(func)(*args, **kwargs)
        
        if not current_user.role == "staff":
            flash("You don't have permission to access this page", category="error")
            return redirect(url_for("home"))
        
        return func(*args, **kwargs)
        
    return decorated_view

@staff_bp.route("/staff/dashboard")
@staff_login_required
def staff_dashboard():
    staff = Staff.query.filter_by(user_id=current_user.id).first()
    total_assigned_treks = staff.assigned_treks.count()
    completed_treks = staff.assigned_treks.filter_by(status="Completed").count()
    upcoming_treks = staff.assigned_treks.filter(Trek.status != "Completed").order_by(Trek.start_date.asc()).all()

    trek_bookings = {}
    total_participants = 0

    for trek in upcoming_treks:
        booking_count = trek.bookings.filter_by(status='Booked').count()

        trek_bookings[trek.name] = booking_count
        
        total_participants += booking_count
    
    return render_template('staff/dashboard.html',
                            total_assigned_treks=total_assigned_treks,
                            completed_treks=completed_treks,
                            upcoming_treks=upcoming_treks,
                            trek_bookings=trek_bookings,
                            total_participants=total_participants)


@staff_bp.route("/staff/assigned_treks")
@staff_login_required
def assigned_treks():
    staff = Staff.query.filter_by(user_id=current_user.id).first()
    assigned_treks = staff.assigned_treks.filter(Trek.status!='Completed').order_by(Trek.start_date.asc()).all()
    query = request.args.get('query', '')
    
    if query:
        assigned_treks = Trek.query.filter(Trek.status!='Completed',
            Trek.name.ilike(f'%{query}%')
        ).order_by(Trek.start_date.asc()).all()
    
    return render_template('staff/assigned_treks.html', query=query, assigned_treks=assigned_treks)

@staff_bp.route("/staff/trek_details/<int:trek_id>", methods=['GET', 'POST'])
@staff_login_required
def trek_details(trek_id):
    trek = Trek.query.get_or_404(trek_id)
    staff = Staff.query.filter_by(user_id=current_user.id).first()

    if trek.assigned_staff_id != staff.id:
        flash("You don't have permission to view this trek!", category="error")
        return redirect(url_for("staff.assigned_treks"))

    bookings = trek.bookings.filter(Booking.status.in_(["Booked", "Completed"])).order_by(Booking.booking_date.desc()).all()
    
    return render_template('staff/trek_details.html', trek=trek, bookings=bookings)


@staff_bp.route('/staff/update_slots/<int:trek_id>', methods=['POST'])
@staff_login_required
def update_slots(trek_id):
    trek = Trek.query.get_or_404(trek_id)
    staff = Staff.query.filter_by(user_id=current_user.id).first()

    if trek.assigned_staff_id != staff.id:
        flash("You don't have permission to update this trek!", category="error")
        return redirect(url_for("staff.assigned_treks"))

    if trek.status == 'Completed':
        flash("Cannot update slots for completed trek!", category="error")
        return redirect(url_for("staff.trek_deatils", trek_id=trek_id))
    
    new_slots = request.form.get('slots')

    trek.slots = new_slots

    db.session.commit()

    flash("Slots updated successfully!", category="success")

    return redirect(url_for("staff.trek_details", trek_id=trek.id))
    
    
@staff_bp.route("/staff/trek/<int:trek_id>/change_status", methods=['POST'])
@staff_login_required
def change_trek_status(trek_id):
    trek = Trek.query.get_or_404(trek_id)
    staff = Staff.query.filter_by(user_id=current_user.id).first()

    if trek.assigned_staff_id != staff.id:
        flash("You don't have permission to update this trek!", category="error")
        return redirect(url_for("staff.trek_deatils", trek_id=trek_id))
    
    new_status = request.form.get("status")

    if trek.status == 'Completed':
        flash("Cannot change status for completed trek!", category="error")
        return redirect(url_for("staff.trekking_history"))

    if new_status == 'Completed':
        trek.slots = 0
        bookings = trek.bookings.filter_by(status='Booked').all()
        for booking in bookings:
            booking.status = 'Completed'

    trek.status = new_status

    db.session.commit()
    flash("Trek status updated successfully!", category="success")
    return redirect(url_for("staff.trek_details", trek_id=trek.id))


@staff_bp.route("/staff/trekking_history", methods=['GET'])
@staff_login_required
def trekking_history():
    staff = Staff.query.filter_by(user_id=current_user.id).first()
    trekking_history = staff.assigned_treks.filter_by(status='Completed').order_by(Trek.start_date.desc()).all()
    query = request.args.get('query', '')
        
    if query:
        trekking_history = Trek.query.filter(Trek.status == 'Completed',
            Trek.name.ilike(f'%{query}%')
        ).order_by(Trek.start_date.desc()).all()
    
    return render_template('staff/trekking_history.html', trekking_history=trekking_history, query=query)


@staff_bp.route("/staff/my_profile", methods=['GET'])
@staff_login_required
def my_profile():
    return render_template("staff/my_profile.html")


@staff_bp.route("/staff/update_profile", methods=['GET', 'POST'])
@staff_login_required
def update_profile():
    staff = current_user
    form = UserDetailsForm(obj=staff)

    if form.validate_on_submit():
        staff.email = form.email.data
        staff.full_name = form.full_name.data
        staff.contact = form.contact.data

        db.session.commit()
        flash("Your details updated successfully!", category="success")
        return redirect(url_for("staff.my_profile"))

    return render_template("staff/update_profile.html",
                           form=form,
                           staff=staff)


@staff_bp.route("/staff/change_password", methods=['GET', 'POST'])
@staff_login_required
def change_password():
    staff = current_user
    form = ChangePasswordForm(obj=staff)

    if form.validate_on_submit():
        staff.set_password(form.password.data)

        db.session.commit()
        flash("Your password changed successfully!", category="success")
        return redirect(url_for("staff.my_profile"))

    return render_template("staff/change_password.html",
                           form=form,
                           staff=staff)
