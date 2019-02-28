"""
Battle commands. They only can be used when a character is in a combat.
"""

from __future__ import print_function

import json
from django.conf import settings
from evennia.utils import logger
from evennia.server.sessionhandler import SESSIONS
from muddery.worlddata.services import data_query, data_edit, general_query
from muddery.utils.exception import MudderyError, ERR
from muddery.worlddata.utils.response import success_response
from muddery.utils.builder import build_all
from muddery.utils.game_settings import GAME_SETTINGS
from muddery.worlddata.controllers.base_request_processer import BaseRequestProcesser
from muddery.worlddata.dao import general_query_mapper
from muddery.mappings.typeclass_set import TYPECLASS


class QueryFields(BaseRequestProcesser):
    """
    Query all fields of a table.

    Args:
        None.
    """
    path = "query_fields"
    name = ""

    def func(self, args, request):
        if 'table' not in args:
            raise MudderyError(ERR.missing_args, 'Missing the argument: "table".')

        table_name = args["table"]

        data = general_query.query_fields(table_name)
        return success_response(data)


class QueryTable(BaseRequestProcesser):
    """
    Query all records of a table.

    Args:
        None.
    """
    path = "query_table"
    name = ""

    def func(self, args, request):
        if 'table' not in args:
            raise MudderyError(ERR.missing_args, 'Missing the argument: "table".')

        table_name = args["table"]

        data = general_query.query_table(table_name)
        return success_response(data)


class QueryTypeclassTable(BaseRequestProcesser):
    """
    Query a table of objects of the same typeclass.

    Args:
        typeclass: (string) typeclass's key.
    """
    path = "query_typeclass_table"
    name = ""

    def func(self, args, request):
        if 'typeclass' not in args:
            raise MudderyError(ERR.missing_args, 'Missing the argument: "typeclass".')

        typeclass_key = args["typeclass"]

        # Query data.
        data = data_query.query_typeclass_table(typeclass_key)
        return success_response(data)


class QueryRecord(BaseRequestProcesser):
    """
    Query a record of a table.

    Args:
        table: (string) table's name.
        record: (string) record's id.
    """
    path = "query_record"
    name = ""

    def func(self, args, request):
        if ('table' not in args) or ('record' not in args):
            raise MudderyError(ERR.missing_args, 'Missing arguments.')

        table_name = args["table"]
        record_id = args["record"]

        data = general_query.query_record(table_name, record_id)
        return success_response(data)


class QueryAreas(BaseRequestProcesser):
    """
    Query all available areas.

    Args:
        None.
    """
    path = "query_areas"
    name = ""

    def func(self, args, request):
        data = data_query.query_areas()
        return success_response(data)


class QueryObjectEvents(BaseRequestProcesser):
    """
    Query all events of the given object.

    Args:
        object: (string) object's key
    """
    path = "query_object_events"
    name = ""

    def func(self, args, request):
        if 'object' not in args:
            raise MudderyError(ERR.missing_args, 'Missing arguments.')

        object_key = args["object"]

        data = data_query.query_object_events(object_key)
        return success_response(data)


class QueryEventActionData(BaseRequestProcesser):
    """
    Query an event action's data.

    Args:
        type: (string) action's type
        key: (string) event's key
    """
    path = "query_event_action_data"
    name = ""

    def func(self, args, request):
        if 'type' not in args or 'key' not in args:
            raise MudderyError(ERR.missing_args, 'Missing arguments.')

        action_type = args["type"]
        event_key = args["key"]

        data = data_query.query_event_action_data(action_type, event_key)
        return success_response(data)


class QueryDialogueSentences(BaseRequestProcesser):
    """
    Query a dialogue's sentences.

    Args:
        key: (string) dialogue's key
    """
    path = "query_dialogue_sentences"
    name = ""

    def func(self, args, request):
        if 'dialogue' not in args:
            raise MudderyError(ERR.missing_args, 'Missing arguments.')

        dialogue_key = args["dialogue"]

        data = data_query.query_dialogue_sentences(dialogue_key)
        return success_response(data)


class QueryForm(BaseRequestProcesser):
    """
    Query a form of a record of a table.

    Args:
        table: (string) table's name
        record: (string, optional) record's id. If it is empty, get a new record.
    """
    path = "query_form"
    name = ""

    def func(self, args, request):
        if 'table' not in args:
            raise MudderyError(ERR.missing_args, 'Missing the argument: "table".')

        table_name = args["table"]
        record = args.get('record', None)

        data = data_edit.query_form(table_name, id=record)
        return success_response(data)


class QueryFormFirstRecord(BaseRequestProcesser):
    """
    Query a form of the first record of a table.

    Args:
        table: (string) table's name
    """
    path = "query_form_first_record"
    name = ""

    def func(self, args, request):
        if 'table' not in args:
            raise MudderyError(ERR.missing_args, 'Missing the argument: "table".')

        table_name = args["table"]

        try:
            record = general_query_mapper.get_the_first_record(table_name)
            if record:
                record_id = record.id
            else:
                record_id = None
        except Exception, e:
            raise MudderyError(ERR.invalid_form, "Wrong table: %s." % table_name)

        data = data_edit.query_form(table_name, id=record_id)
        return success_response(data)


