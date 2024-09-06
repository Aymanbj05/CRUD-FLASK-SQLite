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


@app.route('/logout', methods=['POST'])
def logout():
    session.pop('username', None)
    session.pop('password', None)
    return redirect(url_for('login'))


@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        title = request.form['title']
        author_name = request.form['author']
        author_email = request.form['email']
        category_name = request.form['category']

        # Check if the author already exists
        author = Author.query.filter_by(email=author_email).first()
        if not author:
            author = Author(name=author_name, email=author_email)
            db.session.add(author)
            db.session.commit()


        # Check if the category already exists
        category = Category.query.filter_by(name=category_name).first()
        if not category:
            category = Category(name=category_name)
            db.session.add(category)
            db.session.commit()

        # Create the new book
        new_book = Book(title=title, author_id=author.idAuthor, category_id=category.idCategory)
        db.session.add(new_book)
        db.session.commit()

        return redirect(url_for('index'))

    elif request.method == 'GET':
        authors = Author.query.all()
        categories = Category.query.all()
        return render_template('add.html', authors=authors, categories=categories)


@app.route('/edit_book/<int:id>', methods=['GET', 'POST'])
def edit_book(id):
    book = Book.query.get_or_404(id)  # Récupère le livre avec l'ID donné
    if request.method == 'POST':
        # Récupère les valeurs du formulaire
        book.title = request.form.get('title')
        book.author_id = request.form.get('author_id')
        book.category_id = request.form.get('category_id')

        # Récupère les informations de l'auteur depuis le formulaire
        author_name = request.form.get('author_name')
        author_email = request.form.get('author_email')
        author_id = request.form.get('author_id')
        category_name = request.form.get('category_name')
        category_id = request.form.get('category_id')


        # Cherche l'auteur existant ou crée un nouveau
        author = Author.query.get(author_id)
        category= Category.query.get(book.category_id)
        if author and category:
            author.name = author_name
            author.email = author_email
            category.name = category_name
        else:
            author = Author(name=author_name, email=author_email)
            category = Category(name=category_name)
            db.session.add(category)
            db.session.add(author)



        # Met à jour la relation auteur du livre
        book.author = author
        book.category = category

        # Enregistre les modifications dans la base de données
        db.session.commit()

        # Redirige vers la page d'index
        return redirect(url_for('index'))

    # Récupère les données pour pré-remplir le formulaire
    authors = Author.query.all()
    categories = Category.query.all()

    return render_template('edit.html', book=book, authors=authors, categories=categories)


@app.route('/delete_book/<int:id>', methods=['POST'])
def delete_book(id):
    book= Book.query.get_or_404(id)
    db.session.delete(book)
    db.session.commit()
    return redirect(url_for('index'))



if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)