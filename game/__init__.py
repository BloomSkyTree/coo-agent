from game.GameManager import GameManager

games = {}


def get_game(game_id, resource_root_path):
    game_resources_root_path = resource_root_path + "/" + game_id
    if game_id not in games:
        games[game_id] = GameManager(game_resources_root_path)
    return games[game_id]
