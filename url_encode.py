import urllib.parse
import shutil
import requests

query = '''1
popuko [us] 50
brandon [us] 50

2
popuko [] 60
brandon [de] 60

3
jpgiviner [nl] 70
wanap [jp] 70
'''

my_string = urllib.parse.quote(query)
other_id = 123456789456123456
author_id = 166818526768791552
url = f'https://gb.hlorenzi.com/table.png?data={my_string}'
response = requests.get(url, stream=True)
with open(f'{hex(author_id)}table.png', 'wb') as out_file:
    shutil.copyfileobj(response.raw, out_file)
del response