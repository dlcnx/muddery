"""
Characters' skills.
"""

import json, traceback
from collections import OrderedDict, deque
from django.apps import apps
from django.conf import settings
from muddery.server.utils.exception import MudderyError, ERR
from muddery.server.database.storage.kv_table import KeyValueTable
from muddery.server.database.storage.kv_table_write_back import KeyValueWriteBackTable


class CharacterSkills(object):
    """
    Player character's skills data, including which skills a player character has, skill's level and other data.
    """
    def __init__(self, model_name):
        # db model
        self.model_name = model_name
        self.model = apps.get_model(settings.GAME_DATA_APP, model_name)
        self.storage = KeyValueTable(model_name, "character_id", "skill")

    def save(self, character_id, skill_key, data):
        """
        Set an attribute.

        Args:
            character_id: (number) character's id.
            skill_key: (string) skill's key.
            data: (dict) data to save.
        """
        self.storage.save_dict(character_id, skill_key, data)

    def has(self, character_id, skill_key):
        """
        Check if the skill exists.

        Args:
            character_id: (number) character's id.
            skill_key: (string) skill's key.
        """
        return self.storage.has(character_id, skill_key)

    def load(self, character_id, skill_key, **default):
        """
        Get the value of a skill.

        Args:
            character_id: (number) character's id.
            skill_key: (string) skill's key.
            default: (any or none) default value.

        Raises:
            AttributeError: If `raise_exception` is set and no matching Attribute
                was found matching `key` and no default value set.
        """
        return self.storage.load_dict(character_id, skill_key, **default)

    def load_character(self, character_id):
        """
        Get all skills of a character.

        Args:
            character_id: (number) character's id.
        """
        return self.storage.load_category_dict(character_id)

    def delete(self, character_id, skill_key):
        """
        delete a skill of a character.

        Args:
            character_id: (number) character's id.
            skill_key: (string) skill's key.
        """
        self.storage.delete(character_id, skill_key)

    def remove_character(self, character_id):
        """
        Remove all skills of a character.

        Args:
            character_id: (number) character's id.
        """
        self.storage.delete_category(character_id)


CHARACTER_SKILLS = CharacterSkills("character_skills")
