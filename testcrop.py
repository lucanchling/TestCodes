import SimpleITK as sitk
import json
import numpy as np

im = sitk.ReadImage("/home/luciacev/Documents/TESTCrop/Cleft_01_T1.nii.gz")
target = sitk.ReadImage("/home/luciacev/Documents/TESTCrop/Cleft_01_T1_Cropped.nii.gz")
targ_size = target.GetSize()


ROI_Path = "/home/luciacev/Documents/TESTCrop/Crop Volume ROI.mrk.json"
ROI = json.load(open(ROI_Path))['markups'][0]
ROI_Center = np.array(ROI['center'])
ROI_Size = np.array(ROI['size']).astype(int)

Lower = ROI_Center - ROI_Size / 2
Upper = ROI_Center + ROI_Size / 2

Lower = np.array(im.TransformPhysicalPointToContinuousIndex(Lower)).astype(int)
Upper = np.array(im.TransformPhysicalPointToContinuousIndex(Upper)).astype(int)

# Crop the image
crop_image = im[Lower[0]:Upper[0],
                Lower[1]:Upper[1],
                Lower[2]:Upper[2]]

sitk.WriteImage(crop_image,"/home/luciacev/Documents/TESTCrop/Cleft_01_T1_Cropped2.nii.gz")
crop_size = crop_image.GetSize()


print()
