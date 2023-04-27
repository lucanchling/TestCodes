import os
import dicom2nifti
import glob
import SimpleITK as sitk
from utils import search


def convertdicom2nifti(input_folder,output_folder=None):


    patients_folders = os.listdir(input_folder)

    if output_folder is None:
        output_folder = os.path.join(input_folder,'NIFTI')

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)


    for patient in patients_folders:
        print("Converting patient: {}...".format(patient))
        current_directory = os.path.join(input_folder,patient)
        dicom2nifti.convert_directory(current_directory,current_directory)
        nifti_file = search(current_directory,'nii.gz')['nii.gz'][0]
        os.rename(nifti_file,os.path.join(output_folder,patient+".nii.gz"))    

def simpleITKconvertDCM(input_folder,output_folder=None):

    patients_folders = os.listdir(input_folder)

    if output_folder is None:
        output_folder = os.path.join(input_folder,'NIFTI')

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)


    for patient in patients_folders:
        if not os.path.exists(os.path.join(output_folder,patient+".nii.gz")):    
            print("Converting patient: {}...".format(patient))
            current_directory = os.path.join(input_folder,patient)
            
            reader = sitk.ImageSeriesReader()
            dicom_names = reader.GetGDCMSeriesFileNames(current_directory)
            reader.SetFileNames(dicom_names)
            image = reader.Execute()

            sitk.WriteImage(image, os.path.join(output_folder,os.path.basename(current_directory)+'.nii.gz'))

def ConvertDCM2NIFTI(input_folder,output_folder=None):
    patients_folders = os.listdir(input_folder)

    if output_folder is None:
        output_folder = os.path.join(input_folder,'NIFTI')

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        
    for patient in patients_folders:
        if not os.path.exists(os.path.join(output_folder,patient+".nii.gz")):    
            print("Converting patient: {}...".format(patient))
            current_directory = os.path.join(input_folder,patient)
            try:
                reader = sitk.ImageSeriesReader()
                dicom_names = reader.GetGDCMSeriesFileNames(current_directory)
                reader.SetFileNames(dicom_names)
                image = reader.Execute()
                sitk.WriteImage(image, os.path.join(output_folder,os.path.basename(current_directory)+'.nii.gz'))
            except RuntimeError:
                dicom2nifti.convert_directory(current_directory,output_folder)
                nifti_file = search(output_folder,'nii.gz')['nii.gz'][0]
                os.rename(nifti_file,os.path.join(output_folder,patient+".nii.gz"))


folder = '/home/luciacev/Desktop/Luc_Anchling/TESTFILES/TESTDCMCONVERT/'
ConvertDCM2NIFTI(folder)