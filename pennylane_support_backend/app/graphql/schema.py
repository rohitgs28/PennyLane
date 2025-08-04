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
    sync_user = SyncUser.Field()
    createConversation = CreateConversation.Field()
    addPost = AddPost.Field()
    assignConversation = AssignConversation.Field()        
    updateConversationStatus = UpdateConversationStatus.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)
