import SimpleITK as sitk
import numpy as np
from dcmconvert import search
import os
import multiprocessing as mp

def merge_labels(files,input_dir,out_dir):
    for file in files:
        if file.endswith(".nii.gz"):
            seg = sitk.ReadImage(file)
            array = sitk.GetArrayFromImage(seg)
            array = np.where(array > 0,1,0)
            segtrans = sitk.GetImageFromArray(array)
            segtrans.CopyInformation(seg)
            outname = file.replace(input_dir,out_dir)
            if not os.path.exists(os.path.dirname(outname)):
                os.makedirs(os.path.dirname(outname))
            sitk.WriteImage(sitk.Cast(segtrans,sitk.sitkUInt16),outname)

if __name__ == "__main__":
        
        data_dir = "/home/luciacev/Downloads/Segs/"
        out_dir = "/home/luciacev/Downloads/OUTPUT/"
        
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
    
        files = search(data_dir,".nii.gz")[".nii.gz"]
    
        merge_labels(files,data_dir,out_dir)

        # splits = np.array_split(files,20)
    
        # processes = [mp.Process(target=merge_labels, args=(split,data_dir,out_dir)) for split in splits]
    
        # for p in processes:
        #     p.start()
        # for p in processes:
        #     p.join()
