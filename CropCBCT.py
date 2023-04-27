import SimpleITK as sitk
from utils import search
import numpy as np
import json
from tqdm import tqdm
import os
import multiprocessing as mp

def Crop(ScanListe):
    for file in ScanListe:
        patient = os.path.basename(file).split("_Or")[0]

        ScanOutPath = "/home/luciacev/Desktop/Luc_Anchling/DATA/ALI_CBCT/SaraCropped/"+patient+"_Cropped.nii.gz"

        if not os.path.exists(ScanOutPath):

            img = sitk.ReadImage(file)

            crop_target = sitk.ReadImage("/home/luciacev/Desktop/Luc_Anchling/TestCodes/Test/Cropped_Target.nii.gz")
            ROI_Size = np.array(crop_target.GetSize()).astype(int)

            ROI_Center = [3.8919315338134767, -25.656431198120118, 13.810585021972657]
            # ROI_Size = [140, 115, 54]

            ROI_Center = np.array(img.TransformPhysicalPointToContinuousIndex(ROI_Center)).astype(int)
            # ROI_Size = np.array(img.TransformContinuousIndexToPhysicalPoint(ROI_Size)).astype(int)

            # Crop the image using the target

            crop_image = img[ROI_Center[0]-ROI_Size[0]//2:ROI_Center[0]+ROI_Size[0]//2,
                            ROI_Center[1]-ROI_Size[1]//2:ROI_Center[1]+ROI_Size[1]//2,
                            ROI_Center[2]-ROI_Size[2]//2:ROI_Center[2]+ROI_Size[2]//2]
            try:
                sitk.WriteImage(crop_image,ScanOutPath)
            except:
                print("Error for patient: ",patient)

if __name__ == '__main__':
    ScanListe = search("/home/luciacev/Desktop/Luc_Anchling/DATA/ASO_CBCT/NotOriented/SaraOr",".nii.gz")[".nii.gz"]
    ScanListe.sort()

    splits = np.array_split(ScanListe, 15)

    processes = [mp.Process(target=Crop, args=(splits[i],)) for i in range(15)]

    for p in processes: p.start()
    for p in processes: p.join()

    print("Done")