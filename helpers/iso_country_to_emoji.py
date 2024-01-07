from helpers import countries
import logging
# Input: str 2 char iso code
# Output: emoji flag
async def iso_country_to_emoji(iso_code):
    try:
        emoji_flag = countries.country_to_emoji.get(iso_code, "")
        return emoji_flag
    except Exception as e:
        logging.info(f'iso_country_to_emoji | could not retrieve country flag. iso code = {iso_code}')
        return ''