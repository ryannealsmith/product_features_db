from app import app, db

def reset_empty_database():
    """Reset database to empty state without sample data"""
    with app.app_context():
        db.drop_all()
        db.create_all()
        print("Database reset to empty state!")

if __name__ == "__main__":
    reset_empty_database()