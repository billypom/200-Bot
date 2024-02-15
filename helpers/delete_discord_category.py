from discord import CategoryChannel

async def delete_discord_category(client, category_id):
    category = client.get_channel(category_id)
    if category and isinstance(category, CategoryChannel):
        try:
            await category.delete()
            print(f"Category {category_id} deleted successfully.")
            return True
        except Exception as e:
            print(f"Failed to delete category {category_id}: {e}")
            return False
    else:
        print(f"Category {category_id} not found or is not a category.")
        return False