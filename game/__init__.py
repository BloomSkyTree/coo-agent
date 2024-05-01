from loguru import logger

from game.GameManager import GameManager

games = {}


def get_game(game_id, resource_root_path="files", reload=False):
    game_resources_root_path = resource_root_path + "/" + game_id
    if game_id not in games or reload:
        logger.info(f"从文件系统中加载游戏：{game_id}")
        games[game_id] = GameManager(game_resources_root_path)
    return games[game_id]
