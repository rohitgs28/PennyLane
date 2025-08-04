import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType
from graphene import relay

from app.extensions import db
from app.models.user import User
from app.models.challenge import Challenge, ChallengeHint, LearningObjective, Tag
from app.models.support import SupportConversation, ConversationPost
class UserType(SQLAlchemyObjectType):

    class Meta:
        model = User

  
    name = graphene.String()

    def resolve_name(parent: User, info):
        return getattr(parent, "name", None) or getattr(parent, "username", None)


class TagType(SQLAlchemyObjectType):
    class Meta:
        model = Tag


class ChallengeHintType(SQLAlchemyObjectType):
    class Meta:
        model = ChallengeHint


class LearningObjectiveType(SQLAlchemyObjectType):
    class Meta:
        model = LearningObjective


class ConversationPostType(SQLAlchemyObjectType):
    class Meta:
        model = ConversationPost



class SupportConversationType(SQLAlchemyObjectType):

    class Meta:
        model = SupportConversation

    posts = graphene.List(lambda: ConversationPostType)
    assigned_support = graphene.Field(lambda: UserType)

    # resolvers
    def resolve_posts(parent, info):
        return parent.posts

    def resolve_assigned_support(parent, info):
        if parent.assigned_to_user_id: 
            return db.session.query(User).get(parent.assigned_to_user_id)
        return None


class ChallengeType(SQLAlchemyObjectType):
    class Meta:
        model = Challenge

    assigned_support = graphene.Field(UserType)
    conversations = graphene.List(lambda: SupportConversationType)
    hints = graphene.List(lambda: ChallengeHintType)
    learning_objectives = graphene.List(lambda: LearningObjectiveType)


    def resolve_conversations(parent: Challenge, info):
        return parent.conversations

    def resolve_hints(parent: Challenge, info):
        return parent.hints

    def resolve_learning_objectives(parent: Challenge, info):
        return parent.learning_objectives



class PaginatedConversationsType(graphene.ObjectType):
    items = graphene.List(SupportConversationType)
    total = graphene.Int()


class PaginatedChallengesType(graphene.ObjectType):
    items = graphene.List(ChallengeType)
    total = graphene.Int()
