from flask import Flask, render_template,flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

current_dir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+ os.path.join(current_dir,"test.db")
app.config['SECRET_KEY'] = 'this key is super dooper se bhi Uper VaLa SecRET'


db = SQLAlchemy()
db.init_app(app)
app.app_context().push()


class TestDB(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(75),nullable=False)
    email = db.Column(db.String(150),nullable=False,unique=True)
    datetime_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Name %r>' % self.name
    



class UserForm(FlaskForm):
    name = StringField("Enter your name here", validators=[DataRequired()])
    email = StringField("Enter your email here", validators=[DataRequired()])
    submit =  SubmitField("Submit")

class test(FlaskForm):
    name = StringField("Enter your name here", validators=[DataRequired()])
    email = StringField("Enter your email here", validators=[DataRequired()])
    submit =  SubmitField("Submit")





@app.route('/Users/Add',methods=['POST','GET'])
def Add():
    name = None
    form = UserForm()

    if form.validate_on_submit():
        user = TestDB.query.filter_by(email = form.email.data).first()
        if user is None:
            user = TestDB(name = form.name.data, email = form.email.data)
            db.session.add(user)
            db.session.commit()    
        name = form.name.data
        form.name.data = ''
        form.email.data = ''
        flash("User added successfully!!")
    our_users = TestDB.query.order_by(TestDB.datetime_created)
    return render_template('add_user.html',name=name,form=form,our_users=our_users)




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