import json


def _post_graphql(client, query, variables=None, operation_name=None):
    """
    Helper to send a GraphQL request to the Flask test client.  Mirrors the
    helper in test_graphql.py but duplicated here to avoid cross‑importing.
    """
    return client.post(
        "/graphql",
        data=json.dumps({
            "query": query,
            "variables": variables,
            "operationName": operation_name,
        }),
        content_type="application/json",
    )


def test_create_conversation_captures_author_display_name(client):
    """
    Creating a conversation with a first post should capture the provided
    authorDisplayName on the post so that the backend stores the display
    name even when no user is authenticated.  This ensures the UI can
    display the correct name for the first message in a conversation.
    """
    mutation = """
    mutation CreateConversation($challengePublicId: String!, $topic: String!, $category: String, $firstPost: String, $authorDisplayName: String) {
      createConversation(
        challengePublicId: $challengePublicId,
        topic: $topic,
        category: $category,
        firstPost: $firstPost,
        authorDisplayName: $authorDisplayName
      ) {
        ok
        conversation {
          id
          topic
          posts { id authorDisplayName content }
        }
      }
    }
    """
    variables = {
        "challengePublicId": "CHAL_TEST",
        "topic": "Test Topic",
        "category": "PennyLane Help",
        "firstPost": "Hello world",
        "authorDisplayName": "Alice",
    }
    resp = _post_graphql(client, mutation, variables)
    assert resp.status_code == 200
    payload = resp.get_json()
    assert "errors" not in payload
    conv_data = payload["data"]["createConversation"]
    assert conv_data["ok"] is True
    conversation = conv_data["conversation"]
    # verify the topic matches what was passed
    assert conversation["topic"] == "Test Topic"
    # verify a first post was created and the authorDisplayName is captured
    posts = conversation.get("posts", [])
    assert posts, "Expected a first post to be created"
    assert posts[0]["authorDisplayName"] == "Alice"
    assert posts[0]["content"] == "Hello world"


def test_add_post_records_author_display_name(client):
    """
    Adding a post to an existing conversation should record the given
    authorDisplayName.  This test creates a conversation without a
    firstPost, then adds a reply and verifies the reply is stored with
    the provided display name.
    """
    # First, create a conversation with no initial post
    create_mutation = """
    mutation CreateConversation($challengePublicId: String!, $topic: String!, $category: String) {
      createConversation(
        challengePublicId: $challengePublicId,
        topic: $topic,
        category: $category
      ) {
        ok
        conversation { id }
      }
    }
    """
    create_vars = {
        "challengePublicId": "CHAL_TEST_2",
        "topic": "Another Topic",
        "category": "General",
    }
    resp = _post_graphql(client, create_mutation, create_vars)
    assert resp.status_code == 200
    payload = resp.get_json()
    conv_id = payload["data"]["createConversation"]["conversation"]["id"]
    # Then add a post
    add_post_mutation = """
    mutation AddPost($conversationId: Int!, $content: String!, $authorDisplayName: String) {
      addPost(
        conversationId: $conversationId,
        content: $content,
        authorDisplayName: $authorDisplayName
      ) {
        ok
        post { id authorDisplayName content }
      }
    }
    """
    add_post_vars = {
        "conversationId": conv_id,
        "content": "Reply message",
        "authorDisplayName": "Bob",
    }
    resp2 = _post_graphql(client, add_post_mutation, add_post_vars)
    assert resp2.status_code == 200
    payload2 = resp2.get_json()
    assert "errors" not in payload2
    post_data = payload2["data"]["addPost"]["post"]
    assert post_data["authorDisplayName"] == "Bob"
    assert post_data["content"] == "Reply message"
    # Finally, query the conversation to ensure the post shows up
    query = """
    query GetConversation($id: Int!) {
      conversation(id: $id) {
        id
        posts { id authorDisplayName content }
      }
    }
    """
    resp3 = _post_graphql(client, query, {"id": conv_id})
    assert resp3.status_code == 200
    conv_payload = resp3.get_json()
    posts = conv_payload["data"]["conversation"]["posts"]
    # there should be exactly one post for this conversation and it should match
    assert len(posts) == 1
    assert posts[0]["authorDisplayName"] == "Bob"
    assert posts[0]["content"] == "Reply message"