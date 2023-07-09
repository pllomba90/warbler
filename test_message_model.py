from datetime import datetime
from unittest import TestCase
from models import db, User, Message, Follows
from app import app

# Set up your tests with the necessary setup and teardown methods

class MessageModelTestCase(TestCase):
    """Test cases for the Message model."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        self.client = app.test_client()

    def test_get_messages_from_followed_users(self):
        """Test get_messages_from_followed_users method."""

        # Create users
        user1 = User(username="user1")
        user2 = User(username="user2")
        user3 = User(username="user3")
        db.session.add_all([user1, user2, user3])
        db.session.commit()

        # Make user1 follow user2 and user3
        user1.following.append(user2)
        user1.following.append(user3)
        db.session.commit()

        # Create messages from followed users
        message1 = Message(text="Message from user2", timestamp=datetime.utcnow(), user_id=user2.id)
        message2 = Message(text="Message from user3", timestamp=datetime.utcnow(), user_id=user3.id)
        message3 = Message(text="Message from user1", timestamp=datetime.utcnow(), user_id=user1.id)
        db.session.add_all([message1, message2, message3])
        db.session.commit()

        # Get messages from followed users of user1
        messages = Message.get_messages_from_followed_users(user1)

        # Assert that the messages include messages from user2 and user3
        self.assertIn(message1, messages)
        self.assertIn(message2, messages)
        # Assert that the message from user1 is not included
        self.assertNotIn(message3, messages)
