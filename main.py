from flask import Flask, render_template,flash,request,url_for,redirect
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError
from wtforms.validators import DataRequired, EqualTo, Length
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms.widgets import TextArea
from flask_login import UserMixin, login_user, login_required, LoginManager, logout_user, current_user
import os



current_dir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+ os.path.join(current_dir,"BlogApp.db")
app.config['SECRET_KEY'] = 'this key is super dooper se bhi Uper VaLa SecRET'


db = SQLAlchemy()
db.init_app(app)
app.app_context().push()
migrate = Migrate(app , db)

#Login Manager Stuff

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


#JSON thing

@app.route('/date')
def date():
    datet = datetime.utcnow()
    return {"Date": datet}

#Posts Model

class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(1000),nullable=False)
    content = db.Column(db.Text,nullable=False)
    author = db.Column(db.String(255))
    date_posted = db.Column(db.DateTime,default = datetime.utcnow())
    slug = db.Column(db.String(255))
    hidden = db.Column(db.Boolean, default=False)
    



#Test Model (Can be used as users model with few changes)
#Now it is Users model 
class Users(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(32),nullable=False,unique=True)
    name = db.Column(db.String(75),nullable=False)
    email = db.Column(db.String(150),nullable=False,unique=True)
    fav_color = db.Column(db.String(50))
    password_hash = db.Column(db.String(128),nullable=False)
    datetime_created = db.Column(db.DateTime, default=datetime.utcnow)



    @property
    def password(self):
        raise AttributeError('password is not in a readable format')
    
    @password.setter
    def password(self,password):
        self.password_hash = generate_password_hash(password)


    def verify_password(self,password):
        return check_password_hash(self.password_hash, password)


    def __repr__(self):
        return '<Name %r>' % self.name
    
#-------------------------------------------------------------FORMS-------------------------------------------------------------#


class UserForm(FlaskForm):
    name = StringField("Enter your name here", validators=[DataRequired()])
    username = StringField("Enter your username here", validators=[DataRequired()])
    email = StringField("Enter your email here", validators=[DataRequired()])
    fav_color = StringField("Enter your Favourite color")
    password_hash = PasswordField("Enter your password",validators=[DataRequired(), EqualTo('password_hash2',message='Passwords must match.')])
    password_hash2 = PasswordField("Enter your password again",validators=[DataRequired()])
    submit =  SubmitField("Submit")

class test(FlaskForm):
    name = StringField("Enter your name here", validators=[DataRequired()])
    submit =  SubmitField("Submit")

#Posts Form
class PostForm(FlaskForm):
    title = StringField("Enter your title here", validators=[DataRequired()])
    content = StringField("Enter your content here", validators=[DataRequired()],widget=TextArea())
    author =  StringField("Enter your author here", validators=[DataRequired()])
    slug = StringField("Enter your slug here", validators=[DataRequired()])
    submit = SubmitField("Submit")


#Login Form
class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Submit")


#Login route
@app.route('/login',methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(username = form.username.data).first()
        if user:
            if(check_password_hash(user.password_hash, form.password.data)):
                login_user(user)
                flash("Login Succesfull!!")
                return redirect(url_for('dashboard'))
            else:
                flash("Wrong Password... Try again!!")
        else:
            flash("User does not exists!!")        

    return render_template('login.html',form = form)

#dashboard route
@app.route('/dashboard',methods = ['GET','POST'])
@login_required
def dashboard():
    return render_template('dashboard.html')

#logout route
@app.route('/logout', methods = ['GET','POST'])
@login_required
def logout():
    logout_user()
    flash("Logged out succesfully!")
    return redirect(url_for('login'))

@app.route('/posts')
def posts():
    posts = Posts.query.order_by(Posts.date_posted and Posts.hidden == False)
    return render_template('posts.html',posts = posts)


@app.route('/posts/<int:id>')
def post(id):
    post = Posts.query.get_or_404(id)
    return render_template('post.html',post = post)


@app.route('/add_post', methods=['POST','GET'])
def add_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Posts(title = form.title.data, content = form.content.data, author = form.author.data ,slug = form.slug.data)
        db.session.add(post)
        db.session.commit()
        flash("Post added successfully!!")
        return redirect(url_for('add_post'))
    
    return render_template('add_post.html',form=form)


@app.route('/post/edit/<int:id>', methods=['POST','GET'])
def edit_post(id):
    post = Posts.query.get_or_404(id)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.author = form.author.data
        post.slug = form.slug.data
        post.content = form.content.data

        db.session.add(post)
        db.session.commit()
        flash("Post updated successfully")
        return redirect(url_for('post',id=post.id))
    form.title.data = post.title
    form.author.data = post.author
    form.slug.data = post.slug
    form.content.data = post.content
    return render_template('edit_post.html',form=form)


@app.route('/post/delete/<int:id>')
def delete_post(id):
    post_to_delete = Posts.query.get_or_404(id)

    try:
        db.session.delete(post_to_delete)
        db.session.commit()
        flash("Post deleted successfully")
        posts = Posts.query.order_by(Posts.date_posted and Posts.hidden == False)
        return render_template('posts.html',posts = posts)
    except: 
        flash("Oops something went wrong...")
        posts = Posts.query.order_by(Posts.date_posted and Posts.hidden == False)
        return render_template('posts.html',posts = posts)   

@app.route('/Users/Add',methods=['POST','GET'])
def add():
    name = None
    form = UserForm()

    if form.validate_on_submit():
        user = Users.query.filter_by(email = form.email.data).first()
        if user is None:
            hashed_pass = generate_password_hash(form.password_hash.data,"sha256") 
            user = Users(username = form.username.data, name = form.name.data, email = form.email.data, fav_color = form.fav_color.data, password_hash = hashed_pass)
            db.session.add(user)
            db.session.commit()    
        name = form.name.data
        flash("User added successfully!!")
        return redirect(url_for('add'))
    our_users = Users.query.order_by( Users.datetime_created)
    return render_template('add_user.html',name=name,form=form,our_users=our_users)



@app.route('/delete/<int:id>')
def delete(id):
    user_to_delete =  Users.query.get_or_404(id)
    name = None
    form = UserForm()

    try:
        db.session.delete(user_to_delete)
        db.session.commit()
        flash("User deleted successfully!!")
        our_users = Users.query.order_by( Users.datetime_created)
        return render_template('add_user.html',name=name,form=form,our_users=our_users)
    except:    
        flash("Oops!.. There was an error deleting the user") 
        our_users = Users.query.order_by( Users.datetime_created)
        return render_template('add_user.html',name=name,form=form,our_users=our_users)
        



@app.route('/Update/<int:id>',methods=['POST','GET'])
def update(id):
    form = UserForm()
    name_to_update =  Users.query.get_or_404(id)

    if request.method == 'POST':
        name_to_update.name = request.form['name']
        name_to_update.email = request.form['email']
        name_to_update.fav_color = request.form['fav_color']
        try:
            db.session.commit()
            flash("User updated successfully")
            return render_template('update.html',form = form,name_to_update=name_to_update)     
        except:
            flash("Oops Something went wrong... Try again!")
            return render_template('update.html',form = form,name_to_update=name_to_update)
    else:
        return render_template('update.html',form = form,name_to_update=name_to_update,id = id)




@app.route('/namepage', methods=['GET','POST'])
def namepage():
    name = None
    form = test() 

    if form.validate_on_submit():
        name = form.name.data
        form.name.data = ''
        flash("Name submitted successfully")

    return render_template('name.html', name= name, form= form)    




if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)