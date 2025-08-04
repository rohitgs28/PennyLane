
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from app.extensions import db

class Challenge(db.Model):
    __tablename__ = "challenges"

    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(80), unique=True, nullable=False) 
    title = db.Column(db.String, nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String, nullable=False)
    difficulty = db.Column(db.String)
    points = db.Column(db.Integer)
    assigned_support_user_id = db.Column(db.Integer, ForeignKey('users.id'), nullable=True)

    # Relationship to assigned support user
    assigned_support = relationship('User', backref='assigned_challenges')


    created_at = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now(), nullable=False)

    # children
    hints = db.relationship("ChallengeHint", back_populates="challenge", cascade="all, delete-orphan")
    learning_objectives = db.relationship("LearningObjective", back_populates="challenge", cascade="all, delete-orphan")
    tags = db.relationship("Tag", secondary="challenge_tags", back_populates="challenges")
    conversations = db.relationship("SupportConversation", back_populates="challenge")

class ChallengeHint(db.Model):
    __tablename__ = "challenge_hints"
    id = db.Column(db.Integer, primary_key=True)
    challenge_id = db.Column(db.Integer, db.ForeignKey("challenges.id", ondelete="CASCADE"), index=True)
    text = db.Column(db.Text, nullable=False)
    challenge = db.relationship("Challenge", back_populates="hints")

class LearningObjective(db.Model):
    __tablename__ = "learning_objectives"
    id = db.Column(db.Integer, primary_key=True)
    challenge_id = db.Column(db.Integer, db.ForeignKey("challenges.id", ondelete="CASCADE"), index=True)
    text = db.Column(db.Text, nullable=False)
    challenge = db.relationship("Challenge", back_populates="learning_objectives")

class Tag(db.Model):
    __tablename__ = "tags"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False, index=True)
    challenges = db.relationship("Challenge", secondary="challenge_tags", back_populates="tags")

class ChallengeTag(db.Model):
    __tablename__ = "challenge_tags"
    challenge_id = db.Column(db.Integer, db.ForeignKey("challenges.id", ondelete="CASCADE"), primary_key=True)
    tag_id = db.Column(db.Integer, db.ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True)
