from marshmallow import Schema, fields

class PlainTournamentSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    created = fields.DateTime(dump_only=True)
    number_of_rounds = fields.Int()
    current_round = fields.Int(dump_only=True)
    is_finished = fields.Boolean(dump_only=True)

class PlainUserSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str(required=True)
    password = fields.Str(required=True, load_only=True)

class PlainPlayerSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    games_played = fields.Int(dump_only=True)
    games_winned = fields.Int(dump_only=True)
    matches_played = fields.Int(dump_only=True)
    matches_winned = fields.Float(dump_only=True)
    match_winrate = fields.Float(dump_only=True)
    game_winrate = fields.Float(dump_only=True)

class PlainMatchSchema(Schema):
    id = fields.Int(dump_only=True)
    round_number = fields.Int(dump_only=True)
    player1_id = fields.Int(required=True, load_only=True)
    player2_id = fields.Int(required=True, load_only=True)
    player1_name = fields.Str(dump_only=True)
    player2_name = fields.Str(dump_only=True)
    player1_points = fields.Int(required=True)
    player2_points = fields.Int(required=True)

class UserSchema(PlainUserSchema):
    tournaments = fields.List(fields.Nested(PlainTournamentSchema()), dump_only=True)

class TournamentSchema(PlainTournamentSchema):
    user_id = fields.Int(dump_only=True)
    user = fields.Nested(PlainUserSchema(), dump_only=True )
    players = fields.List(fields.Nested(PlainPlayerSchema()), required=True)
    matches = fields.List(fields.Nested(PlainMatchSchema()), dump_only=True)

class MatchSchema(PlainMatchSchema):
    tournament_id = fields.Int(dump_only=True)
    tournament = fields.Nested(PlainTournamentSchema(), dump_only=True)
    player1 = fields.Nested(PlainPlayerSchema(), dump_only=True)
    player2 = fields.Nested(PlainPlayerSchema(), dump_only=True)

class PlayerSchema(PlainPlayerSchema):
    tournament_id = fields.Int(load_only=True, required=True)
    tournament = fields.Nested(PlainTournamentSchema(), dump_only=True)