from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(50), nullable=False)
    summary = db.Column(db.Text, nullable=False)
    genre = db.Column(db.String(50), nullable=False)
    reviews = db.relationship('Review', backref='book', lazy=True)

    def __repr__(self):
        return f'<Book {self.title}>'

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(100), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    text = db.Column(db.Text, nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)

    def __repr__(self):
        return f'<Review {self.id} by {self.user}>'
