"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase

from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data
with app.app_context():
    db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        self.client = app.test_client()

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)

    
    def test_repr(self):
        """Test the __repr__ method."""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        self.assertEqual(repr(u), f"<User #{u.id}: {u.username}, {u.email}>")

    def test_is_following(self):
        """Test the is_following method."""

        u1 = User(
            email="test1@test.com",
            username="testuser1",
            password="HASHED_PASSWORD1"
        )
        u2 = User(
            email="test2@test.com",
            username="testuser2",
            password="HASHED_PASSWORD2"
        )

        db.session.add_all([u1, u2])
        db.session.commit()

        # Make u1 follow u2
        u1.following.append(u2)
        db.session.commit()

        self.assertTrue(u1.is_following(u2))
        self.assertFalse(u2.is_following(u1))
    
    def test_is_followed_by(self):
        """Test the is_followed_by method."""

        user1 = User(username='user1', email='user1@example.com')
        user2 = User(username='user2', email='user2@example.com')
        db.session.add_all([user1, user2])
        db.session.commit()

        # Make user1 followed by user2
        user2.following.append(user1)
        db.session.commit()

        self.assertTrue(user1.is_followed_by(user2))
        self.assertFalse(user2.is_followed_by(user1))
    
    def test_create_duplicate_username(self):
        """Test create method with duplicate username."""

        user1 = User.signup(username='testuser', email='test1@example.com', password='password1', image_url='image1.png')
        user2 = User.signup(username='testuser', email='test2@example.com', password='password2', image_url='image2.png')
        db.session.commit()

        self.assertIsNone(user2)