from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, FloatField, widgets, SelectMultipleField, IntegerField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, InputRequired
from ordermenu.models import User, Food, Tags
from ordermenu import app


class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()
    
    
class RegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')


class LoginForm(FlaskForm):
    tryna_user = StringField('Username',
                        validators=[DataRequired()]) #CHANGE THIS
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class UpdateAccountForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')


class TagFilterForm(FlaskForm):
    with app.app_context():
        tags = Tags.query.all()
        retags = []
        for each in tags:
            if each.tagname not in retags:
                retags.append(each.tagname)
    foodtag = MultiCheckboxField('Label', choices=retags)
    submit = SubmitField('Filter')

class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Post')


class RequestResetForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('There is no account with that email. You must register first.')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')

class AddfoodForm(FlaskForm):
    name = StringField('Food Name',
                           validators=[DataRequired(), Length(min=1, max=40)])
    price = FloatField('Price (RM)', validators=[InputRequired()])
    picture = FileField('Add Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    smoldescription = StringField('Description')   
    description = StringField('Details',validators=[InputRequired()])
    
    with app.app_context():
        tags = Tags.query.all()
        retags = []
        for each in tags:
            if each.tagname not in retags:
                retags.append(each.tagname)
    foodtag = MultiCheckboxField('Label', choices=retags)
    submit = SubmitField('Add Food')
    
    def validate_name(self, name):
        food = Food.query.filter_by(name=name.data).first()
        if food:
            raise ValidationError('That food name is taken. Please give it a weirder name.')
        
        
        
class ConfirmationOrderForm(FlaskForm):
    tableno = IntegerField("Table Number", validators = [DataRequired()])
    submit = SubmitField('Confirm Order')
    
    

