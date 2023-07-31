import SimpleITK as sitk
from utils import LoadOnlyLandmarks, search, ResampleImage, applyTransformLandmarks, GetDictPatients, WriteJson, CheckSharedList
import os
from tqdm import tqdm
import multiprocessing as mp
import numpy as np

def ApplyMatrix(patients,keys,input_path, out_path, side="Left", num_worker=0, shared_list=None):

    for key in keys:
        try:
                
            img = sitk.ReadImage(patients[key]["scan"])
            # ldmk = LoadOnlyLandmarks(data["lmT2"])
            transform = sitk.ReadTransform(patients[key]["mat"])

            # ldmk = applyTransformLandmarks(ldmk,transform.GetInverse())

            resampled = ResampleImage(img,transform)
            outpath = patients[key]['scan'].replace(input_path,out_path)
            if not os.path.exists(os.path.dirname(outpath)):
                os.makedirs(os.path.dirname(outpath))

            sitk.WriteImage(resampled,outpath.split('.nii.gz')[0]+f'Scan_{side}_Or.nii.gz')
            # WriteJson(ldmk,"/home/luciacev/Desktop/Luc_Anchling/DATA/ALI_CBCT/Resampled/"+patient+".json")
            shared_list[num_worker] += 1
        except KeyError:
            print(f"Patient {key} not have either scan or matrix")
            shared_list[num_worker] += 1
            continue


def GetPatients(file_path,matrix_path, side="Left"):
    patients = {}

    files = search(file_path,".nii.gz")['.nii.gz']
    files = [f for f in files if 'T1' in f]
    
    matrixes = search(matrix_path,".tfm")['.tfm']
    matrixes = [f for f in matrixes if side in f]

    for i in range(len(files)):
        file = files[i]

        file_pat = os.path.basename(file).split("_T1")[0].replace('.','')

        if file_pat not in patients.keys():
            patients[file_pat] = {}
        patients[file_pat]['scan'] = file
        
    for i in range(len(matrixes)):
        matrix = matrixes[i]
        matrix_pat = os.path.basename(matrix).split("_T1")[0].split("_"+side)[0].replace('.','')
        if matrix_pat not in patients.keys():
            patients[matrix_pat] = {}

        patients[matrix_pat]['mat'] = matrix

    return patients


if __name__ == "__main__":
    file_path = "/home/luciacev/Desktop/Luc/DATA/MARCELA/Scan_Centered/"
    matrix_path = "/home/luciacev/Desktop/Luc/DATA/MARCELA/Oriented/"
    outpath = "/home/luciacev/Desktop/Luc/DATA/MARCELA/Scan_Oriented/"
    side = "Right"
    nb_worker = 18

    patients = GetPatients(file_path,matrix_path,side=side)

    nb_scan_done = mp.Manager().list([0 for i in range(nb_worker)])
    check = mp.Process(target=CheckSharedList,args=(nb_scan_done,len(patients))) 
    check.start()

    splits = np.array_split(list(patients.keys()),nb_worker)

    processess = [mp.Process(target=ApplyMatrix,args=(patients,keys,file_path,outpath,side,i,nb_scan_done)) for i,keys in enumerate(splits)]

    for proc in processess: proc.start()
    for proc in processess: proc.join()
    check.join()
