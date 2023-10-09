# Flask Blog Application

## Description

The Flask Blog Application is a social media platform where users can create, edit, and delete posts, comment on posts, like posts, and follow other users. The application provides both web-based and API interfaces for interacting with the platform.

## Features

- **User Authentication:** Users can sign up and log in securely. Passwords are hashed for security.
- **User Profiles:** Users have profiles displaying their posts, followers, and people they follow.
- **Post Management:** Users can create, edit, and delete posts. Posts can include text and captions.
- **Comments:** Users can comment on posts, edit their comments, and delete their comments.
- **Likes:** Users can like and unlike posts.
- **Follow/Unfollow:** Users can follow and unfollow other users.
- **API Endpoints:** Provides API endpoints for user and blog post data retrieval, creation, updating, and deletion.

## Technology Stack

- **Python:** Flask framework is used for developing the application.
- **Database:** SQLAlchemy is utilized for database management.
- **Authentication:** Flask-Login is implemented for user authentication and session management.
- **API:** Flask-RESTful is used for creating API endpoints.
- **Security:** Passwords are hashed using Werkzeug's security utilities.

## Setup Instructions

1. Run the application: `python app.py`

## API Endpoints

### User API

- `GET /api/<string:username>`: Get user details by username.
- `PUT /api/<string:username>`: Update user email.
- `POST /api/`: Create a new user.
- `DELETE /api/<string:username>`: Delete user by username.

### Blog API

- `GET /api/<int:id>`: Get blog post details by post ID.
- `DELETE /api/<int:id>`: Delete blog post by post ID.
- `POST /api/<int:id>`: Create a new blog post.
- `PUT /api/<int:id>`: Update blog post text and captions by post ID.
