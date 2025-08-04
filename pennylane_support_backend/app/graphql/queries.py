from __future__ import annotations

import graphene
from typing import Optional, List

from app.extensions import db
from app.models.challenge import Challenge, Tag
from app.models.support import SupportConversation
from app.models.user import User
from .types import (
    ChallengeType,
    SupportConversationType,
    TagType,
    PaginatedConversationsType,
    PaginatedChallengesType,
    UserType,
)

class Query(graphene.ObjectType):
    
    challenges = graphene.List(ChallengeType, search=graphene.String(), tag=graphene.String())
    challenge = graphene.Field(ChallengeType, public_id=graphene.String(required=True))
    conversation = graphene.Field(SupportConversationType,
                                  id=graphene.Int(required=True))
    conversationsByChallenge = graphene.List(SupportConversationType, challenge_public_id=graphene.String(required=True))
    tags = graphene.List(TagType)

    # Paginated
    conversationsPaged = graphene.Field(
        PaginatedConversationsType,
        status=graphene.String(),
        category=graphene.String(),
        search=graphene.String(),
        challenge_public_id=graphene.String(),
        assigned_to_user_id=graphene.Int(),           
        page=graphene.Int(default_value=1),
        page_size=graphene.Int(default_value=12),
    )

    challengesPaged = graphene.Field(
        PaginatedChallengesType,
        search=graphene.String(),
        tag=graphene.String(),
        page=graphene.Int(default_value=1),
        page_size=graphene.Int(default_value=12),
    )

    # Distinct categories for pickers/filters
    conversationCategories = graphene.List(graphene.String)
    # Distinct users referenced by assigned_to_user_id (for filter)
    assignedUsers = graphene.List(UserType)

    # ---- resolvers ----
    def resolve_challenges(self, info, search: Optional[str] = None, tag: Optional[str] = None):
        q = db.session.query(Challenge)
        if search:
            like = f"%{search}%"
            q = q.filter((Challenge.title.ilike(like)) | (Challenge.description.ilike(like)))
        if tag:
            q = q.join(Challenge.tags).filter(Tag.name == tag)
        return q.order_by(Challenge.points.desc()).all()

    def resolve_challenge(self, info, public_id: str):
        return db.session.query(Challenge).filter_by(public_id=public_id).first()
        
    def resolve_conversation(self, info, id: int):
        return db.session.query(SupportConversation).get(id)

    def resolve_conversationsByChallenge(self, info, challenge_public_id: str):
        return (
            db.session.query(SupportConversation)
            .join(SupportConversation.challenge)
            .filter(Challenge.public_id == challenge_public_id)
            .all()
        )

    def resolve_tags(self, info):
        return db.session.query(Tag).order_by(Tag.name).all()

    def resolve_conversationsPaged(
        self, info,
        status: Optional[str] = None,
        category: Optional[str] = None,
        search: Optional[str] = None,
        challenge_public_id: Optional[str] = None,
        assigned_to_user_id: Optional[int] = None,
        page: int = 1,
        page_size: int = 12,
    ):
        q = db.session.query(SupportConversation)
        if status:
            q = q.filter(SupportConversation.status == status)
        if category:
            q = q.filter(SupportConversation.category == category)
        if challenge_public_id:
            q = q.join(SupportConversation.challenge).filter(Challenge.public_id == challenge_public_id)
        if assigned_to_user_id is not None:
            q = q.filter(SupportConversation.assigned_to_user_id == assigned_to_user_id)
        if search:
            like = f"%{search}%"
            q = q.filter(SupportConversation.topic.ilike(like))

        total = q.count()
        items = (
            q.order_by(SupportConversation.created_at.desc())
             .offset(max(0, (page - 1) * page_size))
             .limit(page_size)
             .all()
        )
        return PaginatedConversationsType(items=items, total=total)

    def resolve_challengesPaged(self, info, search: Optional[str] = None, tag: Optional[str] = None,
                                page: int = 1, page_size: int = 12):
        q = db.session.query(Challenge)
        if search:
            like = f"%{search}%"
            q = q.filter((Challenge.title.ilike(like)) | (Challenge.description.ilike(like)))
        if tag:
            q = q.join(Challenge.tags).filter(Tag.name == tag)

        total = q.count()
        items = (
            q.order_by(Challenge.points.desc())
             .offset(max(0, (page - 1) * page_size))
             .limit(page_size)
             .all()
        )
        return PaginatedChallengesType(items=items, total=total)

    def resolve_conversationCategories(self, info) -> List[str]:
        rows = (
            db.session.query(SupportConversation.category)
            .distinct()
            .order_by(SupportConversation.category.asc())
            .all()
        )
        return [r[0] for r in rows if r[0]]

    def resolve_assignedUsers(self, info):
        rows = (
            db.session.query(User)
            .join(SupportConversation, SupportConversation.assigned_to_user_id == User.id)
            .distinct()
            .order_by(User.username.asc())
            .all()
        )
        return rows
