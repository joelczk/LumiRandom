from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, RadioField, TextAreaField
from wtforms.widgets import ListWidget, CheckboxInput
from wtforms.validators import DataRequired, Length, Email, EqualTo, Optional, ValidationError
from lumirandom.models import User
from flask_login import current_user
from lumirandom import bcrypt


class RegistrationForm(FlaskForm):
    f_name = StringField('First Name', validators=[DataRequired(), Length(max=20)])
    l_name = StringField('Last Name', validators=[DataRequired(), Length(max=20)])
    account_id = StringField('ID Number', validators=[DataRequired(), Length(min=2, max=20)])
    role = RadioField('Role', choices=[('student', 'Student'), ('professor', 'Professor')])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, max=20)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_account_id(self, account_id):
        user = User.query.filter_by(account_id=account_id.data).first()
        if user:
            raise ValidationError('That account already exists. Please log in.')


class LoginForm(FlaskForm):
    account_id = StringField('Account ID', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class UpdateAccountForm(FlaskForm):
    picture = FileField('Update Profile Picture', validators=[Optional(), FileAllowed(['jpg', 'png'])])
    cur_password = PasswordField('Current Password')
    new_password = PasswordField('New Password', validators=[Optional(), Length(min=6, max=20)])
    confirm_password = PasswordField('Confirm Password', validators=[Optional(), EqualTo('new_password', message='Password must match.')])
    submit = SubmitField('Update')

    def validate_cur_password(self, cur_password):
        if cur_password.data and not bcrypt.check_password_hash(current_user.password, cur_password.data):
            raise ValidationError('Current password is wrong.')