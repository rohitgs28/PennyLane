import graphene                                  
from app.graphql.types import UserType
from app.extensions import db
from app.models.user import User
class SyncUser(graphene.Mutation):
    class Arguments:
        email     = graphene.String(required=True)
        name      = graphene.String(required=True)
        username  = graphene.String()       
        auth0_id  = graphene.String()          

    ok   = graphene.Boolean()
    user = graphene.Field(UserType)

    def mutate(self, info, email, name, username=None, auth0_id=None):
        username = username or email.split("@")[0]

        user = User.query.filter_by(email=email).one_or_none()
        if user:
            user.name     = name
            user.username = username
            if auth0_id:
                user.auth0_id = auth0_id
        else:
            user = User(
                email=email,
                name=name,
                username=username,
                auth0_id=auth0_id or username,   
                roles=[],                       
            )
            db.session.add(user)

        db.session.commit()
        return SyncUser(ok=True, user=user)
