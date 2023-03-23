from flask import Flask, render_template,flash,request,url_for,redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from flask_migrate import Migrate
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, login_user, login_required, LoginManager, logout_user, current_user
from flask_ckeditor import CKEditor
from werkzeug.utils import secure_filename
import os
import uuid as uuid
from forms import *



current_dir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+ os.path.join(current_dir,"BlogApp.db")
app.config['SECRET_KEY'] = 'this key is super dooper se bhi Uper VaLa SecRET'
UPLOAD_FOLDER = os.path.join(current_dir,"static/images")
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ckeditor = CKEditor(app)
####################################################### METADATA #####################################################################

metadata = MetaData(
    naming_convention={
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
    }
)


db = SQLAlchemy(metadata=metadata)
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
    #author = db.Column(db.String(255))
    date_posted = db.Column(db.DateTime,default = datetime.utcnow())
    slug = db.Column(db.String(255))
    hidden = db.Column(db.Boolean, default=False)
    poster_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete = "CASCADE"), nullable=False)
    comments = db.relationship('Comment', backref ='post', passive_deletes = True)



#Test Model (Can be used as users model with few changes)
#Now it is Users model 
class Users(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(32),nullable=False,unique=True)
    name = db.Column(db.String(75),nullable=False)
    email = db.Column(db.String(150),nullable=False,unique=True)
    fav_color = db.Column(db.String(50))
    user_bio = db.Column(db.Text(50000), nullable=True)
    profile_pic = db.Column(db.String(), nullable = True)
    password_hash = db.Column(db.String(128),nullable=False)
    datetime_created = db.Column(db.DateTime, default=datetime.utcnow)
    posts = db.relationship('Posts', backref ='poster', cascade = 'all,delete-orphan')
    comments = db.relationship('Comment', backref ='poster', passive_deletes = all)


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
    

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(500),nullable=False)
    date_posted = db.Column(db.DateTime,default = datetime.utcnow())
    poster_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete = "CASCADE"), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id', ondelete = "CASCADE"), nullable=False)




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


@app.route('/posts/<int:id>', methods = ['GET','POST'])
def post(id):
    post = Posts.query.get_or_404(id)
    form = CommentForm()
    if form.validate_on_submit() and current_user.is_authenticated:
        try:
            comment = Comment(content = form.content.data , poster = current_user, post_id = post.id)
            db.session.add(comment)
            db.session.commit()
            flash('Comment added successfully','success')
            return redirect(url_for('post',id = id))
        except:
            flash('Error occured while adding comment','danger')
            db.session.rollback()
    comments = Comment.query.filter_by(post_id = id).order_by(Comment.date_posted.desc())
    return render_template('post.html',post = post, comments = comments, form = form, id = post.id)


@app.route('/add_post', methods=['POST','GET'])
@login_required
def add_post():
    form = PostForm()
    if form.validate_on_submit():
        poster = current_user.id
        post = Posts(title = form.title.data, content = form.content.data, poster_id = poster, slug = form.slug.data)
        db.session.add(post)
        db.session.commit()
        flash("Post added successfully!!")
        return redirect(url_for('add_post'))
    
    return render_template('add_post.html',form=form)



@app.route('/post/edit/<int:id>', methods=['POST','GET'])
@login_required
def edit_post(id):
    post = Posts.query.get_or_404(id)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.slug = form.slug.data
        post.content = form.content.data
        db.session.add(post)
        db.session.commit()
        flash("Post updated successfully")
        return redirect(url_for('post',id=post.id))
    
    if current_user.id == post.poster_id:
        form.title.data = post.title
        form.slug.data = post.slug
        form.content.data = post.content
        return render_template('edit_post.html',form=form)
    else:
        flash("You aren't authorized to update this post!!")
        posts = Posts.query.order_by(Posts.date_posted and Posts.hidden == False)
        return render_template('posts.html',posts = posts)
    

    
@app.route('/post/delete/<int:id>')
@login_required
def delete_post(id):
    
    post_to_delete = Posts.query.get_or_404(id)
    id = current_user.id
    if id == post_to_delete.poster_id:
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
    else:
        flash("You aren't authorized to delete this post!!!!")
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
            user = Users(username = form.username.data, name = form.name.data, email = form.email.data, fav_color = form.fav_color.data, user_bio = form.user_bio.data, password_hash = hashed_pass)
            db.session.add(user)
            db.session.commit()    
        name = form.name.data
        flash("User added successfully!!")
        return redirect(url_for('add'))
    our_users = Users.query.order_by( Users.datetime_created)
    return render_template('add_user.html',name=name,form=form,our_users=our_users)



@app.route('/delete/<int:id>')
@login_required
def delete(id):
    user_to_delete =  Users.query.get_or_404(id)
    name = None
    form = UserForm()
    if id == current_user.id:
        try:
            db.session.delete(user_to_delete)
            db.session.commit()
            flash("User deleted successfully!!")
            our_users = Users.query.order_by( Users.datetime_created)
            logout_user()
            return render_template('add_user.html',name=name,form=form,our_users=our_users)
        except:    
            flash("Oops!.. There was an error deleting the user") 
            our_users = Users.query.order_by( Users.datetime_created)
            return render_template('add_user.html',name=name,form=form,our_users=our_users)
    else:
        flash("You are not allowed to delete this user") 
        return redirect(url_for('dashboard'))

        



@app.route('/Update/<int:id>',methods=['POST','GET'])
@login_required
def update(id):
    form = UserForm()
    name_to_update =  Users.query.get_or_404(id)

    if request.method == 'POST':
        name_to_update.username = form.username.data
        name_to_update.name = form.name.data
        name_to_update.email = form.email.data
        name_to_update.fav_color = form.fav_color.data
        name_to_update.user_bio = form.user_bio.data
        

        if request.files['profile_pic']:
            name_to_update.profile_pic = request.files['profile_pic']

            pic_filename = secure_filename(name_to_update.profile_pic.filename)
            pic_name = str(uuid.uuid1())+'$_'+ pic_filename
            name_to_update.profile_pic = pic_name
            saver = request.files['profile_pic']
            saver.save(os.path.join(app.config['UPLOAD_FOLDER'], pic_name))

            try:
                db.session.commit()

                flash("User updated successfully")
                return render_template('update.html',form = form,name_to_update=name_to_update,id = id)     
            except:
                flash("Oops Something went wrong... Try again!")
                return render_template('update.html',form = form,name_to_update=name_to_update)
            
        else:
            db.session.commit()
            flash("User updated successfully")
            return render_template('update.html',form = form,name_to_update=name_to_update,id = id)
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

@app.context_processor
def base():
    form = SearchForm()
    return dict(form=form)

@app.route('/search', methods=['POST'])
def search():
    form = SearchForm()
    posts = Posts.query
    if form.validate_on_submit():
        post.searched = form.searched.data
        posts = posts.filter(Posts.content.like('%' + post.searched + '%'))
        posts = posts.order_by(Posts.title).all()
        return render_template('search.html',form= form , searched = post.searched, posts = posts)

@app.route('/admin')
@login_required
def admin():
    id = current_user.id
    if id == 1:
        return render_template('admin.html')
    else:
        flash("Sorry you must be admin to access this page!!!")
        return redirect(url_for('dashboard'))

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)