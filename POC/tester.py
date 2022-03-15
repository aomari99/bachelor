import requests
from os import listdir
from os.path import isfile, join
import pandas as pd 
local_files = [f for f in listdir("./testdata/") if isfile(join("./testdata/", f))]

data = []
for i in range(10):
    for j in local_files: 
        print(j)
        url = "http://127.0.0.1:5001/uploadPdf"

        payload={}
        files=[
        ('file',(j,open(join("./testdata/", j),'rb'),'application/pdf'))
        ]
        headers = {}

        response = requests.request("POST", url, headers=headers, data=payload, files=files)

        if(response.status_code == 200):
            datas = response.json()
            data.append((j,datas["calc_time"] , len (datas["Entitys"]), len (datas["Sims"]),i))

print(data)
dataframe = pd.DataFrame(data) 
dataframe.to_csv(r"results.csv",index=None)