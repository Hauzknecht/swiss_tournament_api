from db import db

class MatchModel(db.Model):
    __tablename__ = "matches"

    id = db.Column(db.Integer, primary_key=True)
    round_number = db.Column(db.Integer, nullable=False)
    player1_id = db.Column(db.Integer, db.ForeignKey("players.id"), nullable=False)
    player1_points = db.Column(db.Integer, nullable=False)
    player1_name = db.Column(db.String(80), nullable=False)
    player2_name = db.Column(db.String(80), nullable=False)
    player2_id = db.Column(db.Integer, db.ForeignKey("players.id"), nullable=False)
    player2_points = db.Column(db.Integer, nullable=False)
    tournament_id = db.Column(db.Integer, db.ForeignKey("tournaments.id"), nullable=False)

    tournament = db.relationship("TournamentModel", back_populates="matches")
    player1 = db.relationship("PlayerModel", foreign_keys=[player1_id])
    player2 = db.relationship("PlayerModel", foreign_keys=[player2_id])
