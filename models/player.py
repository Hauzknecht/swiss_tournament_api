from db import db


class PlayerModel(db.Model):
    __tablename__ = "players"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    score = db.Column(db.Integer, default=0)
    games_played = db.Column(db.Integer, default=0)
    games_winned = db.Column(db.Integer, default=0)
    matches_played = db.Column(db.Integer, default=0)
    matches_winned = db.Column(db.Float, default=0.0)

    tournament_id = db.Column(db.Integer, db.ForeignKey("tournaments.id"), unique=False, nullable=False)

    tournament = db.relationship("TournamentModel", back_populates="players")

    @property
    def match_winrate(self):
        if self.name == "BYE": return 0.5
        if self.matches_played == 0: return 0
        return self.matches_winned/self.matches_played
    
    @property
    def game_winrate(self):
        if self.name == "BYE": return 0.5
        if self.games_played == 0: return 0
        return self.games_winned/self.games_played