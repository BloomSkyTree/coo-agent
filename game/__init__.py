from loguru import logger

from game.GameManager import GameManager

games = {}


def get_game(game_id, resource_root_path):
    game_resources_root_path = resource_root_path + "/" + game_id
    if game_id not in games:
        logger.info(f"加载游戏：{game_id}")
        games[game_id] = GameManager(game_resources_root_path)
    else:
        logger.info(f"游戏已加载：{game_id}")
    return games[game_id]
