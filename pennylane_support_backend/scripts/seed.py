from app import create_app, db
from app.models import User, Challenge

app = create_app()

with app.app_context():
    db.create_all()

    if not User.query.first():
        user1 = User(username="alice", email="alice@example.com")
        user2 = User(username="bob", email="bob@example.com")

        ch1 = Challenge(title="Intro to Quantum", category="Quantum", difficulty="Easy", points=100)
        ch2 = Challenge(title="Quantum Gates", category="Quantum", difficulty="Medium", points=200)

        db.session.add_all([user1, user2, ch1, ch2])
        db.session.commit()
        print("Seed data inserted.")
    else:
        print("Data already exists.")
