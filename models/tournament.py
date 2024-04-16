from db import db
from sqlalchemy.sql import func

class TournamentModel(db.Model):
    __tablename__ = "tournaments"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    created = db.Column(db.DateTime(timezone=True), server_default=func.now())
    number_of_rounds = db.Column(db.Integer, nullable=False)
    current_round = db.Column(db.Integer, nullable=False)
    is_finished = db.Column(db.Boolean, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=False, nullable=False)

    user = db.relationship("UserModel", back_populates="tournaments")
    players = db.relationship("PlayerModel", back_populates="tournament", lazy="dynamic", cascade="all, delete")
    matches = db.relationship("MatchModel", back_populates="tournament", lazy="dynamic", cascade="all, delete")