// Simple bridge so any part of the app can ask for an API access token.


let getter: (() => Promise<string | null>) | null = null;

export function setAuthTokenGetter(fn: () => Promise<string | null>) {
  getter = fn;
}

export async function getAccessToken(): Promise<string | null> {
  return getter ? getter() : null;
}
