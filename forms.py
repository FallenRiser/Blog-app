from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError, TextAreaField
from wtforms.validators import DataRequired, EqualTo, Length
from wtforms.widgets import TextArea
from flask_ckeditor import CKEditorField


class UserForm(FlaskForm):
    name = StringField("Enter your name here", validators=[DataRequired()])
    username = StringField("Enter your username here", validators=[DataRequired()])
    email = StringField("Enter your email here", validators=[DataRequired()])
    fav_color = StringField("Enter your Favourite color")
    user_bio = TextAreaField("Bio")
    password_hash = PasswordField("Enter your password",validators=[DataRequired(), EqualTo('password_hash2',message='Passwords must match.')])
    password_hash2 = PasswordField("Enter your password again",validators=[DataRequired()])
    submit =  SubmitField("Submit")

class test(FlaskForm):
    name = StringField("Enter your name here", validators=[DataRequired()])
    submit =  SubmitField("Submit")


class SearchForm(FlaskForm):
    searched = StringField("Searched", validators=[DataRequired()])
    submit =  SubmitField("Submit")


#Posts Form
class PostForm(FlaskForm):
    title = StringField("Enter your title here", validators=[DataRequired()])
    #content = StringField("Enter your content here", validators=[DataRequired()],widget=TextArea())
    content = CKEditorField("Content", validators=[DataRequired()])
    author =  StringField("Enter your author here")
    slug = StringField("Enter your slug here", validators=[DataRequired()])
    submit = SubmitField("Submit")


#Login Form
class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Submit")