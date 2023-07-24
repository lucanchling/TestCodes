import SimpleITK as sitk
import os
import numpy as np
import vtk
from dcmconvert import search
from tqdm import tqdm
import multiprocessing as mp

LABEL_COLORS = {
    1: [216, 101, 79],
    2: [128, 174, 128],
    3: [0, 0, 0],
    4: [230, 220, 70],
    5: [111, 184, 210],
    6: [172, 122, 101],
}

def SavePredToVTK(files_path,input_folder,out_folder,process_ID, temp_folder="/tmp/Slicer-luciacev",smoothing=5):
    # print("Generating VTK for ", file_path)
    for file_path in files_path:
            

        img = sitk.ReadImage(file_path) 
        img_arr = sitk.GetArrayFromImage(img)


        present_labels = []
        for label in range(np.max(img_arr)):
            if label+1 in img_arr:
                present_labels.append(label+1)

        for i in present_labels:
            label = i
            seg = np.where(img_arr == label, 1,0)

            output = sitk.GetImageFromArray(seg)

            output.CopyInformation(img)

            output = sitk.Cast(output, sitk.sitkInt16)

            temp_path = temp_folder +f"/tempVTK_Proc{process_ID}.nrrd"
            # print(temp_path)

            writer = sitk.ImageFileWriter()
            writer.SetFileName(temp_path)
            writer.Execute(output)

            surf = vtk.vtkNrrdReader()
            surf.SetFileName(temp_path)
            surf.Update()
            # print(surf)

            dmc = vtk.vtkDiscreteMarchingCubes()
            dmc.SetInputConnection(surf.GetOutputPort())
            dmc.GenerateValues(100, 1, 100)

            # LAPLACIAN smooth
            SmoothPolyDataFilter = vtk.vtkSmoothPolyDataFilter()
            SmoothPolyDataFilter.SetInputConnection(dmc.GetOutputPort())
            SmoothPolyDataFilter.SetNumberOfIterations(smoothing)
            SmoothPolyDataFilter.SetFeatureAngle(120.0)
            SmoothPolyDataFilter.SetRelaxationFactor(0.6)
            SmoothPolyDataFilter.Update()

            model = SmoothPolyDataFilter.GetOutput()

            color = vtk.vtkUnsignedCharArray() 
            color.SetName("Colors") 
            color.SetNumberOfComponents(3) 
            color.SetNumberOfTuples( model.GetNumberOfCells() )
                
            for i in range(model.GetNumberOfCells()):
                color_tup=LABEL_COLORS[label]
                color.SetTuple(i, color_tup)

            model.GetCellData().SetScalars(color)

            outpath = os.path.join(os.path.dirname(file_path.replace(input_folder,out_folder)),os.path.basename(file_path).split("_Seg")[0] + "_model.vtk")              

            if not os.path.exists(os.path.dirname(outpath)):
                os.makedirs(os.path.dirname(outpath))
            
            polydatawriter = vtk.vtkPolyDataWriter()
            polydatawriter.SetFileName(outpath)
            polydatawriter.SetInputData(model)
            polydatawriter.Write()

if __name__ == "__main__":
    data_dir = "/home/luciacev/Downloads/Merged_Seg_Centered/"
    out_dir = "/home/luciacev/Downloads/VTKs/"

    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    files = search(data_dir,".nii.gz")[".nii.gz"]

    splits = np.array_split(files,8)

    processes = [mp.Process(target=SavePredToVTK, args=(split,data_dir,out_dir,i)) for i,split in enumerate(splits)]

    for p in processes:p.start()
    for p in processes:p.join()


    # for file in tqdm(files):
    #     SavePredToVTK(file,data_dir,out_dir)