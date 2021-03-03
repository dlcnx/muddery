
from muddery.server.database import gamedata_models as BaseModels


# ------------------------------------------------------------
#
# Object's element key.
#
# ------------------------------------------------------------
class object_keys(BaseModels.object_keys):
    pass


# ------------------------------------------------------------
#
# Game object's runtime attributes.
#
# ------------------------------------------------------------
class object_status(BaseModels.object_status):
    pass


# ------------------------------------------------------------
#
# player character's data
#
# ------------------------------------------------------------
class player_character(BaseModels.player_character):
    """
    Character's data.
    """
    pass


# ------------------------------------------------------------
#
# player character's quests
#
# ------------------------------------------------------------
class character_quests(BaseModels.character_quests):
    """
    Character's quests.
    """
    pass


# ------------------------------------------------------------
#
# player character's quests
#
# ------------------------------------------------------------
class quest_objectives(BaseModels.quest_objectives):
    """
    Quests' objectives.
    """
    pass


# ------------------------------------------------------------
#
# The game's runtime data.
#
# ------------------------------------------------------------
class honours(BaseModels.honours):
    """
    Character's honour data.
    """
    pass
