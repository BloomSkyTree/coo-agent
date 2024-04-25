import os

from agentscope.agents import UserAgent

from outdated.singleton import character_outlook_agent
from characters.NonPlayerCharacter import NonPlayerCharacter


def load_non_player_characters(config_root_path):
    non_player_characters = {}
    folder_path = config_root_path + "/characters/non_player_characters"
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.yaml') or file.endswith('.yml'):
                file_path = os.path.join(root, file)
                npc = NonPlayerCharacter(config_path=file_path)
                non_player_characters[npc.get_name()] = npc
    return non_player_characters

def test_chat_with_npc(npc):
    x = None
    user = UserAgent()
    while True:
        x = user(x)
        x = npc(x)

if __name__ == '__main__':
    npc_dict = load_non_player_characters("../files")
    alice = npc_dict["Alice"]
    character_outlook_agent(alice.get_outlook())
    test_chat_with_npc(alice)
