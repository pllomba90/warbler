from unittest import TestCase
from app import app
from models import db, User

class UserRoutesTestCase(TestCase):
    """Test cases for user routes."""

    def setUp(self):
        """Create test client, add sample data."""

        self.client = app.test_client()

        # Connect to the test database and create the tables
        app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql:///warbler_test"
        db.create_all()

    def tearDown(self):
        """Clean up any fouled transaction."""

        db.session.rollback()
        db.session.remove()

    def test_list_users(self):
        """Test list_users route."""

        # Add sample users to the database
        user1 = User(username="user1")
        user2 = User(username="user2")
        db.session.add_all([user1, user2])
        db.session.commit()

        # Send a GET request to the list_users route
        response = self.client.get("/users")

        # Assert that the response status code is 200 (OK)
        self.assertEqual(response.status_code, 200)

        # Assert that the rendered template is 'users/index.html'
        self.assert_template_used("users/index.html")

        # Assert that the response body contains the usernames of the added users
        self.assertIn(user1.username.encode(), response.data)
        self.assertIn(user2.username.encode(), response.data)

    def test_users_show(self):
        """Test users_show route."""

        # Add a sample user to the database
        user = User(username="testuser")
        db.session.add(user)
        db.session.commit()

        # Send a GET request to the users_show route with the user_id
        response = self.client.get(f"/users/{user.id}")

        # Assert that the response status code is 200 (OK)
        self.assertEqual(response.status_code, 200)

        # Assert that the rendered template is 'users/show.html'
        self.assert_template_used("users/show.html")

        # Assert that the response body contains the username of the added user
        self.assertIn(user.username.encode(), response.data)

    def test_users_followers(self):
        """Test users_followers route."""

        # Add a sample user and their follower to the database
        user = User(username="user1")
        follower = User(username="user2")
        follower.following.append(user)
        db.session.add_all([user, follower])
        db.session.commit()

        # Send a GET request to the users_followers route with the user_id
        response = self.client.get(f"/users/{user.id}/followers")

        # Assert that the response status code is 200 (OK)
        self.assertEqual(response.status_code, 200)

        # Assert that the rendered template is 'users/followers.html'
        self.assert_template_used("users/followers.html")

        # Assert that the response body contains the username of the follower
        self.assertIn(follower.username.encode(), response.data)

    def test_add_follow(self):
        """Test add_follow route."""

        # Add a sample user and a user to follow to the database
        user = User(username="user1")
        user_to_follow = User(username="user2")
        db.session.add_all([user, user_to_follow])
        db.session.commit()

        # Log in the user by setting the session cookie
        with self.client.session_transaction() as session:
            session['curr_user'] = user.id

        # Send a POST request to the add_follow route with the follow_id
        response = self.client.post(f"/users/follow/{user_to_follow.id}")

        # Assert that the response status code is 302 (Redirect)
        self.assertEqual(response.status_code, 302)

        # Assert that the user is following the user_to_follow
        self.assertIn(user_to_follow, user.following)

    def test_stop_following(self):
        """Test stop_following route."""

        # Add a sample user and a user to stop following to the database
        user = User(username="user1")
        followed_user = User(username="user2")
        user.following.append(followed_user)
        db.session.add_all([user, followed_user])
        db.session.commit()

        # Log in the user by setting the session cookie
        with self.client.session_transaction() as session:
            session['curr_user'] = user.id

        # Send a POST request to the stop_following route with the follow_id
        response = self.client.post(f"/users/stop-following/{followed_user.id}")

        # Assert that the response status code is 302 (Redirect)
        self.assertEqual(response.status_code, 302)

        # Assert that the user is not following the followed_user anymore
        self.assertNotIn(followed_user, user.following)

    def test_profile(self):
        """Test profile route."""

        # Add a sample user to the database
        user = User(username="testuser")
        db.session.add(user)
        db.session.commit()

        # Log in the user by setting the session cookie
        with self.client.session_transaction() as session:
            session['curr_user'] = user.id

        # Send a GET request to the profile route with the user_id
        response = self.client.get(f"/users/profile/{user.id}")

        # Assert that the response status code is 200 (OK)
        self.assertEqual(response.status_code, 200)

        # Assert that the rendered template is 'users/edit.html'
        self.assert_template_used("users/edit.html")

        # Assert that the response body contains the username of the added user
        self.assertIn(user.username.encode(), response.data)

    def test_delete_user(self):
        """Test delete_user route."""

        # Add a sample user to the database
        user = User(username="testuser")
        db.session.add(user)
        db.session.commit()

        # Log in the user by setting the session cookie
        with self.client.session_transaction() as session:
            session['curr_user'] = user.id

        # Send a POST request to the delete_user route
        response = self.client.post("/users/delete")

        # Assert that the response status code is 302 (Redirect)
        self.assertEqual(response.status_code, 302)

        # Assert that the user is deleted from the database
        self.assertIsNone(User.query.get(user.id))