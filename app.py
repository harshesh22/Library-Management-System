from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'devkey'
db = SQLAlchemy(app)

# Models
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(200), nullable=False)
    copies = db.Column(db.Integer, default=1)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), unique=True, nullable=False)

class Borrow(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    borrowed_at = db.Column(db.DateTime, default=datetime.utcnow)
    returned = db.Column(db.Boolean, default=False)

# Home
@app.route('/')
def index():
    books = Book.query.all()
    users = User.query.all()
    borrows = Borrow.query.filter_by(returned=False).all()
    return render_template('index.html', books=books, users=users, borrows=borrows)

# Book routes
@app.route('/books/add', methods=['POST'])
def add_book():
    title = request.form['title']
    author = request.form['author']
    copies = int(request.form.get('copies', 1))
    if not title or not author:
        flash('Title and author required')
        return redirect(url_for('index'))
    b = Book(title=title, author=author, copies=copies)
    db.session.add(b)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/books/delete/<int:id>')
def delete_book(id):
    b = Book.query.get_or_404(id)
    db.session.delete(b)
    db.session.commit()
    return redirect(url_for('index'))

# User routes
@app.route('/users/add', methods=['POST'])
def add_user():
    name = request.form['name']
    email = request.form['email']
    if not name or not email:
        flash('Name and email required')
        return redirect(url_for('index'))
    u = User(name=name, email=email)
    db.session.add(u)
    db.session.commit()
    return redirect(url_for('index'))

# Borrow/Return
@app.route('/borrow', methods=['POST'])
def borrow_book():
    book_id = int(request.form['book_id'])
    user_id = int(request.form['user_id'])
    book = Book.query.get_or_404(book_id)
    if book.copies < 1:
        flash('No copies available')
        return redirect(url_for('index'))
    book.copies -= 1
    br = Borrow(book_id=book_id, user_id=user_id)
    db.session.add(br)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/return/<int:id>')
def return_book(id):
    br = Borrow.query.get_or_404(id)
    if not br.returned:
        br.returned = True
        book = Book.query.get(br.book_id)
        book.copies += 1
        db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    # create DB inside the app context
    with app.app_context():
        db.create_all()

    app.run(debug=True)

