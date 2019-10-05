from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, RadioField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from lumirandom.models import User


class RegistrationForm(FlaskForm):
    f_name = StringField('First Name', validators=[DataRequired(), Length(max=20)])
    l_name = StringField('Last Name', validators=[DataRequired(), Length(max=20)])
    account_id = StringField('ID Number', validators=[DataRequired(), Length(min=2, max=20)])
    role = RadioField('Role', choices=[('student', 'Student'), ('professor', 'Professor')])
    password = PasswordField('Password', validators=[DataRequired()])
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