import os
from functools import wraps
from flask import Blueprint, render_template, redirect, flash, request, url_for
from app.forms import TrekForm
from app import db
from flask_login import current_user, login_required
from app.models.trek import Trek
from app.models.staff import Staff
from app.models.booking import Booking
from app.models.user import User

admin_bp = Blueprint('admin', __name__)

def admin_login_required(func):
    @wraps(func)

    def decorated_view(*args, **kwargs):
        if not current_user.is_authenticated:
            return login_required(func)(*args, **kwargs)
        
        if not current_user.role == "admin":
            flash("You don't have permission to access this page", category="error")
            return redirect(url_for("home"))
        
        return func(*args, **kwargs)
        
    return decorated_view

@admin_bp.route("/admin/dashboard")
@admin_login_required
def admin_dashboard():
    total_treks = Trek.query.count()
    total_staff = Staff.query.count()
    total_trekkers = User.query.filter_by(role='trekker').count()
    total_bookings = Booking.query.count()

    trek_status_data = {
                        "Open": Trek.query.filter_by(status="Open").count(),
                        "Closed": Trek.query.filter_by(status="Closed").count(),
                        "Ongoing": Trek.query.filter_by(status="Ongoing").count(),
                        "Completed": Trek.query.filter_by(status="Completed").count()
                    }

    return render_template('admin/dashboard.html',
                                total_treks=total_treks,
                                total_staff=total_staff,
                                total_trekkers=total_trekkers,
                                total_bookings=total_bookings,
                                trek_status_data=trek_status_data)

# TREK ROUTES

@admin_bp.route("/admin/manage_treks", methods=['GET', 'POST'])
@admin_login_required
def manage_treks():
    treks = Trek.query.filter(Trek.status != 'Completed').order_by(Trek.start_date.asc()).all()
    query = request.args.get('query', '')

    if query:
        treks = Trek.query.filter(Trek.status != 'Completed',
            Trek.name.ilike(f'%{query}%')
        ).order_by(Trek.start_date.asc()).all()

    return render_template("admin/trek/manage_treks.html",
                           query=query, treks=treks)

@admin_bp.route("/admin/add_trek", methods=['GET', 'POST'])
@admin_login_required
def add_trek():
    form = TrekForm()
    if form.validate_on_submit():
        existing = Trek.query.filter_by(name=form.name.data).first()
        if existing:
            flash("Trek already exists!", category="error")
            return render_template("admin/trek/add_trek.html", form=form)

        image = form.image.data
        if image:
            image.save("app/static/images/" + image.filename)
            image_name = image.filename
        else:
            image_name = None

        trek = Trek(
            name=form.name.data,
            location=form.location.data,
            difficulty=form.difficulty.data,
            duration=form.duration.data,
            slots=form.slots.data,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            image= image_name
        )

        db.session.add(trek)
        db.session.commit()

        flash(f'Trek "{trek.name}" added successfully!', category="success")
        return redirect(url_for("admin.manage_treks"))
    return render_template("admin/trek/add_trek.html", form=form)

@admin_bp.route("/admin/trek_details/<int:trek_id>", methods=['GET', 'POST'])
@admin_login_required
def trek_details(trek_id):
    trek = Trek.query.get_or_404(trek_id)
    participants = trek.bookings.filter(Booking.status.in_(["Booked", "Completed"])).count()
    return render_template('admin/trek/trek_details.html', trek=trek, participants=participants)

@admin_bp.route("/admin/edit_trek/<int:id>", methods=['GET', 'POST'])
@admin_login_required
def edit_trek(id):
    trek = Trek.query.get_or_404(id)
    form = TrekForm(obj=trek)
    if form.validate_on_submit():
        existing = Trek.query.filter(Trek.name == form.name.data, Trek.id != id).first()

        if existing:
            flash("Trek already exists!", category="error")
            return render_template("admin/trek/edit_trek.html", form=form)

        new_image = request.files.get("image")

        if new_image and new_image.filename != "":

            # Delete old image
            if trek.image:
                path = "app/static/images/" + trek.image
                if os.path.exists(path):
                    os.remove(path)

            # Save new image
            new_image.save("app/static/images/" + new_image.filename)
            trek.image = new_image.filename

            
        trek.name = form.name.data
        trek.location = form.location.data
        trek.difficulty = form.difficulty.data
        trek.duration = form.duration.data
        trek.slots = form.slots.data
        trek.start_date = form.start_date.data
        trek.end_date = form.end_date.data

        db.session.commit()

        flash(f'Trek "{trek.name}" updated successfully!', category="success")
        return redirect(url_for("admin.trek_details", trek_id=trek.id))
    return render_template("admin/trek/edit_trek.html", form=form, trek=trek)

@admin_bp.route("/admin/delete_trek/<int:id>", methods=['POST'])
@admin_login_required
def delete_trek(id):
    trek = Trek.query.get_or_404(id)

    if trek.image:
        path = "app/static/images/" + trek.image

        if os.path.exists(path):
            os.remove(path)

    db.session.delete(trek)
    db.session.commit()
    flash(f'Trek "{trek.name}" deleted successfully!', category="error")
    return redirect(url_for("admin.manage_treks"))

