import pandas as pd
from utils import LoadOnlyLandmarks
import os


if __name__ == "__main__":
    dir1,dir2 = '/home/luciacev/Desktop/Luc/DATA/SOPHIE/T1/','/home/luciacev/Desktop/Luc/DATA/SOPHIE/T2/'
    dir_excel = '/home/luciacev/Desktop/Luc/DATA/SOPHIE/EXCEL/'

    files = sorted(os.listdir(dir1))

    for basename in files:
        patient = basename.split('_lm')[0].split('_Or')[0]
        # create excel file
        excel_file = os.path.join(dir_excel,patient+'.xlsx')
        df = pd.DataFrame(columns=['Landmark','T1','T2'])
        LM,T1,T2 = [],[],[]
        file1,file2 = os.path.join(dir1,basename),os.path.join(dir2,basename)

        lm1,lm2 = LoadOnlyLandmarks(file1),LoadOnlyLandmarks(file2)

        for landmark in lm2.keys():
            LM.append(landmark)
            T1.append(lm1[landmark])
            T2.append(lm2[landmark])

        df['Landmark'] = LM
        df['T1'] = T1
        df['T2'] = T2
        df.to_excel(excel_file,index=False)