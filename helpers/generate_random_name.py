import random
import string
# Returns a random string of length 9
async def generate_random_name():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=9))