# STAFF ROUTES

@admin_bp.route("/admin/manage_staff/<string:status>", methods=['GET', 'POST'])
@admin_login_required
def manage_staff(status):
    pending_staff_list = Staff.query.filter_by(status='Pending').all()
    approved_staff_list = Staff.query.filter_by(status='Approved').all()
    rejected_staff_list = Staff.query.filter_by(status='Rejected').all()

    query = request.args.get('query', '')

    if query:
        if status=='Approved':
            approved_staff_list = Staff.query.filter(Staff.status=='Approved',
                Staff.full_name.ilike(f'%{query}%')
            ).all()
        elif status=='Rejected':
            rejected_staff_list = Staff.query.filter(Staff.status=='Rejected',
                Staff.full_name.ilike(f'%{query}%')
            ).all()
        else:
            pending_staff_list = Staff.query.filter(Staff.status=='Pending',
                Staff.full_name.ilike(f'%{query}%')
            ).all()

    return render_template("admin/manage_staff.html",
                           query=query, pending_staff_list=pending_staff_list,
                           approved_staff_list=approved_staff_list,
                           rejected_staff_list=rejected_staff_list, status=status)

@admin_bp.route("/admin/staff/<int:staff_id>/staff_status/<string:status>", methods=['GET', 'POST'])
@admin_login_required
def change_staff_status(staff_id, status):
    staff = Staff.query.get_or_404(staff_id)
    staff.status = status
    db.session.commit()
    flash(f'Staff request status changed successfully!', category="success")
    return redirect(url_for("admin.manage_staff", status=status))

@admin_bp.route('/admin/trek/<int:trek_id>/assign_staff', methods=['GET'])
@admin_login_required
def assign_staff(trek_id):
    trek = Trek.query.get_or_404(trek_id)
    approved_staff = Staff.query.filter_by(status='Approved').all()
    query = request.args.get('query', '')
    
    if query:
        approved_staff = Staff.query.filter(Staff.status=='Approved',
            Staff.full_name.ilike(f'%{query}%')
        ).all()

    return render_template('admin/trek/assign_staff.html', trek=trek, approved_staff=approved_staff, query=query)

@admin_bp.route('/admin/trek/<int:trek_id>/confirm_assign_staff/<int:staff_id>', methods=['POST'])
@admin_login_required
def confirm_assign_staff(trek_id, staff_id):

    trek = Trek.query.get_or_404(trek_id)
    staff = Staff.query.get_or_404(staff_id)

    trek.assigned_staff_id = staff_id

    db.session.commit()

    flash(f'Staff "{staff.full_name}" assigned to "{trek.name}" successfully!', category='success')

    return redirect(url_for('admin.trek_details', trek_id=trek_id))

@admin_bp.route('/admin/trek/<int:trek_id>/confirm_remove_staff/<int:staff_id>', methods=['POST'])
@admin_login_required
def confirm_remove_staff(trek_id, staff_id):

    trek = Trek.query.get_or_404(trek_id)
    staff = Staff.query.get_or_404(staff_id)

    trek.assigned_staff_id = None

    db.session.commit()

    flash(f'Staff "{staff.full_name}" removed from "{trek.name}" successfully!', category='error')

    return redirect(url_for('admin.assign_staff', trek_id=trek_id))

# BOOKING ROUTES

@admin_bp.route('/admin/all_bookings', methods=['GET'])
@admin_login_required
def all_bookings():
    all_bookings = Booking.query.order_by(Booking.booking_date.desc()).all()
    return render_template('admin/all_bookings.html', all_bookings=all_bookings)

# TREKKING ROUTES

@admin_bp.route('/admin/trekking_history', methods=['GET'])
@admin_login_required
def trekking_history():
    trekking_history = Trek.query.filter_by(status='Completed').order_by(Trek.start_date.desc()).all()
    query = request.args.get('query', '')

    if query:
        trekking_history = Trek.query.filter(Trek.status == 'Completed',
            Trek.name.ilike(f'%{query}%')
        ).order_by(Trek.start_date.desc()).all()

    return render_template('admin/trekking_history.html', trekking_history=trekking_history, query=query)


# USER ROUTES

@admin_bp.route("/admin/manage_users", methods=['GET', 'POST'])
@admin_login_required
def manage_users():
    users = User.query.all()
    query = request.args.get('query', '')

    if query:
        users = User.query.filter(
            User.full_name.ilike(f'%{query}%')
        ).all()

    return render_template("admin/manage_users.html",
                           query=query, users=users)


@admin_bp.route("/admin/user/<int:user_id>/user_status/<string:status>", methods=['GET', 'POST'])
@admin_login_required
def change_user_status(user_id, status):
    user = User.query.get_or_404(user_id)
    user.status = status
    db.session.commit()
    flash(f'User status changed successfully!', category="success")
    return redirect(url_for("admin.manage_users"))