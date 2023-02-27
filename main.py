from flask import Flask, render_template
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


app = Flask(__name__)
app.config['SECRET_KEY'] = 'this key is super dooper se bhi Uper VaLa SecRET'

class test(FlaskForm):
    name = StringField("Enter your name here", validators=[DataRequired()])
    submit =  SubmitField("Submit")



@app.route('/namepage', methods=['GET','POST'])
def namepage():
    name = None
    form = test() 

    if form.validate_on_submit():
        name = form.name.data
        form.name.data = ''

    return render_template('name.html', name= name, form= form)    





if __name__ == '__main__':
    app.run(debug=True)