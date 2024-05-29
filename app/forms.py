from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField, PasswordField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError
from app.models import Group, User, Status

class TicketForm_edit(FlaskForm):
    note = TextAreaField('Note', validators=[DataRequired()])
    status = SelectField('Status', choices=[(status.name, status.value) for status in Status], validators=[DataRequired()])
    submit = SubmitField('Create Ticket')

class TicketForm_create(FlaskForm):
    note = TextAreaField('Note', validators=[DataRequired()])
    assigned_user_id = SelectField('Assigned User', coerce=int, choices=[(0, 'None')])
    assigned_group_id = SelectField('Assigned Group', coerce=int, choices=[(0, 'None')])
    submit = SubmitField('Create Ticket')

class GroupForm(FlaskForm):
    name = TextAreaField('Name', validators=[DataRequired()])
    submit = SubmitField('Create Ticket')

class UserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    group = SelectField('Group', coerce=int, choices=[])
    submit = SubmitField('Submit')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Please use a different email address.')