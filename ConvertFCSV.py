import os
from utils import SaveJsonFromFcsv, search
from ManageJson import MergeJson
import pandas as pd
import numpy as np


if __name__ == "__main__":
    df = pd.read_excel("/home/luciacev/Desktop/Luc/DATA/ASO/Accuracy/Maxillary/FCSV/DylandCorrespondance.xlsx")
    Corresp = {df['Patients'][i]:df['Type'][i].split(' ')[0] for i in range(len(df['Type']))}
    dir_name = "/home/luciacev/Desktop/Luc/DATA/ASO/Accuracy/Maxillary/FCSV/"
    out_dir = "/home/luciacev/Desktop/Luc/DATA/ASO/Accuracy/Maxillary/JSON/"

    files = search(dir_name, ".fcsv")[".fcsv"]

    for file in files:
        # print(file)
        # if "T1" in file:
        #     outpath = os.path.join(out_dir,file.split("/")[-4], "T1", "_".join(file.split("/")[-3].split(" ")) +"_"+ file.split("/")[-1].split(".")[0] + ".mrk.json")
        # if "T2" in file:
        #     outpath = os.path.join(out_dir,file.split("/")[-4], "T2", "_".join(file.split("/")[-3].split(" ")) +"_"+ file.split("/")[-1].split(".")[0] + ".mrk.json")
            
        # if not os.path.exists(os.path.dirname(outpath)):
        #     os.makedirs(os.path.dirname(outpath))
        outpath = os.path.join(out_dir,os.path.basename(file).replace(".fcsv","_lm.mrk.json"))
        SaveJsonFromFcsv(file,outpath,Corresp[os.path.basename(file).split('.')[0]])
        # print(outpath)
        # break
    
    # MergeJson(out_dir)