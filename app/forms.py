from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField, FileRequired
from wtforms import StringField, PasswordField, DateField, SubmitField, SelectField, IntegerField
from wtforms.validators import Email, Length, EqualTo, DataRequired


class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()], render_kw={"autofocus": True})
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    full_name = StringField('Full Name', validators=[DataRequired()])
    contact = StringField('Contact Number', validators=[Length(min=10, max=15)])
    role = SelectField("Register As", choices=[("trekker", "Trekker"), ("staff", "Staff")], validators=[DataRequired()])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()], render_kw={"autofocus": True})
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    submit = SubmitField('Login')

class UserDetailsForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()], render_kw={"autofocus": True})
    full_name = StringField('Full Name', validators=[DataRequired()])
    contact = StringField('Contact Number', validators=[Length(min=10, max=15)])
    submit = SubmitField('Submit')

class ChangePasswordForm(FlaskForm):
    password = PasswordField('New Password', validators=[DataRequired(), Length(min=8)], render_kw={"autofocus": True})
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Submit')


class TrekForm(FlaskForm):
    name = StringField('Trek Name', validators=[DataRequired()], render_kw={"autofocus": True})
    location = StringField('Location', validators=[DataRequired()])
    difficulty = SelectField('Difficulty', choices=[("Easy", "Easy"), ("Moderate", "Moderate"), ("Hard", "Hard")], validators=[DataRequired()])
    duration = StringField('Duration (Days)', validators=[DataRequired()])
    slots = IntegerField('Available Slots', validators=[DataRequired()])
    start_date = DateField('Start Date', validators=[DataRequired()])
    end_date = DateField('End Date', validators=[DataRequired()])
    image = FileField('Trek Image', validators=[FileAllowed(["jpg", "jpeg", "png"], "Only 'jpg', 'jpeg', and 'png' files are allowed!")])
    submit = SubmitField('Save')
