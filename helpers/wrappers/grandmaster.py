# helpers/grandmaster_wrapper.py

async def grandmaster(input):
    # return (f'[0;2m[0;40m[0;31m{input}[0m[0;40m[0m[0m')
    return (f'<span foreground="DarkRed">{input}</span>')