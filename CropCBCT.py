import SimpleITK as sitk
from utils import search
import numpy as np
import os,json
import multiprocessing as mp

def Crop(ScanListe, ROI_Path=None):
    for file in ScanListe:
        patient = os.path.basename(file).split("_Or")[0]

        ScanOutPath = "/home/luciacev/Desktop/Luc_Anchling/DATA/ALI_CBCT/SaraCropped/"+patient+"_Cropped.nii.gz"

        if not os.path.exists(ScanOutPath):

            img = sitk.ReadImage(file)

            if ROI_Path is not None: # When the Crop Volume ROI has been saved in a json file
                ROI = json.load(open(ROI_Path))['markups'][0]
                ROI_Center = np.array(ROI['center'])
                ROI_Size = np.array(ROI['size'])
            
            else: # When you know the size and the center of the ROI
                ROI_Center = [3.8919315338134767, -25.656431198120118, 13.810585021972657]
                ROI_Size = [140, 115, 54]

            ROI_Center = np.array(img.TransformPhysicalPointToContinuousIndex(ROI_Center)).astype(int)

            # Crop the image
            crop_image = img[ROI_Center[0]-ROI_Size[0]*2:ROI_Center[0]+ROI_Size[0]*2,
                            ROI_Center[1]-ROI_Size[1]*2:ROI_Center[1]+ROI_Size[1]*2,
                            ROI_Center[2]-ROI_Size[2]*2:ROI_Center[2]+ROI_Size[2]*2]
            
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