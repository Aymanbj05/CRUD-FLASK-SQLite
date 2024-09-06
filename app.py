from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///myDB.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

app.secret_key = 'super secret key'

class User(db.Model):
    __tablename__ = 'users'
    idUser = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)


class Author(db.Model):
    __tablename__ = 'authors'
    idAuthor = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    books = db.relationship('Book', backref='author', lazy=True)

class Book(db.Model):
    __tablename__ = 'books'
    idBook = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('authors.idAuthor'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.idCategory'), nullable=False)
    category = db.relationship('Category', backref='books', lazy=True)

class Category(db.Model):
    __tablename__ = 'categories'
    idCategory = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        session['username']= request.form['username']
        session['password']= request.form['password']

        user = User.query.filter_by(username=session['username']).first()

        if user is None or not check_password_hash(user.password_hash, session['password']):
            error = 'Incorrect username or password. Please try again.'
        else:
            session['username'] = user.username
            return redirect(url_for('index'))

    return render_template('login.html', error=error)




@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        username =  request.form['username']
        email = request.form['email']
        password = request.form['password']


        # check if the user already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user is None:
            password_hash = generate_password_hash(password)
            new_user = User(username=username,email=email, password_hash=password_hash)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('login'))

        else:
            error = 'The username already exists. Please try again.'

    return render_template('register.html', error=error)
    
@app.route('/')
def index():
    if 'username' and 'password' in session:
        username = session['username']
        password = session['password']
        books = Book.query.all()
        return render_template('index.html', books=books)
    return redirect(url_for('login'))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)