"""
Default condition scripts are in this model.
Condition script functions must be compatible with this:

def func(character, obj, *args)
    args:
        character(object): a player character.
        obj(object): the player character's action target.
        args: other args.

The return value must be a boolean value.

"""

def example(caller, obj, *args):
    """
    This is an example.
    """
    return True


def is_quest_in_progress(character, obj, *args):
    """
    If the character is doing specified quest.
    args: quest's key
    """
    if not character:
        return False

    if not args:
        return False

    return character.quest.is_in_progress(args[0])


def can_provide_quest(character, obj, *args):
    """
    If can provide specified quest to the character.
    args: quest's key
    """
    if not character:
        return False

    if not args:
        return False

    return character.quest.can_provide(args[0])


def is_quest_finished(character, obj, *args):
    """
    If specified quest is finished.
    args: quest's key
    """
    if not character:
        return False

    if not args:
        return False

    return character.quest.is_finished(args[0])


def have_object(character, obj, *args):
    """
    If the character has specified object.
    args: object's key
    """
    for item in character.contents:
        if item.get_info_key() == args[0]:
            return True
    return False
