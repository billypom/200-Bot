# Input: list()
# Output: Boolean
async def check_for_dupes_in_list(my_list):
    if len(my_list) == len(set(my_list)):
        return False
    else:
        return True