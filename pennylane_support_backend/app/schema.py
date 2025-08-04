import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType
from app.models import User, Challenge
from app.models.support import SupportConversation, ConversationPost
from app import db

# --- User ---
class UserType(SQLAlchemyObjectType):
    class Meta:
        model = User

# --- Post ---
class ConversationPostType(SQLAlchemyObjectType):
    class Meta:
        model = ConversationPost

# --- Conversation ---
class SupportConversationType(SQLAlchemyObjectType):
    class Meta:
        model = SupportConversation

    posts = graphene.List(ConversationPostType)

    def resolve_posts(parent, info):
        return parent.posts

# --- Challenge ---
class ChallengeType(SQLAlchemyObjectType):
    class Meta:
        model = Challenge

    conversations = graphene.List(lambda: SupportConversationType)

    def resolve_conversations(parent, info):
        return db.session.query(SupportConversation).filter_by(challenge_id=parent.id).all()

# --- Query ---
class Query(graphene.ObjectType):
    all_users = graphene.List(UserType)
    all_challenges = graphene.List(ChallengeType)
    challenge = graphene.Field(ChallengeType, public_id=graphene.String(required=True))

    def resolve_all_users(parent, info):
        return db.session.query(User).all()

    def resolve_all_challenges(parent, info):
        return db.session.query(Challenge).all()

    def resolve_challenge(parent, info, public_id):
        return db.session.query(Challenge).filter_by(publicId=public_id).first()

# --- Schema ---
schema = graphene.Schema(query=Query)
