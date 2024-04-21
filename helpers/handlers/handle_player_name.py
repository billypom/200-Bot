from helpers.getters import get_random_name
from helpers import jp_kr_romanize
import logging
from constants import ALLOWED_CHARACTERS
import DBA


async def handle_player_name(name: str) -> str | None:
    """Takes in a name, outputs a cleaned name (for database utf-8 and whatever)

    Returns the new name if OK
    Returns None if bad"""
    logging.info(f"handle_player_name | Step 1 - Handling name: [{name}]")
    insert_name = ""
    logging.info(f"insert_name = {insert_name}")
    # Romanize the text
    try:
        insert_name = await jp_kr_romanize(name)
    except Exception as e:
        print("FDSJFKSDJFKDJLFJSDLKFJSDLJFSDJFLKSDJLF")
        print(e)
        return None
    logging.info(f"handle_player_name | Step 2 - romanized name: [{insert_name}]")
    # Handle name too long
    if len(insert_name) > 16:
        temp_name = ""
        count = 0
        for char in insert_name:
            if count == 15:
                break
            temp_name += char
            count += 1
        insert_name = temp_name
    logging.info(f"handle_player_name | Step 3 - checked length: [{insert_name}]")
    # Handle ä-type characters (delete them)
    allowed_name = ""
    for char in insert_name:
        if char.lower() in ALLOWED_CHARACTERS:
            allowed_name += char
        else:
            allowed_name += ""
    logging.info(f"handle_player_name | Step 4 - handled chars: [{allowed_name}]")
    insert_name = allowed_name
    # Handle empty name
    if not insert_name:
        insert_name = await get_random_name()
    logging.info(f"handle_player_name | Step 5 - handled empty: [{insert_name}]")
    # Handle whitespace name  - generate a random name lol
    if insert_name.isspace():
        insert_name = await get_random_name()
    logging.info(f"handle_player_name | Step 6 - handled whitespace: [{insert_name}]")
    # Handle duplicate names - append underscores
    name_still_exists = True
    count = 0
    while name_still_exists:
        with DBA.DBAccess() as db:
            temp = db.query(
                "SELECT player_name FROM player WHERE player_name = %s;", (insert_name,)
            )
        if temp:
            insert_name += "_"
        else:
            name_still_exists = False
        count += 1
        if count == 16:
            insert_name = await get_random_name()
    logging.info(f"handle_player_name | Step 7 - handled duplicates: [{insert_name}]")
    return str(insert_name).replace(" ", "-")
