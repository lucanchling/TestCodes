import pandas as pd
import os
from glob import iglob

def change_separator(liste):
    new_liste = []
    for i in liste:
        new_liste.append(i.replace("\\","/").split('MARCELA/')[-1].split('Data/')[-1].split('Data_nii/')[-1])
    return new_liste

def generate_dict(xlsx_file):
    table = pd.read_excel(xlsx_file)

    input,output = change_separator(table['input'].dropna().tolist()), change_separator(table['output'].dropna().tolist())

    dict = {output[i]:input[i].split('/') for i in range(len(input))}

    return dict

if __name__ == "__main__":

    dict = generate_dict('DJD_crosswalk.xlsx')

    normpath = 