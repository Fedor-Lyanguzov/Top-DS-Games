import os
import zipfile
import csv

res = []
zips = os.listdir('Nintendo DS')
for z in zips:
    with zipfile.ZipFile('Nintendo DS/'+z) as myzip:
        info = myzip.infolist()
        for i in info:
            res.append([z, i.filename, int(i.file_size/(1024**2))])

with open('archive.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerows(res)
