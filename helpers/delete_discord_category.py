from discord import CategoryChannel


async def delete_discord_category(client, category_id):
    """Deletes a discord category.
    Returns true on success, false on failure"""
    category = client.get_channel(category_id)
    if category and isinstance(category, CategoryChannel):
        try:
            await category.delete()
            return True
        except Exception:
            return False
    else:
        return False
