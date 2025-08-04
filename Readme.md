
# PennyLane Support Platform

A full-stack sample assignment that demonstrates how to build a **support conversation platform** for PennyLane.  
Users can browse coding challenges, ask questions in a support forum, and agents can reply and manage conversations.

---

## Tech Stack

| Layer       | Location                        | Tech                                                |
|-------------|---------------------------------|-----------------------------------------------------|
| **Frontend**| `src/`                          | Next.js · React · TypeScript · Chakra UI · Apollo Client |
| **Backend** | `app/`                          | Flask · GraphQL (graphene) · SQLAlchemy · PostgreSQL/ |
| **Auth**    | —                               | Auth0 (SPA & M2M/Web Applications)                  |

---

## Prerequisites

- **Node.js** ≥ 18 .x and **npm** / Yarn  
- **Python** 3.10+  
- A relational database ( PostgreSQL recommended)  
- An **Auth0** tenant with:
  - One **Single Page Application** (Frontend)
  - One **Machine-to-Machine** or **Regular Web** Application (Backend)
  - One **API** (e.g. `https://pennylane.support/api`)

---

## Auth0 Configuration

### Applications
| Type | What to copy | Where it goes |
|------|--------------|---------------|
| **SPA (frontend)** | `client_id` | `NEXT_PUBLIC_AUTH0_CLIENT_ID` in `.env.local` |
| **M2M / Regular Web (backend)** | `client_id` & `client_secret` | `.env` for the backend |

---

### API
- **Identifier**: `https://pennylane.support/api`  
- Enable the **Offline Access** scope if you need refresh tokens.

---

### Roles
1. Create a role called **`support_admin`** (or `site_admin`).
2. Assign that role to your support-agent users.

---

### Post-Login Action (optional)

```js
// Auth0 Action: onExecutePostLogin
exports.onExecutePostLogin = async (event, api) => {
  const roles = event.authorization?.roles || [];
  api.idToken.setCustomClaim('roles', roles);
};



## Backend (set‑up on macOS)

```bash
# 1) clone & enter
git clone https://github.com/rohitgs28/PennyLane.git
cd PennyLane/pennylane_support_backend

# 2) create & activate venv
python3 -m venv venv
source venv/bin/activate

# 3) install deps
pip install --upgrade pip
pip install -r requirements.txt -v --no-cache-dir --default-timeout=100
```

> **PostgreSQL PATH** (EnterpriseDB install):

```bash
echo 'export PATH="/Library/PostgreSQL/15/bin:$PATH"' >> ~/.zprofile
source ~/.zprofile
```

### Database

```bash
# 5) create DB  (change port if not 5432)
createdb -U postgres -p 5432 db_pennylane
```

### Environment

Create **`.env`** (Unix LF endings):

```dotenv
FLASK_ENV=development
FLASK_APP=wsgi.py

# Database (choose one)
DATABASE_URL=sqlite:///db.sqlite3
# DATABASE_URL=postgresql://postgres:<password>@localhost:5432/db_pennylane

# Auth0
AUTH0_DOMAIN=your-tenant.eu.auth0.com
AUTH0_AUDIENCE=https://pennylane.support/api
AUTH0_CLIENT_ID=<backend-client-id>
AUTH0_CLIENT_SECRET=<backend-client-secret>
JWT_ALGORITHMS=RS256

SECRET_KEY=change-me
```

### Migrations & Seeding

```bash
# 7) run migrations
flask db migrate -m "Initial schema"
flask db upgrade

# 8) seed data
flask --app wsgi.py seed-json   pennylane_coding_challenges.json   pennylane_support_conversations.json

# Expected output
# Challenges: 30 upserted | Tags: 76 | LOs: 90 | Hints: 90
# Conversations: 60 upserted | Posts: 182 inserted
```

---

## Frontend (local dev)

```bash
cd src
cp .env.local.example .env.local       # create your file

# .env.local
NEXT_PUBLIC_AUTH0_DOMAIN=your-tenant.eu.auth0.com
NEXT_PUBLIC_AUTH0_CLIENT_ID=<frontend-client-id>
NEXT_PUBLIC_AUTH0_AUDIENCE=https://pennylane.support/api
NEXT_PUBLIC_AUTH0_REDIRECT_URI=http://localhost:3000/auth/callback
NEXT_PUBLIC_API_URL=http://localhost:5000/graphql
```

```bash
npm install       
npm run dev          # starts http://localhost:3000
```

---

## Auth0 Configuration

1. **Applications**
   - **SPA (frontend)** – copy `client_id` → `NEXT_PUBLIC_AUTH0_CLIENT_ID`
   - **M2M / Regular Web (backend)** – copy credentials into backend `.env`
2. **API**
   - Identifier: `https://pennylane.support/api`
   - Enable **Offline Access** scope if you need refresh tokens
3. **Roles**
   - Create `support_admin` (or `site_admin`)
   - Assign it to agent users
   - Optional **Post-Login Action** to inject roles into the ID token:

```js
// Auth0 Action: onExecutePostLogin
exports.onExecutePostLogin = async (event, api) => {
  const roles = event.authorization?.roles || [];
  api.idToken.setCustomClaim('roles', roles);
};
```

`roles.includes('support_admin')` lets the frontend show assignment controls.


## License

MIT © PennyLane
