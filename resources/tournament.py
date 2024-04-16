from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity

from db import db
from models import TournamentModel, PlayerModel, MatchModel
from schemas import TournamentSchema, MatchSchema
from logic import pairings

blp = Blueprint("Tournaments", "tournaments", description="Operations on tournaments.")

@blp.route("/tournament")
class TournamentList(MethodView):
    """
    Creates new tournament with given players.
    """
    @jwt_required()
    @blp.arguments(TournamentSchema)
    @blp.response(201, TournamentSchema)
    @blp.alt_response(500, description="An error occured while creating a tournament or player.")
    @blp.alt_response(400, description="Number of players can't be greater or equal to number of rounds.")
    def post(self, tournament_data):
        current_user = get_jwt_identity()
        new_tournament = TournamentModel(
            user_id = current_user,
            name = tournament_data["name"],
            number_of_rounds = tournament_data["number_of_rounds"],
            current_round = 1,
            is_finished = False
        )

        if(len(tournament_data["players"]) <= tournament_data["number_of_rounds"]):
            abort(400, "Number of players can't be greater or equal to number of rounds.")
        
        try:
            db.session.add(new_tournament)
            db.session.commit()
        except:
            abort(500, "An error occured while creating a tournament.")
        print("tournament created.")

        for player_data in tournament_data["players"]:
            new_player = PlayerModel(
                name=player_data["name"],
                tournament_id=new_tournament.id,
                tournament=new_tournament
            )
            try:
                db.session.add(new_player)
                db.session.commit()
            except:
                db.session.delete(new_tournament)
                db.session.commit()
                abort(500, "An error occured while inserting player to tournament.")
        if len(tournament_data["players"])%2 == 1:
            bye_player = PlayerModel(
                name="BYE",
                tournament_id = new_tournament.id,
                tournament = new_tournament
            )
            db.session.add(bye_player)
            db.session.commit()
            
        return new_tournament

    """get all torunaments of player"""
    @jwt_required()
    @blp.response(200, TournamentSchema(many=True))
    def get(self):
        current_user = get_jwt_identity()
        return TournamentModel.query.filter(TournamentModel.user_id==current_user)
    
@blp.route("/tournament/<int:tournament_id>")
class Tournament(MethodView):

    """Get details of single tournament"""
    @jwt_required()
    @blp.response(200, TournamentSchema)
    @blp.alt_response(401, description="Unathorized. You are not owner")
    def get(self,tournament_id):
        current_user = get_jwt_identity()
        tournament = TournamentModel.query.get_or_404(tournament_id)
        if tournament.id != current_user:
            abort(401, "Only owner can request tournament information.")
        return tournament
    
    """Delete tournament"""
    @jwt_required(refresh=True)
    def delete(self, tournament_id):
        current_user = get_jwt_identity()
        tournament = TournamentModel.query.get_or_404(tournament_id)
        if tournament.id != current_user:
            abort(401, "Only owner can delete tournament.")
        db.session.delete(tournament)
        db.session.commit()
        return {"message": "Tournament deleted"}, 200
    
@blp.route("/tournament/<int:tournament_id>/round")
class Round(MethodView):

    """Report round consisting of matches"""
    @jwt_required()
    @blp.arguments(MatchSchema(many=True))
    def post(self, matches_data, tournament_id):
        current_user = get_jwt_identity()
        tournament = TournamentModel.query.get_or_404(tournament_id)
        if tournament.id != current_user:
            abort(401, "Only owner can submit round results.")
        
        for match in matches_data:
            player1_id = match["player1_id"]
            player2_id = match["player2_id"]
            player1_points = match["player1_points"]
            player2_points = match["player2_points"]
            if not PlayerModel.query.filter_by(id=player1_id, tournament_id=tournament_id) or not PlayerModel.query.filter_by(id=player2_id, tournament_id=tournament_id):
                abort(404, "One or both players not found in tournament.")
            new_match = MatchModel(
                player1_id=player1_id,
                player2_id=player2_id,
                player1_points=player1_points,
                player2_points=player2_points,
                tournament_id=tournament_id,
                round_number = tournament.current_round,
                tournament = tournament
            )
            try:
                db.session.add(new_match)
                db.session.commit()
            except:
                abort(500, "An error occured while reporting match.")
            
            games_count = player1_points+player2_points
            player1 = PlayerModel.query.get(player1_id)
            player2 = PlayerModel.query.get(player2_id)
            player1.games_played += games_count
            player2.games_played += games_count
            player1.games_winned += player1_points
            player2.games_winned += player2_points
            player1.matches_played += 1
            player2.matches_played += 1
            if player1_points == player2_points:
                player1.matches_winned += 0.5
                player2.matches_winned += 0.5
                player1.score += 1
                player2.score += 1
            elif player1_points>player2_points:
                player1.matches_winned += 1
                player1.score +=3
            else:
                player2.matches_winned += 1
                player2.score += 3
            
            db.session.add(player1)
            db.session.add(player2)
            db.session.commit()
        
        tournament.current_round += 1
        if tournament.current_round == tournament.number_of_rounds+1:
            tournament.is_finished=True
        db.session.add(tournament)
        db.session.commit()
        
        return {"message": "Round reported."}
    
    """Get pairings for next round"""
    @jwt_required()
    def get(self, tournament_id):
        current_user = get_jwt_identity()
        tournament = TournamentModel.query.get_or_404(tournament_id)
        if tournament.id != current_user:
            abort(401, "Only owner can submit round results.")
        
        pairs, standings = pairings(tournament)
        if len(pairs)!=0:
            if pairs[0]["player2_name"] == "BYE":
                new_match = MatchModel(
                    player1_id=pairs[0]["player1_id"],
                    player2_id=pairs[0]["player2_id"],
                    player1_points=1,
                    player2_points=0,
                    tournament_id=tournament_id,
                    round_number = tournament.current_round+1
                )
                player_with_bye = PlayerModel.query.filter_by(id=pairs[0]["player1_id"], tournament_id=tournament_id).first()
                player_with_bye.games_played += 1
                player_with_bye.games_winned += 1
                player_with_bye.matches_played += 1
                player_with_bye.matches_winned += 1
                player_with_bye.score += 3
                db.session.add(player_with_bye)
                db.session.add(new_match)
                db.session.commit()

        return {"pairings": pairs, "standings": standings}
        
