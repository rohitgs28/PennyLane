import json

def _post_graphql(client, query, variables=None, operation_name=None):
    return client.post(
        "/graphql",
        data=json.dumps({"query": query, "variables": variables, "operationName": operation_name}),
        content_type="application/json",
    )

def test_empty_challenges_paged(client):
    # Use camelCase for GraphQL argument names (Graphene auto-camelcases).
    query = """
    query {
      challengesPaged(page: 1, pageSize: 5) {
        total
        items { publicId title }
      }
    }
    """
    resp = _post_graphql(client, query)
    assert resp.status_code == 200
    payload = resp.get_json()
    assert "data" in payload
    assert payload["data"]["challengesPaged"]["total"] == 0
    assert payload["data"]["challengesPaged"]["items"] == []

def test_sync_user_mutation(client):
    # Mutations and fields are camelCase in the GraphQL API.
    mutation = """
    mutation SyncUser($email: String!, $username: String!, $auth0Id: String!) {
      syncUser(email: $email, username: $username, auth0Id: $auth0Id) {
        ok
      }
    }
    """
    variables = {"email": "a@example.com", "username": "alice", "auth0Id": "auth0|123"}
    resp = _post_graphql(client, mutation, variables)
    assert resp.status_code == 200
    body = resp.get_json()
    assert "data" in body and "errors" not in body
    data = body["data"]["syncUser"]
    assert data["ok"] is True
