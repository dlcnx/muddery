"""
QuestHandler handles a character's quests.
"""

import weakref
from muddery.server.utils.logger import logger
from muddery.server.statements.statement_handler import STATEMENT_HANDLER
from muddery.server.utils.localized_strings_handler import _
from muddery.server.utils.exception import MudderyError
from muddery.server.utils.game_settings import GameSettings
from muddery.server.database.worlddata.worlddata import WorldData
from muddery.server.database.worlddata.quest_dependencies import QuestDependencies
from muddery.server.mappings.quest_status_set import QUEST_STATUS_SET
from muddery.server.mappings.element_set import ELEMENT
from muddery.server.database.gamedata.character_quests import CharacterQuests
from muddery.server.utils.utils import async_wait, async_gather


class QuestHandler(object):
    """
    Handles a character's quests.
    """

    def __init__(self, owner):
        """
        Initialize handler
        """
        self.owner = weakref.proxy(owner)
        self.quests = {}

    async def init(self):
        """
        Initial setup.
        """
        await self.load_quests()

    async def load_quests(self):
        """
        Load character's quests.
        :return:
        """
        self.quests = await CharacterQuests.inst().get_character(self.owner.get_db_id())
        if self.quests:
            await async_wait([self.create_quest(key) for key in self.quests if not self.quests[key]["finished"]])

    async def accept(self, quest_key):
        """
        Accept a quest.

        Args:
            quest_key: (string) quest's key

        Returns:
            None
        """
        all_quests = await CharacterQuests.inst().get_character(self.owner.get_db_id())
        if quest_key in all_quests:
            return

        # Create quest object.
        quest = await self.create_quest(quest_key)
        await CharacterQuests.inst().add(self.owner.get_db_id(), quest_key)

        await self.owner.msg({"msg": _("Accepted quest {C%s{n.") % quest.get_name()})
        await self.show_quests()
        await self.owner.show_location()
        
    async def remove_all(self):
        """
        Remove all quests.
        
        It will be called when quests' owner will be deleted.
        """
        self.quests = {}
        await CharacterQuests.inst().remove_character(self.owner.get_db_id())

    async def give_up(self, quest_key):
        """
        Accept a quest.

        Args:
            quest_key: (string) quest's key

        Returns:
            None
        """
        if not GameSettings.inst().get("can_give_up_quests"):
            logger.log_trace("Can not give up quests.")
            raise MudderyError(_("Can not give up this quest."))

        quest = await CharacterQuests.inst().get_quest(self.owner.get_db_id(), quest_key)
        if not quest or quest["finished"]:
            raise MudderyError("Can not find this quest.")

        await CharacterQuests.inst().remove_quest(self.owner.get_db_id(), quest_key)
        if quest_key in self.quests:
            del self.quests[quest_key]

        await self.show_quests()

    async def turn_in(self, quest_key):
        """
        Turn in a quest.

        Args:
            quest_key: (string) quest's key

        Returns:
            None
        """
        quest_info = await CharacterQuests.inst().get_quest(self.owner.get_db_id(), quest_key)
        if not quest_info or quest_info["finished"]:
            raise MudderyError("Can not find this quest.")

        quest = await self.get_quest(quest_key)
        if not await quest.is_accomplished():
            raise MudderyError(_("Can not turn in this quest."))

        # Call turn in function in the quest.
        await quest.turn_in(self.owner)
        await CharacterQuests.inst().set(self.owner.get_db_id(), quest_key, {"finished": True})

        # Get quest's name.
        name = quest.get_name()

        await self.owner.msg({"msg": _("Turned in quest {C%s{n.") % name})
        await self.show_quests()
        await self.owner.show_status()
        await self.owner.show_location()

    async def is_accomplished(self, quest_key):
        """
        All objectives of this quest are accomplished.

        Args:
            quest_key: (string) quest's key

        Returns:
            None
        """
        if not await self.is_in_progress(quest_key):
            return False

        return await self.quests[quest_key]["obj"].is_accomplished()

    async def is_not_accomplished(self, quest_key):
        """
        Whether the character accomplished this quest or not.

        Args:
            quest_key: (string) quest's key

        Returns:
            None
        """
        if not await self.is_in_progress(quest_key):
            return False

        return not await self.quests[quest_key]["obj"].is_accomplished()

    async def is_finished(self, quest_key):
        """
        Whether the character finished this quest or not.

        Args:
            quest_key: (string) quest's key

        Returns:
            None
        """
        all_quests = await CharacterQuests.inst().get_character(self.owner.get_db_id())
        if quest_key not in all_quests:
            return False

        return all_quests[quest_key]["finished"]

    async def is_in_progress(self, quest_key):
        """
        If the character is doing this quest.

        Args:
            quest_key: (string) quest's key

        Returns:
            None
        """
        all_quests = await CharacterQuests.inst().get_character(self.owner.get_db_id())
        if quest_key not in all_quests:
            return False

        if all_quests[quest_key]["finished"]:
            return False

        return True

    async def can_provide(self, quest_key):
        """
        If can provide this quest to the owner.

        Args:
            quest_key: (string) quest's key

        Returns:
            None
        """
        if await self.is_finished(quest_key):
            return False

        if await self.is_in_progress(quest_key):
            return False

        if not await self.match_dependencies(quest_key):
            return False

        if not await self.match_condition(quest_key):
            return False

        return True

    async def match_dependencies(self, quest_key):
        """
        Check quest's dependencies

        Args:
            quest_key: (string) quest's key

        Returns:
            (boolean) result
        """
        dependencies = QuestDependencies.get(quest_key)
        if dependencies:
            results = await async_gather([
                QUEST_STATUS_SET.get(dep.type).match(self.owner, dep.dependency) for dep in dependencies
            ])
        else:
            return True

        return min(results)

    async def match_condition(self, quest_key):
        """
        Check if the quest matches its condition.
        Args:
            quest_key: (string) quest's key

        Returns:
            (boolean) result
        """
        # Get quest's record.
        model_name = ELEMENT("QUEST").model_name
        if not model_name:
            return False

        try:
            record = WorldData.get_table_data(model_name, key=quest_key)
            record = record[0]
            return await STATEMENT_HANDLER.match_condition(record.condition, self.owner, None)
        except Exception as e:
            logger.log_err("Can't get quest %s's condition: %s" % (quest_key, e))
        return False

    async def show_quests(self):
        """
        Send quests to player.
        """
        quests = await self.return_quests()
        await self.owner.msg({"quests": quests})

    async def return_quests(self):
        """
        Get quests' data.
        """
        all_quests = await CharacterQuests.inst().get_character(self.owner.get_db_id())
        not_finished = [key for key, info in all_quests.items() if not info["finished"]]
        if not_finished:
            quest_objects = await async_gather([self.get_quest(key) for key in not_finished])
            quests_info = await async_gather([quest.return_info() for quest in quest_objects])
        else:
            quests_info = []

        return quests_info

    async def at_objective(self, object_type, object_key, number=1):
        """
        Called when the owner may complete some objectives.
        Call relative hooks.

        Args:
            object_type: (type) objective's type
            object_key: (string) object's key
            number: (int) objective's number

        Returns:
            None
        """
        status_changed = False

        # Get unfinished quests.
        all_quests = await CharacterQuests.inst().get_character(self.owner.get_db_id())
        not_finished = [key for key, info in all_quests.items() if not info["finished"]]
        if not_finished:
            # Check objectives.
            quest_objects = await async_gather([self.get_quest(key) for key in not_finished])
            results = await async_gather([quest.at_objective(object_type, object_key, number) for quest in quest_objects])
            objective_changed = [quest for index, quest in enumerate(quest_objects) if results[index]]

            if objective_changed:
                status_changed = True

                # Check if quest is accomplished.
                accomplished = await async_gather([quest.is_accomplished() for quest in objective_changed])
                quest_names = [quest.get_name() for index, quest in enumerate(quest_objects) if accomplished[index]]
                
                if quest_names:
                    # Notify the player.
                    await self.owner.msg([
                        {"msg": _("Quest {C%s{n's goals are accomplished.") % n} for n in quest_names
                    ])

        if status_changed:
            await self.show_quests()

    async def create_quest(self, quest_key):
        """
        Get a quest object by its key.
        :param quest_key:
        :return:
        """
        quest = ELEMENT("QUEST")()
        await quest.setup_element(quest_key)
        quest.set_character(self.owner.get_db_id())
        self.quests[quest_key] = {
            "obj": quest
        }

        return quest

    async def get_quest(self, quest_key):
        """
        Get a quest object by its key.
        :param quest_key:
        :return:
        """
        if quest_key in self.quests:
            quest = self.quests[quest_key]["obj"]
        else:
            quest = await self.create_quest(quest_key)

        return quest

    async def get_quest_info(self, quest_key):
        """
        Get a quest's detail information.
        :param quest_key:
        :return:
        """
        all_quests = await CharacterQuests.inst().get_character(self.owner.get_db_id())
        if all_quests[quest_key]["finished"]:
            logger.log_err("%s's quest %s is finished." % (self.owner.get_db_id(), quest_key))
            return

        quest = await self.get_quest(quest_key)
        return await quest.return_info()
