
from flask import Flask, redirect, render_template, request, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from urllib.parse import quote
from models import Users, Todoss, db
from flask_bcrypt import Bcrypt

encoded_password=quote("root")
app = Flask(__name__)
bcrypt = Bcrypt(app)


app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+mysqlconnector://root:{encoded_password}@mysql-db:3306/ashish'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = '123'  
db.init_app(app)    


def hash_password(password):
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    return hashed_password

def check_password(password, hashed_password):
    return bcrypt.check_password_hash(hashed_password, password)

@app.route('/signup', methods=["GET", "POST"])
def signup():
    error = None
    if request.method == "POST":
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # Check if username or email already exists
        existing_user = Users.query.filter((Users.username == username) | (Users.email == email)).first()
        if existing_user:
            error = "Username or email already exists. Please choose a different one."
            return render_template('signup.html', error=error)

        hashed_password = hash_password(password)

        new_user = Users(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        # Get the id of the newly created user
        user_id = new_user.id
        session['user_id'] = user_id

        return redirect("/login")
    return render_template('signup.html', error=error)

@app.route('/login', methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        user = Users.query.filter_by(username=username).first()

        if user and check_password(password, user.password):
            session['user_id'] = user.id
            return redirect("/")
        else:
            error = "Please enter correct username and password."

    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect("/login")


@app.route('/', methods=["GET", "POST"])
def hello_world():
    username=None

    if 'user_id' in session:
        user_id = session['user_id']
        user = Users.query.filter_by(id=user_id).first()
        username = user.username if user else None

        
        if request.method == "POST":
            title = request.form['title']
            desc = request.form['desc']
            user_id = session['user_id']
            
            print(f"DEBUG: username={username}")
            todo = Todoss(title=title, desc=desc, user_id=user_id)
            db.session.add(todo)
            db.session.commit()

        user_todos = Todoss.query.filter_by(user_id=session['user_id']).all()
        return render_template('index.html', allTodo=user_todos,username=username)
    else:
        return redirect("/login")


@app.route('/update/<int:sno>', methods=["GET", "POST"])
def update(sno):
    if 'user_id' not in session:
        return redirect("/login")

    user_id = session['user_id']
    todo = Todoss.query.filter_by(sno=sno, user_id=user_id).first()

    if not todo:
        return redirect("/")

    if request.method == "POST":
        title = request.form['title']
        desc = request.form['desc']

        todo.title = title
        todo.desc = desc

        db.session.commit()
        return redirect("/")

    return render_template('update.html', todo=todo)


@app.route('/delete/<int:sno>')
def delete(sno):
    if 'user_id' not in session:
        return redirect("/login")

    user_id = session['user_id']
    todo = Todoss.query.filter_by(sno=sno, user_id=user_id).first()

    if todo:
        db.session.delete(todo)
        db.session.commit()

    return redirect("/")


@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True,host='0.0.0.0', port=5001)
