import {
  ApolloClient,
  InMemoryCache,
  HttpLink,
  ApolloLink,
  from,
} from '@apollo/client';

/* In-memory token that other modules can mutate ------------------ */
export let accessToken: string | null = null;
export const setAccessToken = (token: string | null) => {
  accessToken = token;
};

/* HTTP transport ------------------------------------------------- */
const httpLink = new HttpLink({
  uri:
    process.env.NEXT_PUBLIC_GRAPHQL_ENDPOINT ??
    'https://pennylane-support-api/graphql',
  credentials: 'include',
});

/* Auth link – inject header if we have a token ------------------- */
const authLink = new ApolloLink((operation, forward) => {
  if (accessToken) {
    operation.setContext(({ headers = {} }) => ({
      headers: { ...headers, Authorization: `Bearer ${accessToken}` },
    }));
  }
  return forward(operation);
});

export const apolloClient = new ApolloClient({
  cache: new InMemoryCache(),
  link: from([authLink, httpLink]), 
});