class SaveForm(BaseRequestProcesser):
    """
    Save a form.

    Args:
        values: (dict) values to save.
        table: (string) table's name.
        record: (string, optional) record's id. If it is empty, add a new record.
    """
    path = "save_form"
    name = ""

    def func(self, args, request):
        if not args:
            raise MudderyError(ERR.missing_args, 'Missing arguments.')

        if 'values' not in args:
            raise MudderyError(ERR.missing_args, 'Missing the argument: "values".')

        if 'table' not in args:
            raise MudderyError(ERR.missing_args, 'Missing the argument: "table".')

        values = args["values"]
        table_name = args["table"]
        record_id = args.get('record', None)

        record_id = data_edit.save_form(values, table_name, record_id)
        data = general_query.query_record(table_name, record_id)
        return success_response(data)


class QueryObjectForm(BaseRequestProcesser):
    """
    Query a record of an object which may include several tables.

    Args:
        base_typeclass: (string) candidate typeclass name
        obj_typeclass: (string, optional) object's typeclass name
        obj_key: (string, optional) object's key. If it is empty, get a new object.
    """
    path = "query_object_form"
    name = ""

    def func(self, args, request):
        if not args:
            raise MudderyError(ERR.missing_args, 'Missing arguments.')

        if 'base_typeclass' not in args:
            raise MudderyError(ERR.missing_args, 'Missing the argument: "base_typeclass".')

        base_typeclass = args["base_typeclass"]
        obj_typeclass = args.get('obj_typeclass', None)
        obj_key = args.get('obj_key', None)

        data = data_edit.query_object_form(base_typeclass, obj_typeclass, obj_key)
        return success_response(data)


class QueryMap(BaseRequestProcesser):
    """
    Query the map of an area

    Args:
        area: (string) area's key
    """
    path = "query_map"
    name = ""

    def func(self, args, request):
        if not args:
            raise MudderyError(ERR.missing_args, 'Missing arguments.')

        if 'area' not in args:
            raise MudderyError(ERR.missing_args, 'Missing the argument: "area".')

        area_key = args["area"]

        data = data_query.query_map(area_key)
        return success_response(data)


class SaveObjectForm(BaseRequestProcesser):
    """
    Save a form.

    Args:
        tables: (list) a list of table data.
               [{
                 "table": (string) table's name.
                 "values": (string, optional) record's value.
                }]
        base_typeclass: (string) candidate typeclass name
        obj_typeclass: (string) object's typeclass name
        obj_key: (string) object's key. If it is empty or different from the current object's key, get a new object.
    """
    path = "save_object_form"
    name = ""

    def func(self, args, request):
        if not args:
            raise MudderyError(ERR.missing_args, 'Missing arguments.')

        if 'tables' not in args:
            raise MudderyError(ERR.missing_args, 'Missing the argument: "tables".')

        if 'base_typeclass' not in args:
            raise MudderyError(ERR.missing_args, 'Missing the argument: "base_typeclass".')

        if 'obj_typeclass' not in args:
            raise MudderyError(ERR.missing_args, 'Missing the argument: "obj_typeclass".')

        if 'obj_key' not in args:
            raise MudderyError(ERR.missing_args, 'Missing the argument: "obj_key".')

        tables = args["tables"]
        base_typeclass = args["base_typeclass"]
        obj_typeclass = args["obj_typeclass"]
        obj_key = args["obj_key"]

        obj_key = data_edit.save_object_form(tables, obj_typeclass, obj_key)
        data = data_edit.query_object_form(base_typeclass, obj_typeclass, obj_key)
        return success_response(data)


class SaveNewRoom(BaseRequestProcesser):
    """
    Save a new room.

    Args:
        typeclass: (string) room's typeclass.
        area: (string) room's area.
        position: (string) room's position string.
    """
    path = "save_new_room"
    name = ""

    def func(self, args, request):
        if not args:
            raise MudderyError(ERR.missing_args, 'Missing arguments.')

        if 'typeclass' not in args:
            raise MudderyError(ERR.missing_args, 'Missing the argument: "typeclass".')

        if 'location' not in args:
            raise MudderyError(ERR.missing_args, 'Missing the argument: "location".')

        typeclass = args["typeclass"]
        location = args["location"]
        position = args.get("position", None)
        if position:
            position = json.dumps(position)

        forms = data_edit.query_object_form(typeclass, typeclass, None)
        new_room = []
        for form in forms:
            values = {field["name"]: (field["value"] if "value" in field else "") for field in form["fields"]}
            if "location" in values:
                values["location"] = location
            if "position" in values:
                values["position"] = position

            new_room.append({
                "table": form["table"],
                "values": values
            })

        obj_key = data_edit.save_object_form(new_room, typeclass, "")
        data = {"key": obj_key}
        return success_response(data)


