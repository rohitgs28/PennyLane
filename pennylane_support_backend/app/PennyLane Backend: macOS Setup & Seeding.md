PennyLane Backend: macOS Setup & Seeding Guide
0) Prereqs
Python 3.10+

PostgreSQL installed (EnterpriseDB GUI or Postgres.app)

Git

1) Clone & enter the backend

git clone https://github.com/rohitgs28/PennyLane.git
cd PennyLane/pennylane_support_backend
2) Create & activate a virtualenv

python3 -m venv venv
source venv/bin/activate
3) Install dependencies (with useful flags)

pip install --upgrade pip
pip install -r requirements.txt -v --no-cache-dir --default-timeout=100
4) Configure PostgreSQL CLI (only if psql/createdb not found)
EnterpriseDB GUI install (most likely in your case):

echo 'export PATH="/Library/PostgreSQL/15/bin:$PATH"' >> ~/.zprofile
source ~/.zprofile

Verify:

which psql
which createdb
5) Create the database
Use your actual port . If you’re on default, it’s 5432.

createdb -U postgres -p 5432 db_pennylane

(If prompted for password, use the one you set during install.)

6) Configure environment variables
Create .env (Unix line endings; avoid ^M):


FLASK_ENV=development
FLASK_APP=wsgi.py

# Choose the correct port (5433 in your case)
DATABASE_URL=postgresql://postgres:postgres@localhost:5433/db_pennylane
AUTH0_DOMAIN=dev-zby4ebj6iuuyhfqd.us.auth0.com
API_IDENTIFIER=https://pennylane-support-api
ALGORITHMS=RS256
AUTH0_NAMESPACE=https://pennylane.app/



Run migrations

flask db migrate -m "Initial schema"
flask db upgrade
10) Seed the database
From project root (you used these exact files):


flask --app wsgi.py seed-json pennylane_coding_challenges.json pennylane_support_conversations.json
You should see a summary like:


Challenges: 30 upserted | Tags: 76 | LOs: 90 | Hints: 90
Conversations: 60 upserted | Posts: 182 inserted
