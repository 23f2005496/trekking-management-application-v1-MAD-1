from flask import Blueprint, render_template, redirect, flash, url_for, request
from app import db
from flask_login import current_user, login_required
from app.forms import UserDetailsForm, ChangePasswordForm
from app.models.trek import Trek
from app.models.booking import Booking

trekker_bp = Blueprint('trekker', __name__)


@trekker_bp.route("/trekker/dashboard")
@login_required
def trekker_dashboard():
    total_bookings = Booking.query.filter(Booking.user_id == current_user.id).count()
    cancelled_bookings = Booking.query.filter(Booking.user_id == current_user.id, Booking.status == "Cancelled").count()
    completed_treks = Trek.query.join(Booking).filter(
                                                    Booking.user_id == current_user.id,
                                                    Booking.status == "Completed",
                                                    Trek.id == Booking.trek_id,
                                                    Trek.status == "Completed"
                                                ).count()
    upcoming_treks = Trek.query.join(Booking).filter(
                                                    Booking.user_id == current_user.id,
                                                    Booking.status == "Booked",
                                                    Trek.id == Booking.trek_id,
                                                    Trek.status != "Completed"
                                                ).order_by(Trek.start_date.asc()).all()
    

    return render_template("trekker/dashboard.html",
                           total_bookings=total_bookings,
                           cancelled_bookings=cancelled_bookings,
                           completed_treks=completed_treks,
                           upcoming_treks=upcoming_treks)


@trekker_bp.route("/trekker/view_treks", methods=['GET', 'POST'])
@login_required
def view_treks():
    treks = Trek.query
    location = request.args.get('location', '')
    difficulty = request.args.get('difficulty', '')

    if location:
        treks = treks.filter(
            Trek.location.ilike(f"%{location}%")
        )

    if difficulty:
        treks = treks.filter_by(
            difficulty=difficulty
        )

    treks = treks.order_by(Trek.start_date.desc()).all()

    return render_template('trekker/view_treks.html',
                                treks=treks,
                                location=location,
                                difficulty=difficulty)

@trekker_bp.route("/trekker/trek_details/<int:trek_id>", methods=['GET', 'POST'])
@login_required
def trek_details(trek_id):
    trek = Trek.query.get_or_404(trek_id)
    booking = Booking.query.filter_by(user_id=current_user.id, trek_id=trek.id).order_by(Booking.booking_date.desc()).first()

    return render_template('trekker/trek_details.html', trek=trek, booking=booking)

@trekker_bp.route("/trekker/book_trek/<int:trek_id>", methods=['GET', 'POST'])
@login_required
def book_trek(trek_id):

    trek = Trek.query.get_or_404(trek_id)

    existing = Booking.query.filter_by(user_id=current_user.id, status='Booked', trek_id=trek.id).first()

    if existing:

        flash("You have already booked this trek!", category="success")
        return redirect(url_for('trekker.trek_details', trek_id=trek.id))

    if trek.status != 'Open':
        flash("Booking closed!", category="error")
        return redirect(url_for('trekker.trek_details', trek_id=trek.id))

    if trek.slots <= 0:
        flash("No slots available!", category="error")
        return redirect(url_for('trekker.trek_details', trek_id=trek.id))

    
    booking = Booking(status="Booked", user_id=current_user.id, trek_id=trek.id)

    trek.slots -= 1

    db.session.add(booking)
    db.session.commit()
    
    flash("Trek booked successfully!", category="success")
    return redirect(url_for('trekker.trek_details', trek_id=trek.id))


@trekker_bp.route("/trekker/cancel_booking/<int:booking_id>", methods=['POST'])
@login_required
def cancel_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)

    if booking.user_id != current_user.id:
        flash("Unauthorized action!", category="error")
        return redirect(url_for('trekker.my_bookings'))

    trek = Trek.query.get(booking.trek_id)

    if trek.status == 'Completed':
        flash("Cannot cancel booking for completed trek!", category="error")
        return redirect(url_for('trekker.my_bookings'))
    
    elif booking.status == 'Cancelled':
        flash("You already cancelled this booking!", category="error")
        return redirect(url_for('trekker.my_bookings'))

    booking.status = "Cancelled"
    trek.slots += 1

    db.session.commit()

    flash("Booking cancelled successfully!", category="success")
    return redirect(url_for('trekker.my_bookings'))


@trekker_bp.route("/trekker/my_bookings", methods=['GET'])
@login_required
def my_bookings():
    my_bookings = Booking.query.filter_by(user_id=current_user.id).order_by(Booking.booking_date.desc()).all()

    return render_template('trekker/my_bookings.html', my_bookings=my_bookings)

@trekker_bp.route("/trekker/trekking_history", methods=['GET'])
@login_required
def trekking_history():
    trekking_history = Trek.query.join(Booking).filter(
                                                    Booking.user_id == current_user.id,
                                                    Trek.id == Booking.trek_id,
                                                    Trek.status == "Completed"
                                                ).order_by(Trek.start_date.desc()).all()
    query = request.args.get('query', '')

    if query:
        trekking_history = Trek.query.join(Booking).filter(
                                                    Booking.user_id == current_user.id,
                                                    Trek.id == Booking.trek_id,
                                                    Trek.status == "Completed",
                                                    Trek.name.ilike(f'%{query}%')
                                                ).order_by(Trek.start_date.desc()).all()

    return render_template('trekker/trekking_history.html', trekking_history=trekking_history, query=query)

@trekker_bp.route("/trekker/my_profile", methods=['GET'])
@login_required
def my_profile():
    return render_template("trekker/my_profile.html")

@trekker_bp.route("/trekker/update_profile", methods=['GET', 'POST'])
@login_required
def update_profile():
    trekker = current_user
    form = UserDetailsForm(obj=trekker)

    if form.validate_on_submit():
        trekker.email = form.email.data
        trekker.full_name = form.full_name.data
        trekker.contact = form.contact.data

        db.session.commit()
        flash("Your details updated successfully!", category="success")
        return redirect(url_for("trekker.my_profile"))

    return render_template("trekker/update_profile.html",
                           form=form,
                           trekker=trekker)

@trekker_bp.route("/trekker/change_password", methods=['GET', 'POST'])
@login_required
def change_password():
    trekker = current_user
    form = ChangePasswordForm(obj=trekker)

    if form.validate_on_submit():
        trekker.set_password(form.password.data)

        db.session.commit()
        flash("Your password changed successfully!", category="success")
        return redirect(url_for("trekker.my_profile"))

    return render_template("trekker/change_password.html",
                           form=form,
                           trekker=trekker)
