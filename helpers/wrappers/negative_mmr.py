async def negative_mmr(input):
    """Red negative mmr element for MMR table"""
    # return (f'[0;2m[0;31m{input}[0m[0m')
    return f'<span foreground="Red2">{input}</span>'
