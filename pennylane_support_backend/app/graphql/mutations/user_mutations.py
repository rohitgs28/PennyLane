
from __future__ import annotations

import graphene

from app.extensions import db
from app.models.user import User
from app.graphql.types import UserType


class SyncUser(graphene.Mutation):
    """Create or update a User.  Makes name optional so tests can omit it."""

    class Arguments:
        email = graphene.String(required=True)
        username = graphene.String(required=True)
        auth0_id = graphene.String(required=True)
        name = graphene.String() 

    ok = graphene.Boolean()
    user = graphene.Field(UserType)

    def mutate(self, info,
               email: str,
               username: str,
               auth0_id: str,
               name: str | None = None) -> "SyncUser":
        # Default name to the username if not provided
        resolved_name = name or username

        # Look up existing user by email; update or create accordingly
        user = User.query.filter_by(email=email).one_or_none()
        if user:
            user.username = username
            user.auth0_id = auth0_id
            user.name = resolved_name
        else:
            user = User(
                email=email,
                username=username,
                auth0_id=auth0_id,
                name=resolved_name,
                roles=[],  
            )
            db.session.add(user)

        db.session.commit()
        return SyncUser(ok=True, user=user)
