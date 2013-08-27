import os
import hashlib
from flask import Flask, render_template, request, session, redirect, url_for, escape, g
from functools import wraps
from flask.ext.sqlalchemy import SQLAlchemy
import json
data = [{"x":1,"y":1,"z":3},{"x":2,"y":4,"z":4},{"x":3,"y":7,"z":5}]




app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://tjxcxreyeqogcl:sA1eX2Y5XwGBirlhg8elgZW-kt@ec2-54-221-236-4.compute-1.amazonaws.com/dfstbp77qj18nk'
app.secret_key = 'Z>\xed\x81\xfeI\x8b\xfeh\x15\x13\x0e\x02#\tI \x94r\xbd\xc0\x84\xcc\xbc'
session = {'user':None}
db = SQLAlchemy(app)

class Users(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(255), unique=True)
  sha1 = db.Column(db.String(255))

class Weights(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  timestamp = db.Column(db.TIMESTAMP)
  weight = db.Column(db.Float)
  unit = db.Column(db.String(255))


def login_required(f):
  @wraps(f)
  def decorated_function(*args, **kwargs):
    if session['user'] is None:
      return redirect(url_for('login', next=request.url))
    return f(*args, **kwargs)
  return decorated_function

def validateUser(u,p):
  try:
    user = Users.query.filter_by(username=u).first()
    if user.sha1==hashlib.sha1(p).hexdigest():        
      return True
    raise
  except:
    return False

@app.route('/login', methods=['GET', 'POST'])
def login():
  if request.method == 'POST':
    u = request.form['username']
    p = request.form['password']
    if not validateUser(u,p):
      return redirect(url_for('login'))
    session['user'] = request.form['username']
    return redirect(url_for('home'))
  return render_template('login.html')

@app.route('/', methods=['GET', 'POST'])
@login_required
def home():
  if request.method == 'GET':
    context = {'data':json.dumps(data)}
    return render_template('home.html',**context)
  if request.method == 'POST':
    context = {'data':json.dumps(data)}
    return render_template('home.html',**context)
  
if __name__ == '__main__':
  app.run(host='0.0.0.0')


