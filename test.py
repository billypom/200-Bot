insert_name = "abcdefghijklopqrstuv4890128490843809"

if len(insert_name) > 16:
    temp_name = ""
    count = 0
    for char in insert_name:
        if count == 16:
            break
        temp_name+=char
        count+=1
    insert_name = temp_name
print(insert_name)