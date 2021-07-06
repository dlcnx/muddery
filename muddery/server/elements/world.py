"""
Area

Areas are compose the whole map. Rooms are belongs to areas.

"""

from evennia.utils import logger
from muddery.server.elements.base_element import BaseElement
from muddery.server.mappings.element_set import ELEMENT
from muddery.server.database.worlddata.world_areas import WorldAreas
from muddery.server.database.worlddata.worlddata import WorldData
from muddery.server.utils.localized_strings_handler import _


class MudderyWorld(BaseElement):
    """
    The whole world which contains all areas.
    """
    element_type = "WORLD"
    element_name = _("World", "elements")

    def load_data(self, key, level=None):
        """
        Load the object's data.

        :arg
            key: (string) the key of the data.
            level: (int) element's level.

        :return:
        """
        # Load data.
        self.load_areas()

    def load_areas(self):
        """
        Load all areas.
        """
        records = WorldAreas.all()
        models = ELEMENT("AREA").get_models()
        self.all_areas = {}

        # self.all_rooms {
        #   room's key: area's key
        # }
        self.room_dict = {}
        for record in records:
            area_data = WorldData.get_tables_data(models, record.key)
            area_data = area_data[0]

            new_area = ELEMENT("AREA")()
            new_area.setup_element(area_data.key)

            self.all_areas[new_area.get_element_key()] = new_area

            rooms_key = new_area.get_rooms_key()
            for key in rooms_key:
                self.room_dict[key] = area_data.key

    def get_room(self, room_key):
        """
        Get a room by its key.
        :param room_key:
        :return:
        """
        area_key = self.room_dict[room_key]
        return self.all_areas[area_key].get_room(room_key)

    def get_area_by_room(self, room_key):
        """
        Get the room's area.
        :param room_key:
        :return:
        """
        area_key = self.room_dict[room_key]
        return self.all_areas[area_key]
