from flask import Blueprint, render_template, redirect, flash, url_for
from app import db
from app.forms import RegisterForm, LoginForm
from flask_login import current_user, login_user, login_required, logout_user
from app.models.user import User
from app.models.staff import Staff

auth_bp = Blueprint('auth', __name__)

@auth_bp.route("/register", methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if current_user.is_authenticated:
        flash("You are already registered!", category="success")
        if current_user.role == "admin":
            return redirect(url_for("admin.admin_dashboard"))
        elif current_user.role == "staff":
            return redirect(url_for("staff.staff_dashboard"))
        else:
            return redirect(url_for("trekker.trekker_dashboard"))
    if form.validate_on_submit():

        # Check if username already exists
        existing_user = User.query.filter_by(email=form.email.data).first()

        if existing_user:

            flash("Email already exists! Please Login.", category="error")
            return redirect(url_for('auth.register'))
        
        user = User(
                    email=form.email.data,
                    full_name=form.full_name.data,
                    contact=form.contact.data,
                    role=form.role.data
                )
        user.set_password(form.password.data)
        db.session.add(user)

        user = User.query.filter_by(email=form.email.data).first()

        if form.role.data == "staff":
            staff = Staff(
                        email=form.email.data,
                        full_name=form.full_name.data,
                        contact=form.contact.data,
                        user_id=user.id
                    )
            db.session.add(staff)

        db.session.commit()
        flash(f'"{user.role}" registration is successful!', category="success")
        return redirect(url_for('auth.login'))
    return render_template("register.html", form=form)

@auth_bp.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if current_user.is_authenticated:
        flash("You are already logged in!", category="success")
        if current_user.role == "admin":
            return redirect(url_for("admin.admin_dashboard"))
        elif current_user.role == "staff":
            return redirect(url_for("staff.staff_dashboard"))
        else:
            return redirect(url_for("trekker.trekker_dashboard"))

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data) and user.status == "Active":
            login_user(user)
            if user.role == "admin":
                flash("Admin logged in successfully!", category="success")
                return redirect(url_for("admin.admin_dashboard"))
            elif user.role == "staff":
                staff = Staff.query.filter_by(user_id=user.id).first()
                if staff and staff.status == "Approved":
                    flash("Staff logged in successfully!", category="success")
                    return redirect(url_for('staff.staff_dashboard'))
                elif staff and staff.status == "Rejected":
                    logout_user()
                    flash('Your staff account is rejected by admin!', category="error")
                    return redirect(url_for('auth.login'))
                else:
                    logout_user()
                    flash('Your staff account is pending approval. Please wait for admin approval!', category="error")
                    return redirect(url_for('auth.login'))
            else:
                flash("Trekker logged in successfully!", category="success")
                return redirect(url_for('trekker.trekker_dashboard'))
        elif user and user.check_password(form.password.data) and user.status == "Blacklisted":
            flash('Your account is blacklisted by admin!', category="error")
            return redirect(url_for('auth.login'))
        else:
            flash("Invalid Email or Password!", category="error")
    return render_template("login.html", form=form)

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logout successful!", category="success")
    return redirect(url_for('auth.login'))

