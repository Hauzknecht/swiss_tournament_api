import random
from models import MatchModel

"""functions returns list of (player_id, player_name, player score, player omw and player ogw)"""
def calculate_score_omw_ogw(player, matches):
    total_opponents_mwr = 0
    total_opponents_gwr = 0
    total_opponents = 0
    for match in matches:
        if player.id == match.player1_id:
            total_opponents_mwr += match.player2.match_winrate
            total_opponents_gwr += match.player2.game_winrate
            total_opponents += 1
        if player.id == match.player2_id:
            total_opponents_mwr += match.player1.match_winrate
            total_opponents_gwr += match.player1.game_winrate
            total_opponents += 1
    if total_opponents == 0:
        return player.id, player.name, player.score, 0, 0
    omw = total_opponents_mwr / total_opponents
    ogw = total_opponents_gwr / total_opponents
    return player.id, player.name, player.score, omw, ogw


def score_board(tournament):
    players = tournament.players
    players_score = []
    for player in players:
        if player.name != "BYE":
            players_score.append(calculate_score_omw_ogw(player, tournament.matches))
    """Players are sorting by score, omw, gwp descending"""
    sorted_players = sorted(players_score, key=lambda x: (x[2], x[3], x[4]), reverse=True)
    return sorted_players
    
def played_together(player1_id, player2_id, tournament_id):
    match = MatchModel.query.filter(((MatchModel.player1_id == player1_id) & (MatchModel.player2_id == player2_id) & (MatchModel.tournament_id == tournament_id)) | ((MatchModel.player1_id == player2_id) & (MatchModel.player2_id == player1_id) & (MatchModel.tournament_id == tournament_id))).first()
    return match is not None

def pairings(tournament):
    players = list(tournament.players)
    standings = score_board(tournament)
    if tournament.is_finished:
        return [], standings
    if tournament.current_round == 1:
        pairs = []
        if players[-1].name == "BYE":
            bye_player = players.pop(len(players)-1)
            random.shuffle(players)
            bye_opponent = players.pop(0)
            pairs.append({
                "player1_id" : bye_opponent.id,
                "player1_name" : bye_opponent.name,
                "player2_id" : bye_player.id,
                "player2_name" : bye_player.name,
            })       
        random.shuffle(players)
        pairs += [{"player1_id" : players[i].id,
                  "player1_name" : players[i].name,
                  "player2_id" : players[i+1].id,
                  "player2_name" : players[i+1].name,}
                  for i in range(0, len(players), 2)]        
    else:
        unmatched = list(standings)
        pairs = []
        while len(unmatched)>1:
            player1 = unmatched.pop(0)
            for i, player in enumerate(unmatched):
                if not played_together(player1[0], player[0], tournament.id):
                    pairs.append({
                        "player1_id": player1[0],
                        "player1_name": player1[1],
                        "player2_id": player[0],
                        "player2_name": player[1]
                    })
                    unmatched.pop(i)
                    break    
        if len(unmatched)==1:
              bye_player = players[len(players)-1]
              bye_opponent = unmatched.pop(0)
              pairs.insert(0,{
                        "player1_id": bye_opponent[0],
                        "player1_name": bye_opponent[1],
                        "player2_id": bye_player.id,
                        "player2_name": bye_player.name
                    })
    return pairs, standings



        
