import graphene
from .queries import Query
from .mutations.user_mutations import SyncUser
from .mutations.conversation_mutations import (
    CreateConversation,
    AddPost,
    AssignConversation,
    UpdateConversationStatus,
)

class Mutation(graphene.ObjectType):
    syncUser = SyncUser.Field()
    createConversation = CreateConversation.Field()
    addPost = AddPost.Field()
    assignConversation = AssignConversation.Field()          # ← returns convo now
    updateConversationStatus = UpdateConversationStatus.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)
