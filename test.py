import csv

f = open('./200lounge.csv',encoding='utf-8-sig') # f is our filename as string
lines = list(csv.reader(f,delimiter=',')) # lines contains all of the rows from the csv
f.close()
for line in lines:
    print(line)