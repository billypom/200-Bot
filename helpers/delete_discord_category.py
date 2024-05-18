from discord import CategoryChannel
import logging


async def delete_discord_category(client, category_id):
    category = client.get_channel(category_id)
    if category and isinstance(category, CategoryChannel):
        try:
            await category.delete()
            logging.info(f"Category {category_id} deleted successfully.")
            return True
        except Exception as e:
            logging.info(f"Failed to delete category {category_id}: {e}")
            return False
    else:
        logging.info(f"Category {category_id} not found or is not a category.")
        return False
