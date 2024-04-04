from helpers import countries
import logging


async def iso_country_to_emoji(iso_code: str) -> str:
    """Given an Alpha-2 ISO country code, returns the corresponding emoji flag"""
    try:
        emoji_flag = countries.country_to_emoji.get(iso_code, "")
        return emoji_flag
    except Exception as e:
        logging.info(
            f"iso_country_to_emoji | could not retrieve country flag. iso code = {iso_code} | {e}"
        )
        return ""
