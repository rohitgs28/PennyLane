

import pytest
from app import create_app
from app.extensions import db
from app.services import conversation_service as svc


@pytest.fixture
def app_ctx():
    """Create an application context with an in‑memory SQLite database."""
    app = create_app({
        "SQLALCHEMY_DATABASE_URI": "PostGres",
        "TESTING": True,
    })
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


def test_create_conversation_empty_topic_raises_validation_error(app_ctx):
    # Creating a conversation with an empty topic should raise ValidationError
    with pytest.raises(svc.ValidationError):
        svc.create_conversation(
            challenge_public_id="",
            topic="   ",
            category=None,
            first_post=None,
            author_display_name=None,
        )


def test_add_post_empty_content_raises_validation_error(app_ctx):
    # Setup: create a valid conversation first
    conv = svc.create_conversation(
        challenge_public_id="",
        topic="Valid topic",
        category=None,
        first_post=None,
        author_display_name=None,
    )
    # Attempt to add a post with empty content
    with pytest.raises(svc.ValidationError):
        svc.add_post(
            conversation_id=conv.id,
            content="   ",
            author_display_name="",
            current_user=None,
        )


def test_assign_conversation_without_role_raises_authorization_error(app_ctx):
    # Setup: create a conversation and a dummy user payload
    conv = svc.create_conversation(
        challenge_public_id="",
        topic="Need help",
        category=None,
        first_post=None,
        author_display_name=None,
    )
    roles: list[str] = []  # no support_admin role
    current_user = {"sub": "user123", "email": "user@example.com"}
    with pytest.raises(svc.AuthorizationError):
        svc.assign_conversation(
            conversation_id=conv.id,
            roles=roles,
            current_user=current_user,
        )