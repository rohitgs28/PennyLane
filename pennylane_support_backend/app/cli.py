import json
from datetime import datetime
import click
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.extensions import db
from app.models.challenge import (
    Challenge,
    Tag,
    ChallengeHint,
    LearningObjective,
    ChallengeTag,
)
from app.models.support import (
    SupportConversation,
    ConversationPost,
)

# ---------- helpers ----------

def _chunks(iterable, size=1000):
    buf = []
    for item in iterable:
        buf.append(item)
        if len(buf) >= size:
            yield buf
            buf = []
    if buf:
        yield buf

def _parse_iso(ts: str | None):
    if not ts:
        return None
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except Exception:
        return None

# ---------- core loaders ----------

def _seed_challenges_from_json(path: str, chunk_size: int = 1000):
    click.echo(f"Loading challenges JSON from: {path}")
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)

    items = raw.get("coding_challenges", [])
    if not items:
        click.echo("No 'coding_challenges' found. Skipping.")
        return

    # Tags
    tag_names = set()
    for c in items:
        for t in c.get("tags", []):
            tag_names.add(t.strip())

    if tag_names:
        tag_rows = [{"name": n} for n in tag_names if n]
        for batch in _chunks(tag_rows, chunk_size):
            stmt = pg_insert(Tag.__table__).values(batch)
            stmt = stmt.on_conflict_do_nothing(index_elements=["name"])
            db.session.execute(stmt)

    tag_map = dict(db.session.execute(select(Tag.name, Tag.id)).all())

    # Challenges
    challenge_rows = []
    for c in items:
        challenge_rows.append({
            "public_id": c["challenge_id"],
            "title": c.get("title"),
            "description": c.get("description"),
            "category": c.get("category"),
            "difficulty": c.get("difficulty"),
            "points": c.get("points") or 0,
        })

    for batch in _chunks(challenge_rows, chunk_size):
        stmt = pg_insert(Challenge.__table__).values(batch)
        stmt = stmt.on_conflict_do_update(
            index_elements=["public_id"],
            set_={
                "title": stmt.excluded.title,
                "description": stmt.excluded.description,
                "category": stmt.excluded.category,
                "difficulty": stmt.excluded.difficulty,
                "points": stmt.excluded.points,
            },
        )
        db.session.execute(stmt)

    chall_map = dict(db.session.execute(select(Challenge.public_id, Challenge.id)).all())

    # Learning objectives & hints
    lo_rows, hint_rows = [], []
    for c in items:
        cid = chall_map.get(c["challenge_id"])
        if not cid:
            continue
        for lo in c.get("learning_objectives", []):
            if lo:
                lo_rows.append({"challenge_id": cid, "text": lo})
        for h in c.get("hints", []):
            if h:
                hint_rows.append({"challenge_id": cid, "text": h})

    for batch in _chunks(lo_rows, chunk_size):
        db.session.execute(LearningObjective.__table__.insert(), batch)
    for batch in _chunks(hint_rows, chunk_size):
        db.session.execute(ChallengeHint.__table__.insert(), batch)

    # Challenge-Tag m2m
    ct_rows = []
    for c in items:
        cid = chall_map.get(c["challenge_id"])
        if not cid:
            continue
        for tname in c.get("tags", []):
            tid = tag_map.get(tname)
            if tid:
                ct_rows.append({"challenge_id": cid, "tag_id": tid})

    for batch in _chunks(ct_rows, chunk_size):
        stmt = pg_insert(ChallengeTag.__table__).values(batch)
        stmt = stmt.on_conflict_do_nothing(index_elements=["challenge_id", "tag_id"])
        db.session.execute(stmt)

    db.session.commit()
    click.echo(
        f"Challenges: {len(challenge_rows)} upserted | Tags: {len(tag_names)} "
        f"| LOs: {len(lo_rows)} | Hints: {len(hint_rows)}"
    )

def _seed_conversations_from_json(path: str, chunk_size: int = 1000):
    click.echo(f"Loading conversations JSON from: {path}")
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)

    items = raw.get("support_conversations", [])
    if not items:
        click.echo("No 'support_conversations' found. Skipping.")
        return

    chall_map = dict(db.session.execute(select(Challenge.public_id, Challenge.id)).all())

    conv_rows = []
    for c in items:
        conv_rows.append({
            "identifier": c.get("identifier"),
            "topic": c.get("topic"),
            "category": c.get("category"),
            "status": c.get("status", "OPEN"),
            "challenge_id": chall_map.get(c.get("challenge_id")),
        })

    for batch in _chunks(conv_rows, chunk_size):
        stmt = pg_insert(SupportConversation.__table__).values(batch)
        stmt = stmt.on_conflict_do_update(
            index_elements=["identifier"],
            set_={
                "topic": stmt.excluded.topic,
                "category": stmt.excluded.category,
                "status": stmt.excluded.status,
                "challenge_id": stmt.excluded.challenge_id,
            },
        )
        db.session.execute(stmt)

    conv_map = dict(
        db.session.execute(
            select(SupportConversation.identifier, SupportConversation.id)
        ).all()
    )

    posts = []
    for c in items:
        conv_id = conv_map.get(c.get("identifier"))
        if not conv_id:
            continue
        for p in c.get("posts", []):
            posts.append({
                "conversation_id": conv_id,
                "author_display_name": p.get("user"),
                "content": p.get("content"),
                "created_at": _parse_iso(p.get("timestamp")),
            })

    for batch in _chunks(posts, chunk_size):
        db.session.execute(ConversationPost.__table__.insert(), batch)

    db.session.commit()
    click.echo(f"Conversations: {len(conv_rows)} upserted | Posts: {len(posts)} inserted")

# ---------- public CLI ----------

def register_cli(app):
    @app.cli.command("seed-challenges")
    @click.argument("challenges_json", type=click.Path(exists=True))
    @click.option("--chunk", default=1000, help="Batch size for bulk operations")
    def seed_challenges_cmd(challenges_json, chunk):
        with app.app_context():
            _seed_challenges_from_json(challenges_json, chunk)

    @app.cli.command("seed-conversations")
    @click.argument("conversations_json", type=click.Path(exists=True))
    @click.option("--chunk", default=1000, help="Batch size for bulk operations")
    def seed_conversations_cmd(conversations_json, chunk):
        with app.app_context():
            _seed_conversations_from_json(conversations_json, chunk)

    @app.cli.command("seed-json")
    @click.argument("challenges_json", type=click.Path(exists=True))
    @click.argument("conversations_json", type=click.Path(exists=True))
    @click.option("--chunk", default=1000, help="Batch size for bulk operations")
    def seed_all_cmd(challenges_json, conversations_json, chunk):
        with app.app_context():
            _seed_challenges_from_json(challenges_json, chunk)
            _seed_conversations_from_json(conversations_json, chunk)
