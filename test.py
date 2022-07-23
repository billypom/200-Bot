format_list = [1, 2, 3, 5, 5]

max_val = max(format_list)
ind = [i for i, v in enumerate(format_list) if v == max_val]

print(ind)
