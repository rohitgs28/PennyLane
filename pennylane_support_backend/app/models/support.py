from app.extensions import db

class SupportConversation(db.Model):
    __tablename__ = "support_conversations"

    id = db.Column(db.Integer, primary_key=True)
    identifier = db.Column(db.String(32), unique=True, nullable=False, index=True)  # e.g. "CONV_001"
    topic = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(100), index=True)

    status = db.Column(db.String(20), nullable=False, default="OPEN", index=True)      # OPEN | ASSIGNED | RESOLVED | CLOSED
    priority = db.Column(db.String(20), nullable=True, index=True)                     # LOW | MEDIUM | HIGH (optional)

    challenge_id = db.Column(db.Integer, db.ForeignKey("challenges.id", ondelete="SET NULL"), index=True)
    challenge = db.relationship("Challenge", back_populates="conversations")

    created_by_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True, index=True)
    assigned_to_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True, index=True)

    created_at = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now(), nullable=False)

    posts = db.relationship("ConversationPost", back_populates="conversation", cascade="all, delete-orphan", order_by="ConversationPost.created_at")

class ConversationPost(db.Model):
    __tablename__ = "conversation_posts"
    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey("support_conversations.id", ondelete="CASCADE"), index=True)
    conversation = db.relationship("SupportConversation", back_populates="posts")

    author_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True, index=True)
    author_display_name = db.Column(db.String(120), nullable=True)  # for imported/anonymous posts
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)
