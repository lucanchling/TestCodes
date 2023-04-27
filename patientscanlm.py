import glob
import os
from icecream import ic

def search(path,*args):
        """
        Return a dictionary with args element as key and a list of file in path directory finishing by args extension for each key

        Example:
        args = ('json',['.nii.gz','.nrrd'])
        return:
            {
                'json' : ['path/a.json', 'path/b.json','path/c.json'],
                '.nii.gz' : ['path/a.nii.gz', 'path/b.nii.gz']
                '.nrrd.gz' : ['path/c.nrrd']
            }
        """
        arguments=[]
        for arg in args:
            if type(arg) == list:
                arguments.extend(arg)
            else:
                arguments.append(arg)
        return {key: [i for i in sorted(glob.iglob(os.path.normpath("/".join([path,'**','*'])),recursive=True)) if i.endswith(key)] for key in arguments}

def PatientScanLandmark(dic,scan_extension,lm_extension):
    patients = {}

    for extension,files in dic.items():
        for file in files:
            file_name = os.path.basename(file).split(".")[0]
            patient = file_name.split('_scan')[0].split('_Scanreg')[0].split('_lm')[0]
            
            if patient not in patients.keys():
                patients[patient] = {"dir": os.path.dirname(file),
                                     "fid": []}
            if extension in scan_extension:
                patients[patient]["scan"] = file
            if extension in lm_extension:
                patients[patient]["fid"].append(file)

    return patients



scan_folder = '/home/luciacev/Desktop/Luc_Anchling/DATA/ASO_CBCT/TEST_Slicer/Data'
scan_extension = [".nrrd", ".nrrd.gz", ".nii", ".nii.gz", ".gipl", ".gipl.gz"]
json_extension = ['.json','fcsv']
dic = search(scan_folder,json_extension,scan_extension)

patients = PatientScanLandmark(dic,scan_extension,json_extension)
# ic(patients)
for patient,data in patients.items():
    if "scan" not in data.keys():
        print("Missing scan for patient :",patient,"at",data["dir"])
        error = True
    if len(data["fid"]) == 0:
        print("Missing landmark for patient :",patient,"at",data["dir"])
        error = True

