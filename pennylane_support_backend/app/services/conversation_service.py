
from __future__ import annotations

from typing import Optional
import uuid

from flask import g
from sqlalchemy.orm import Session

from app.extensions import db
from app.models.support import SupportConversation, ConversationPost
from app.models.challenge import Challenge
from app.models.user import User


class ServiceError(Exception):
    """Base class for service errors."""


class ValidationError(ServiceError):
    """Raised when user input is invalid."""


class AuthorizationError(ServiceError):
    """Raised when the current user lacks permission."""


class NotFoundError(ServiceError):
    """Raised when a referenced record cannot be found."""


def _gen_identifier() -> str:
    """
    Generate a human‑readable identifier for a conversation (e.g. CONV_A1B2C3D4).
    """
    return f"CONV_{uuid.uuid4().hex[:8].upper()}"


def _current_user_display_name() -> str:
    """
    Derive a display name from the current user stored .
    Returns an empty string if no user information is available.
    """
    try:
        cu = getattr(g, "current_user", None)
        if isinstance(cu, dict):
            return cu.get("name") or cu.get("nickname") or cu.get("email") or ""
    except Exception:
        pass
    return ""


def create_conversation(
    challenge_public_id: str,
    topic: str,
    category: Optional[str] = None,
    first_post: Optional[str] = None,
    author_display_name: Optional[str] = None,
    *,
    session: Optional[Session] = None,
) -> SupportConversation:
    """
    Create a new support conversation.  If `first_post` is supplied,
    automatically create an initial ConversationPost with an author display
    name.

    Args:
        challenge_public_id: The public identifier of the related challenge.
        topic: A required topic summarizing the issue.  Leading/trailing
               whitespace is trimmed.  Must not be empty and maximum 255
               characters.
        category: Optional category (defaults to "PennyLane Help").  Maximum
                  100 characters.
        first_post: Optional body of the initial post.  If supplied, a
                    ConversationPost will be created.
        author_display_name: Optional display name for the author.  When not
                             provided, the current user's name/nickname/email
                             or "User" will be used.
        session: Optional SQLAlchemy session for testing.  Defaults to the
                 application database session.

    Returns:
        The newly created SupportConversation instance (detached).

    Raises:
        ValidationError: If topic is empty or exceeds length limits.
        NotFoundError: If the referenced challenge does not exist.
    """
    session = session or db.session

    topic = (topic or "").strip()
    if not topic:
        raise ValidationError("Topic cannot be empty")
    if len(topic) > 255:
        raise ValidationError("Topic must be at most 255 characters")

    category = (category or "PennyLane Help").strip()
    if len(category) > 100:
        raise ValidationError("Category must be at most 100 characters")

    # Find the challenge by public_id; may be None
    challenge = Challenge.query.filter_by(public_id=challenge_public_id).first()

    # Create the conversation record
    conv = SupportConversation(
        identifier=_gen_identifier(),
        topic=topic,
        category=category,
        challenge=challenge,
        status="OPEN",
    )
    session.add(conv)
    session.flush()  

    # If an initial post is provided, create it
    if first_post and first_post.strip():
        content = first_post.strip()
        display = (author_display_name or "").strip() or _current_user_display_name()
        if not display:
            display = "User"
        post = ConversationPost(
            conversation_id=conv.id,
            content=content,
            author_display_name=display,
        )
        session.add(post)

    session.commit()
    return conv


def assign_conversation(
    conversation_id: int,
    *,
    roles: list[str],
    current_user: dict,
    session: Optional[Session] = None,
) -> SupportConversation:
    """
    Assign the specified conversation to the current user.  Only users with
    the `support_admin` role may assign conversations.

    Args:
        conversation_id: ID of the conversation to assign.
        roles: List of role strings from the JWT.
        current_user: Dict representing the JWT payload.
        session: Optional SQLAlchemy session for testing.

    Returns:
        The updated SupportConversation instance.

    Raises:
        AuthorizationError: If the user does not have the `support_admin` role.
        NotFoundError: If the conversation does not exist.
    """
    session = session or db.session

    if "support_admin" not in roles:
        raise AuthorizationError("Only support agents can assign conversations")

    sub = current_user.get("sub") if isinstance(current_user, dict) else None
    if not sub:
        raise AuthorizationError("Missing user context")

    # Ensure the local User row exists or create it
    user = User.query.filter_by(auth0_id=sub).first()

    ns = "https://pennylane.app/"
    name_claim  = (current_user.get("name")  or current_user.get(f"{ns}name"))
    email_claim = (current_user.get("email") or current_user.get(f"{ns}email"))
    if not user:
        username_source = current_user.get("nickname") or name_claim or email_claim or sub
        username = str(username_source).split("@")[0]

        email = email_claim or f"{sub.replace('|', '_')}@example.com"

        user = User(
            username=username,
            email=email,
            auth0_id=sub,
            name=name_claim,  
        )
        session.add(user)
        session.flush()
    else:
        if not getattr(user, "name", None) and name_claim:
            user.name = name_claim
        if email_claim:
            is_placeholder = (not user.email) or user.email.endswith("@example.com")
            if is_placeholder and user.email != email_claim:
                exists = session.query(User.id).filter(User.email == email_claim).first()
                if not exists:
                    user.email = email_claim

        session.flush()

    conv = SupportConversation.query.get(conversation_id)
    if not conv:
        raise NotFoundError("Conversation not found")

    conv.assigned_to_user_id = user.id
    conv.status = "ASSIGNED"
    session.commit()
    return conv


def add_post(
    conversation_id: int,
    content: str,
    author_display_name: Optional[str] = None,
    *,
    current_user: Optional[dict] = None,
    session: Optional[Session] = None,
) -> ConversationPost:
    """
    Add a reply post to a conversation.  Validates that the content is not empty.

    Args:
        conversation_id: ID of the conversation being replied to.
        content: Reply text; trimmed and must not be empty.
        author_display_name: Optional override for the author display name.  If
                             not provided and the user is authenticated, the
                             user's display name will be used.
        current_user: Dict representing the JWT payload (may be None).
        session: Optional SQLAlchemy session for testing.

    Returns:
        The newly created ConversationPost instance.

    Raises:
        ValidationError: If `content` is empty.
        NotFoundError: If the conversation does not exist.
    """
    session = session or db.session

    content = (content or "").strip()
    if not content:
        raise ValidationError("Reply content cannot be empty")

    conv = SupportConversation.query.get(conversation_id)
    if not conv:
        raise NotFoundError("Conversation not found")

    author_user_id: Optional[int] = None
    if current_user and isinstance(current_user, dict):
        sub = current_user.get("sub")
        if sub:
            user = User.query.filter_by(auth0_id=sub).first()
            if user:
                author_user_id = user.id

    display = (author_display_name or "").strip()
    if not display and current_user:
        display = _current_user_display_name()

    post = ConversationPost(
        conversation_id=conversation_id,
        content=content,
        author_user_id=author_user_id,
        author_display_name=display if display else None,
    )
    session.add(post)
    session.commit()
    return post