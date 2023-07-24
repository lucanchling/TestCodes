import SimpleITK as sitk
from utils import LoadOnlyLandmarks, search, ResampleImage, applyTransformLandmarks, GetDictPatients, WriteJson


if __name__ == "__main__":
    path = "/home/luciacev/Desktop/Luc_Anchling/DATA/ALI_CBCT/SaraCropped"

    patients = GetDictPatients(path,path)

    for patient,data in patients.items():
        img = sitk.ReadImage(data["scanT2"])
        ldmk = LoadOnlyLandmarks(data["lmT2"])
        transform = sitk.ReadTransform(data["mat"])

        ldmk = applyTransformLandmarks(ldmk,transform.GetInverse())

        resampled = ResampleImage(img,transform)

        sitk.WriteImage(resampled,"/home/luciacev/Desktop/Luc_Anchling/DATA/ALI_CBCT/Resampled/"+patient+".nii.gz")
        # WriteJson(ldmk,"/home/luciacev/Desktop/Luc_Anchling/DATA/ALI_CBCT/Resampled/"+patient+".json")