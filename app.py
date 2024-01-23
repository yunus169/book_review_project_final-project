from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
import requests

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///books.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Models
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    summary = db.Column(db.Text, nullable=False)
    genre = db.Column(db.String(50), nullable=False)
    reviews = db.relationship('Review', backref='book', lazy=True)

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(100), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    text = db.Column(db.Text, nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)

# Initialize the database
@app.before_first_request
def initialize_database():
    db.create_all()

# Welcome route
@app.route('/')
def welcome():
    return "Welcome to the Book Review Platform!"

# GET all books with optional filtering
@app.route('/books', methods=['GET'])
def get_books():
    query = Book.query
    title = request.args.get('title')
    author = request.args.get('author')
    genre = request.args.get('genre')
    if title:
        query = query.filter(Book.title.contains(title))
    if author:
        query = query.filter(Book.author.contains(author))
    if genre:
        query = query.filter(Book.genre.contains(genre))
    books = query.all()
    book_list = [{'id': book.id, 'title': book.title, 'author': book.author, 'summary': book.summary, 'genre': book.genre} for book in books]
    return jsonify({'books': book_list})

# POST a new book
@app.route('/books', methods=['POST'])
def add_book():
    data = request.json
    new_book = Book(
        title=data['title'],
        author=data['author'],
        summary=data['summary'],
        genre=data['genre']
    )
    db.session.add(new_book)
    db.session.commit()
    return jsonify({'message': 'Book added successfully'}), 201

# GET a single book
@app.route('/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    book = Book.query.get(book_id)
    if not book:
        return jsonify({'message': 'Book not found'}), 404
    book_data = {'id': book.id, 'title': book.title, 'author': book.author, 'summary': book.summary, 'genre': book.genre}
    return jsonify(book_data)

# PUT update a book
@app.route('/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    data = request.json
    book = Book.query.get(book_id)
    if not book:
        return jsonify({'message': 'Book not found'}), 404
    book.title = data.get('title', book.title)
    book.author = data.get('author', book.author)
    book.summary = data.get('summary', book.summary)
    book.genre = data.get('genre', book.genre)
    db.session.commit()
    return jsonify({'message': 'Book updated successfully'})

# DELETE a book
@app.route('/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    book = Book.query.get(book_id)
    if not book:
        return jsonify({'message': 'Book not found'}), 404
    db.session.delete(book)
    db.session.commit()
    return jsonify({'message': 'Book deleted successfully'})

# POST a review
@app.route('/reviews', methods=['POST'])
def add_review():
    data = request.json
    new_review = Review(
        user=data['user'],
        rating=data['rating'],
        text=data['text'],
        book_id=data['book_id']
    )
    db.session.add(new_review)
    db.session.commit()
    return jsonify({'message': 'Review added successfully'}), 201

# GET all reviews
@app.route('/reviews', methods=['GET'])
def get_reviews():
    reviews = Review.query.all()
    review_list = [{'id': review.id, 'user': review.user, 'rating': review.rating, 'text': review.text, 'book_id': review.book_id} for review in reviews]
    return jsonify({'reviews': review_list})

# GET reviews for a specific book along with average rating
@app.route('/reviews/<int:book_id>', methods=['GET'])
def get_reviews_for_book(book_id):
    reviews = Review.query.filter_by(book_id=book_id).all()
    if not reviews:
        return jsonify({'message': 'No reviews found for this book'}), 404

    total_rating = sum(review.rating for review in reviews)
    average_rating = total_rating / len(reviews) if reviews else 0

    review_list = [{'id': review.id, 'user': review.user, 'rating': review.rating, 'text': review.text} for review in reviews]
    return jsonify({'reviews': review_list, 'average_rating': average_rating})

# GET top 5 books based on average rating
@app.route('/books/top', methods=['GET'])
def top_books():
    books = Book.query.all()
    book_ratings = []

    for book in books:
        if book.reviews:
            total_rating = sum(review.rating for review in book.reviews)
            average_rating = total_rating / len(book.reviews)
            book_ratings.append((book, average_rating))

    top_books = sorted(book_ratings, key=lambda x: x[1], reverse=True)[:5]
    top_books_list = [{'id': book[0].id, 'title': book[0].title, 'author': book[0].author, 'summary': book[0].summary, 'genre': book[0].genre, 'average_rating': book[1]} for book in top_books]
    return jsonify({'top_books': top_books_list})

# GET author information
@app.route('/author/<author_name>', methods=['GET'])
def get_author_info(author_name):
    encoded_author_name = requests.utils.quote(author_name)
    url = f'https://openlibrary.org/search/authors.json?q={encoded_author_name}'
    response = requests.get(url)
    if response.status_code == 200:
        author_data = response.json()
        return jsonify(author_data)
    else:
        return jsonify({'message': 'Author information not found'}), response.status_code

if __name__ == '__main__':
    app.run(debug=True)
