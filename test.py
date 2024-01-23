from app import app, db, Book
import pytest

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # Use in-memory SQLite for testing
    client = app.test_client()
    with app.app_context():
        db.create_all()
    yield client
    with app.app_context():
        db.drop_all()

def test_get_books_endpoint(client):
    with app.app_context():
        # Add general books for testing
        general_books = [
            Book(title="General Book 1", author="Author 1", summary="Summary 1", genre="Genre 1"),
            Book(title="General Book 2", author="Author 2", summary="Summary 2", genre="Genre 2"),
            Book(title="General Book 3", author="Author 3", summary="Summary 3", genre="Genre 3"),
        ]
        db.session.bulk_save_objects(general_books)
        db.session.commit()

    response = client.get('/books')
    assert response.status_code == 200
    data = response.get_json()
    assert 'books' in data
    assert len(data['books']) == 3  # Expecting 3 general books

def test_get_specific_book(client):
    with app.app_context():
        # Add a specific book for testing
        specific_book = Book(title="Specific Book", author="Specific Author", summary="Specific Summary", genre="Specific Genre")
        db.session.add(specific_book)
        db.session.commit()

    response = client.get('/books/1')  # Assuming the specific book has ID 1
    assert response.status_code == 200
    data = response.get_json()
    assert data['title'] == "Specific Book"
    assert data['author'] == "Specific Author"
    assert data['summary'] == "Specific Summary"
    assert data['genre'] == "Specific Genre"