class DeleteRoom(BaseRequestProcesser):
    """
    Delete a room and its exits.

    Args:
        room: (string) room's key.
        exits: (list) a list of exit keys.
    """
    path = "delete_room_exits"
    name = ""

    def func(self, args, request):
        if not args:
            raise MudderyError(ERR.missing_args, 'Missing arguments.')

        if "room" not in args:
            raise MudderyError(ERR.missing_args, 'Missing the argument: "room".')

        if "exits" not in args:
            raise MudderyError(ERR.missing_args, 'Missing the argument: "exits".')

        room = args["room"]
        exits = args["exits"]

        data_edit.delete_object("ROOM", room)
        for exit in exits:
            data_edit.delete_object("EXIT", exit)

        data = {"room": room}
        return success_response(data)


class SaveNewExit(BaseRequestProcesser):
    """
    Save a new exit.

    Args:
        typeclass: (string) the exit's typeclass.
        location: (string) exit's location.
        destination: (string) exit's destination.
    """
    path = "save_new_exit"
    name = ""

    def func(self, args, request):
        if not args:
            raise MudderyError(ERR.missing_args, 'Missing arguments.')

        if 'typeclass' not in args:
            raise MudderyError(ERR.missing_args, 'Missing the argument: "typeclass".')

        if 'location' not in args:
            raise MudderyError(ERR.missing_args, 'Missing the argument: "location".')

        if 'destination' not in args:
            raise MudderyError(ERR.missing_args, 'Missing the argument: "destination".')

        typeclass = args["typeclass"]
        location = args["location"]
        destination = args["destination"]

        forms = data_edit.query_object_form(typeclass, typeclass, None)
        new_exit = []
        for form in forms:
            values = {field["name"]: (field["value"] if "value" in field else "") for field in form["fields"]}
            if "location" in values:
                values["location"] = location
            if "destination" in values:
                values["destination"] = destination

            new_exit.append({
                "table": form["table"],
                "values": values
            })

        print(new_exit)
        obj_key = data_edit.save_object_form(new_exit, typeclass, "")
        data = {"key": obj_key}
        return success_response(data)


class SaveMap(BaseRequestProcesser):
    """
    Save a map.

    Args:
        area: (dict) area's data
              {
                   "key": (string) area's key
                   "background": (string) area's background
                   "width": (number) area's width
                   "height": (number) area's height
              }
        rooms: (dict) rooms positions.
                {
                    "key": (string) room's key
                    "position": (list) room's position
                }
    """
    path = "save_map_positions"
    name = ""

    def func(self, args, request):
        if not args:
            raise MudderyError(ERR.missing_args, 'Missing arguments.')

        if 'area' not in args:
            raise MudderyError(ERR.missing_args, 'Missing the argument: "area".')

        if 'rooms' not in args:
            raise MudderyError(ERR.missing_args, 'Missing the argument: "rooms".')

        area = args["area"]
        rooms = args["rooms"]

        data = data_edit.save_map_positions(area, rooms)
        return success_response(data)


class DeleteRecord(BaseRequestProcesser):
    """
    Delete a record.

    Args:
        table: (string) table's name.
        record: (string) record's id.
    """
    path = "delete_record"
    name = ""

    def func(self, args, request):
        if 'table' not in args:
            raise MudderyError(ERR.missing_args, 'Missing the argument: "table".')

        if 'record' not in args:
            raise MudderyError(ERR.missing_args, 'Missing the argument: "record".')

        table_name = args["table"]
        record_id = args["record"]

        data_edit.delete_record(table_name, record_id)
        data = {"record": record_id}
        return success_response(data)


class DeleteObject(BaseRequestProcesser):
    """
    Delete an object.

    Args:
        base_typeclass: (string) object's base typeclass. Delete all records in all tables under this typeclass.
        obj_key: (string) object's key.
    """
    path = "delete_object"
    name = ""

    def func(self, args, request):
        if 'base_typeclass' not in args:
            raise MudderyError(ERR.missing_args, 'Missing the argument: "base_typeclass".')

        if 'obj_key' not in args:
            raise MudderyError(ERR.missing_args, 'Missing the argument: "obj_key".')

        base_typeclass = args["base_typeclass"]
        obj_key = args["obj_key"]

        data_edit.delete_object(base_typeclass, obj_key)
        data = {"obj_key": obj_key}
        return success_response(data)


class ApplyChanges(BaseRequestProcesser):
    """
    Query all tables' names.

    Args:
        None.
    """
    path = "apply_changes"
    name = ""

    def func(self, args, request):
        try:
            # reload system data
            # import_syetem_data()

            # reload localized strings
            # LOCALIZED_STRINGS_HANDLER.reload()

            # rebuild the world
            build_all()

            # send client settings
            client_settings = GAME_SETTINGS.get_client_settings()
            text = json.dumps({"settings": client_settings})
            SESSIONS.announce_all(text)

            # restart the server
            SESSIONS.announce_all("Server restarting ...")
            SESSIONS.server.shutdown(mode='reload')
        except Exception, e:
            message = "Can not build the world: %s" % e
            logger.log_tracemsg(message)
            raise MudderyError(ERR.build_world_error, message)

        return success_response("success")
