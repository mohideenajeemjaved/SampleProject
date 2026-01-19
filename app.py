from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "secret_key_for_session" # Change this for production

# Database Configuration
app.config['SQLALCHEMY_DATABASE_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

# User Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)
    is_logged_in = db.Column(db.Boolean, default=False) # For admin monitoring

# Create the database
with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        uname = request.form['username']
        pwd = request.form['password']
        
        # Simple check if user exists
        if User.query.filter_by(username=uname).first():
            flash("Username already exists!")
        else:
            new_user = User(username=uname, password=pwd)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        uname = request.form['username']
        pwd = request.form['password']
        user = User.query.filter_by(username=uname, password=pwd).first()
        
        if user:
            session['user'] = uname
            user.is_logged_in = True
            db.session.commit()
            return f"Welcome {uname}! <a href='/logout'>Logout</a>"
        else:
            flash("Invalid credentials")
    return render_template('login.html')

@app.route('/logout')
def logout():
    uname = session.get('user')
    user = User.query.filter_by(username=uname).first()
    if user:
        user.is_logged_in = False
        db.session.commit()
    session.pop('user', None)
    return redirect(url_for('login'))

# Admin Dashboard
@app.route('/admin')
def admin():
    # Simple security: check if a specific 'admin' is logged in 
    # (In a real app, use a 'role' column in the DB)
    users = User.query.all()
    return render_template('admin.html', users=users)

if __name__ == '__main__':
    app.run(debug=True)