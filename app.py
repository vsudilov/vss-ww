import os
import hashlib
from flask import Flask, render_template, request, session, redirect, url_for, escape, g
from functools import wraps
from flask.ext.sqlalchemy import SQLAlchemy
import json
import datetime
try:
  #localhost connection
  from keys import SQLALCHEMY_DATABASE_URI
except ImportError:
  #production connection
  import urlparse
  urlparse.uses_netloc.append("postgres")
  url = urlparse.urlparse(os.environ["HEROKU_POSTGRESQL_BRONZE_URL"])
  database=url.path[1:]
  user=url.username
  password=url.password
  host=url.hostname
  port=url.port
  SQLALCHEMY_DATABASE_URI = 'postgres://%s:%s@%s:%s/%s' % (url.username,url.password,url.hostname,url.port,database)


app = Flask(__name__)
app.config['DEBUG'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
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
  username = db.Column(db.String(255),db.ForeignKey("users.username"))
  def __init__(self,ts,w,u,un):
    self.timestamp = ts
    self.weight = w
    self.unit = u
    self.username = un

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

def queryWeights():
  weights = Weights.query.filter_by(username=session['user']).order_by(Weights.timestamp.asc())
  data = []
  for w in weights:
    data.append({'x':w.timestamp,'y':w.weight})
  dthandler = lambda obj: obj.isoformat() if isinstance(obj, datetime.datetime) else None
  return json.dumps(data,default=dthandler)

def insertWeight(weight, unit):
  now = datetime.datetime.isoformat(datetime.datetime.now())
  row = Weights(now,weight,unit,session['user'])
  db.session.add(row)
  db.session.commit()


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
  context = {'user':session['user']}
  if request.method == 'GET':
    context.update({'data':queryWeights()})
    return render_template('home.html',**context)
  if request.method == 'POST':
    insertWeight(request.form['weight'],request.form['units'])
    context.update({'data':queryWeights()})
    return render_template('home.html',**context)
  
if __name__ == '__main__':
  app.config['DEBUG'] = True
  app.run(host='0.0.0.0')


