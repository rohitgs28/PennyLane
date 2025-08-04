

from __future__ import annotations

from flask import g
import graphene
from graphql import GraphQLError

from app.auth import requires_auth, AuthError
from app.graphql.types import SupportConversationType, ConversationPostType

from app.services.conversation_service import (
    create_conversation as svc_create_conversation,
    assign_conversation as svc_assign_conversation,
    add_post as svc_add_post,
    ValidationError,
    AuthorizationError,
    NotFoundError,
)


class CreateConversation(graphene.Mutation):
    class Arguments:
        challenge_public_id = graphene.String(required=True)
        topic = graphene.String(required=True)
        category = graphene.String(required=False)
        first_post = graphene.String(required=False)
        author_display_name = graphene.String(required=False)

    ok = graphene.Boolean()
    conversation = graphene.Field(lambda: SupportConversationType)

    def mutate(
        self,
        info,
        challenge_public_id: str,
        topic: str,
        category: str | None = None,
        first_post: str | None = None,
        author_display_name: str | None = None,
    ):
        """
        Create a new conversation.  Returns ok=False on validation errors.
        """
        try:
            conv = svc_create_conversation(
                challenge_public_id=challenge_public_id,
                topic=topic,
                category=category,
                first_post=first_post,
                author_display_name=author_display_name,
            )
            return CreateConversation(ok=True, conversation=conv)
        except ValidationError:
            return CreateConversation(ok=False, conversation=None)
        except NotFoundError as e:
            raise GraphQLError(str(e))
        except Exception:
            raise GraphQLError("Failed to create conversation")


class AssignConversation(graphene.Mutation):
    """
    Assign a conversation to the authenticated user.  Only available to users
    with the `support_admin` role.  If successful, returns the updated
    conversation.  Unauthorized errors are surfaced via AuthError to retain
    existing behaviour in the REST layer.
    """
    class Arguments:
        conversation_id = graphene.Int(required=True)

    ok = graphene.Boolean()
    conversation = graphene.Field(lambda: SupportConversationType)

    @requires_auth
    def mutate(self, info, conversation_id: int):
        roles: list[str] = getattr(g, "roles", [])
        current_user: dict = getattr(g, "current_user", {}) or {}
        try:
            conv = svc_assign_conversation(
                conversation_id=conversation_id,
                roles=roles,
                current_user=current_user,
            )
            return AssignConversation(ok=True, conversation=conv)
        except AuthorizationError as e:
            raise AuthError({"code": "forbidden", "description": str(e)}, 403)
        except NotFoundError as e:
            raise GraphQLError(str(e))
        except Exception:
            raise GraphQLError("Failed to assign conversation")


class UpdateConversationStatus(graphene.Mutation):
    class Arguments:
        conversation_id = graphene.Int(required=True)
        status = graphene.String(required=True)  # OPEN | ASSIGNED | RESOLVED | CLOSED

    ok = graphene.Boolean()

    @requires_auth
    def mutate(self, info, conversation_id: int, status: str):
        roles: list[str] = getattr(g, "roles", [])
        if "support_admin" not in roles:
            raise AuthError(
                {"code": "forbidden", "description": "Only support agents can change status."},
                403,
            )
        from app.models.support import SupportConversation  # imported lazily to avoid circular deps
        from app.extensions import db

        conv = SupportConversation.query.get(conversation_id)
        if not conv:
            return UpdateConversationStatus(ok=False)

        conv.status = status
        db.session.commit()
        return UpdateConversationStatus(ok=True)


class AddPost(graphene.Mutation):
    class Arguments:
        conversation_id = graphene.Int(required=True)
        content = graphene.String(required=True)
        author_display_name = graphene.String(required=False)

    ok = graphene.Boolean()
    post = graphene.Field(lambda: ConversationPostType)

    def mutate(
        self,
        info,
        conversation_id: int,
        content: str,
        author_display_name: str | None = None,
    ):
        current_user: dict | None = getattr(g, "current_user", None)
        try:
            post = svc_add_post(
                conversation_id=conversation_id,
                content=content,
                author_display_name=author_display_name,
                current_user=current_user,
            )
            return AddPost(ok=True, post=post)
        except ValidationError:
            return AddPost(ok=False, post=None)
        except NotFoundError as e:
            raise GraphQLError(str(e))
        except Exception:
            raise GraphQLError("Failed to add reply")