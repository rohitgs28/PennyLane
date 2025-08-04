from __future__ import annotations

import graphene
from app.extensions import db
from app.models.user import User

class SyncUser(graphene.Mutation):
    """Upsert a user by auth0Id.

    Args (GraphQL):
        email: User's email address.
        username: Display username.
        auth0Id: Auth0 subject identifier for the user.

    Returns:
        ok: Boolean indicating success.
    """

    class Arguments:
        email = graphene.String(required=True)
        username = graphene.String(required=True)
        auth0Id = graphene.String(required=True)

    ok = graphene.Boolean()

    def mutate(self, info, email: str, username: str, auth0Id: str):
        user = User.query.filter_by(auth0_id=auth0Id).first()
        if not user:
            user = User(email=email, username=username, auth0_id=auth0Id)
            db.session.add(user)
        else:
            user.email = email
            user.username = username

        db.session.commit()
        return SyncUser(ok=True)
