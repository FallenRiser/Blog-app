from datetime import datetime
import os
import website.models as models
from flask import Flask, render_template, request, url_for, redirect
from flask_loginmanager import LoginManager
from flask_login import login_user, logout_user, login_required
import bcrypt as bpt
from website.models import db


current_dir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)



@app.route('/',methods=['GET','POST'])
def index():
    
    if request.method =='GET':
        return render_template('./index.html')

    if request.method =='POST':
        userid = request.form['usrid']
        password = request.form['password']
        query = " SELECT userid,password FROM users where userid = '"+userid+"' and password = '"+password+"'"
        db.cur.execute(query)
        results = db.cur.fetchall()

        if len(results)==0:
            print("Sorry you need to sign up for this app.")
        else:    
            return render_template('./home.html',username=userid)    

@app.route('/signup',methods=['GET','POST'])
def signup():
    if request.method == 'GET':
        return render_template('./signup.html')
    if request.method =='POST':
        userid = request.form['usrid']
        password = request.form['password']
        create_time = acc_timestamp()
        email = request.form['email']
        db.cur.execute("INSERT INTO users VALUES(?,?,?,?,?,?)",(create_time,userid,email,password))
        db.con.commit()
        return redirect(url_for('index'))


def acc_timestamp():
    acc_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return acc_timestamp




if __name__ == '__main__':
    app.run(debug=True)