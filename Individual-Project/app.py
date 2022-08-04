import os
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, redirect, url_for, flash, session
from datetime import datetime
import pyrebase

CONFIG = { 
  "apiKey": "AIzaSyC991VhI6UMnqBc9qF_-KX-77vN1QQWGpM",
  "authDomain": "individual-project-2c4bc.firebaseapp.com",
  "databaseURL": "https://individual-project-2c4bc-default-rtdb.europe-west1.firebasedatabase.app",
  "projectId": "individual-project-2c4bc",
  "storageBucket": "individual-project-2c4bc.appspot.com",
  "messagingSenderId": "755275024194",
  "appId": "1:755275024194:web:f5fb175cf7d1e3c0a0eadb",
  "measurementId": "G-4GBX17PQQ1",
}


firebase = pyrebase.initialize_app(CONFIG)
auth = firebase.auth()
db = firebase.database()

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['SECRET_KEY'] = 'super-secret-key'

@app.route('/', methods=['GET', 'POST'])
def index():
    if 'user' not in session or auth.current_user is None:
        return redirect(url_for('signin'))
    return render_template('index.html')


@app.route('/signup', methods=['GET', 'POST'])
def  signup():
    if request.method == 'POST':
        user = {'username': request.form['username'], 'email': request.form['email']}
        try:
            session['user'] = auth.create_user_with_email_and_password(user['email'], request.form['password'])
            db.child('users').child(session['user']['localId']).set(user)
            return redirect(url_for('signin'))
        except Exception:
            flash('User already exists')
            return redirect(url_for('signup'))
    return render_template('signup.html')


@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        user = {'email': request.form['email'], 'password': request.form['password']}
        try:
            session['user'] = auth.sign_in_with_email_and_password(user['email'], user['password'])
            return redirect(url_for('sock'))
        except Exception:
            flash('Invalid username or password')
            return redirect(url_for('signin', error=True))
    return render_template('signin.html')


@app.route('/sock', methods=['GET', 'POST'])
def sock():
    reviews = db.child('reviews').child('socks').get().val().values()
    if request.method == 'POST':
        try:
            session['username'] = db.child('users').child(session['user']['localId']).get().val()['username']
            sock = {'name': request.form['name'], 'username':session['username'],'review':request.form['review'],'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            db.child('reviews').child('socks').push(sock)
            reviews = db.child('reviews').child('socks').get().val().values()
            return redirect(url_for('sock', reviews=reviews))
        except Exception:
            flash('Invalid file')
            return redirect(url_for('sock', reviews=reviews))
    return render_template('sock.html', reviews=reviews)


@app.route('/dictator', methods=['GET', 'POST'])
def dictator():
    if auth.current_user is None:
        return redirect(url_for('signin'))
    


if __name__ == '__main__':
    app.run(debug=True)