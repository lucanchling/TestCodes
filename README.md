# TestCodes
## Different Codes with use

- **ApplyMatrix.py**: To apply matrix to scans and json
- **ConvertFCSV.py**: To convert a list of FCSV markups into JSON format (by also changing the name of the landmarks)
- **CorrectSegmentation.py**: To correct the segmentation of the scans for AMASSS Training (if different labels)
- **CreateVTK.py**: To create VTK files from the segmentation files 
- **CropCBCT.py**: To crop CBCT scans using a box created in Slicer (Center,Size, and Position)
- **DCMConvert.py**: To convert DICOM files to NIFTI files
- **LandmarkFind.py**: To find the lists patients that has specific landmarks
- **LMPosition.py**: To find the position of the landmarks and save them in an excel file
- **ManageJson.py**: To manage the json files (merge, clean, change name, etc.)
- **MergeSegmentation.py**: To merge the segmentation files with different labels within a single file/label
- **RenamingCrosswalk.py**: To rename the files based on a crosswalk file (usually after batchanonynmization)
- **utils.py**: To have some useful functions for the other codes
- **ZipModels.py**: To zip the model files for the different tools