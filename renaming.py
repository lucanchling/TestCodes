import pandas as pd
import os
from glob import iglob
import shutil

def change_separator(liste):
    new_liste = []
    for i in liste:
        new_liste.append(i.replace("\\","/").split('MARCELA/')[-1].split('Data/')[-1].split('Data_nii/')[-1])
    return new_liste

def generate_dict(xlsx_file):
    table = pd.read_excel(xlsx_file)

    input,output = change_separator(table['input'].dropna().tolist()), change_separator(table['output'].dropna().tolist())

    dict = {output[i].split('.')[0]:input[i].split('/') for i in range(len(input))}

    return dict


def main(input_folder,output_folder):
    dict = generate_dict('DJD_crosswalk.xlsx')

    normpath = os.path.join(input_folder,"**","*")
    for file in iglob(normpath,recursive=True):
        if file.endswith("nii.gz"):
            patient = os.path.basename(file).split('.')[0].split('_MAND')[0]
            new_patient, time_point = dict[patient]
            
            new_path = os.path.join(output_folder,new_patient)
            if not os.path.exists(new_path):
                os.mkdir(new_path)
            
            if 'MAND' not in file:
                shutil.copy(file,os.path.join(new_path,new_patient+'_'+time_point+'.nii.gz'))
            else:
                shutil.copy(file,os.path.join(new_path,new_patient+'_'+time_point+'_MAND-Seg.nii.gz'))

if __name__ == "__main__":
    main('/home/luciacev/Desktop/Luc/DATA/TEST/IN','/home/luciacev/Desktop/Luc/DATA/TEST/OUT')