import pykakasi
from korean_romanizer.romanizer import Romanizer
text = "Deshawn-Marcus"

r = Romanizer(text)
kr_result = r.romanize()
kks = pykakasi.kakasi()
result = kks.convert(kr_result)
my_string = ""
for item in result:
    my_string+=item['hepburn']
print(my_string)