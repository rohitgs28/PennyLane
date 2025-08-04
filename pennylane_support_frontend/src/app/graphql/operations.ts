import { gql } from '@apollo/client';

export const USER_FIELDS = gql`
  fragment UserFields on UserType {
    id
    username
    email
  }
`;

export const CONVERSATION_FIELDS = gql`
  fragment ConversationFields on SupportConversationType {
    id
    identifier
    topic
    category
    status
    createdAt
    challenge {
      id
      title
    }
    assignedSupport {            
      ...UserFields
    }
    posts {
      id
      content
      authorDisplayName
      createdAt
    }
  }
  ${USER_FIELDS}
`;

export const GET_CONVERSATION = gql`
  query GetConversation($id: Int!) {
    conversation(id: $id) {
      ...ConversationFields
    }
  }
  ${CONVERSATION_FIELDS}
`;

export const GET_CHALLENGE = gql`
  query GetChallenge($publicId: String!) {
    challenge(publicId: $publicId) {
      id
      title
      description
      category
      difficulty
      points
      assignedSupport {   
        id
        username
        email
      }
      conversations {
        ...ConversationFields
      }
    }
  }
  ${CONVERSATION_FIELDS}
`;

export const LIST_CONVERSATIONS_PAGED = gql`
  query ListConversationsPaged(
    $search: String
    $status: String
    $category: String
    $challengePublicId: String
    $assignedToUserId: Int
    $page: Int!
    $pageSize: Int!
  ) {
    conversationsPaged(
      search: $search
      status: $status
      category: $category
      challengePublicId: $challengePublicId
      assignedToUserId: $assignedToUserId
      page: $page
      pageSize: $pageSize
    ) {
      total
      items {
        ...ConversationFields
      }
    }
  }
  ${CONVERSATION_FIELDS}
`;

export const GET_CONVERSATION_CATEGORIES = gql`
  query GetConversationCategories {
    conversationCategories
  }
`;

export const GET_ASSIGNED_USERS = gql`
  query GetAssignedUsers {
    assignedUsers {
      ...UserFields
    }
  }
  ${USER_FIELDS}
`;

export const ASSIGN_CONVERSATION = gql`
  mutation AssignConversation($conversationId: Int!) {
    assignConversation(conversationId: $conversationId) {
      ok
      conversation {
        id
        status
        assignedSupport { ...UserFields }
      }
    }
  }
  ${USER_FIELDS}
`;

export const CREATE_CONVERSATION = gql`
  mutation CreateConversation(
    $challengePublicId: String!
    $topic: String!
    $category: String
    $firstPost: String
    $authorDisplayName: String
  ) {
    createConversation(
      challengePublicId: $challengePublicId
      topic: $topic
      category: $category
      firstPost: $firstPost
      authorDisplayName: $authorDisplayName
    ) {
      ok
      conversation { id }
    }
  }
`;

export const ADD_POST = gql`
  mutation AddPost(
    $conversationId: Int!
    $content: String!
    $authorDisplayName: String
  ) {
    addPost(
      conversationId: $conversationId
      content: $content
      authorDisplayName: $authorDisplayName
    ) {
      ok
      post { id }
    }
  }
`;

export const CHALLENGE_CARD_FIELDS = gql`
  fragment ChallengeCardFields on ChallengeType {
    id
    publicId
    title
    description
    category
    difficulty
    points
    tags { id name }
  }
`;

export const LIST_CHALLENGES_PAGED = gql`
  query ListChallengesPaged(
    $search: String
    $tag: String
    $page: Int!
    $pageSize: Int!
  ) {
    challengesPaged(
      search: $search
      tag: $tag
      page: $page
      pageSize: $pageSize
    ) {
      total
      items {
        ...ChallengeCardFields
      }
    }
  }
  ${CHALLENGE_CARD_FIELDS}
`;


export const SYNC_USER = gql`
  mutation SyncUser($e: String!, $n: String!) {
  syncUser(email: $e, name: $n) {
    ok
    user { id email name }
  }
}

`;
