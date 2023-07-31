import numpy as np
import SimpleITK as sitk
import json, glob, os, time
from tqdm import tqdm

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
    return {key: [i for i in glob.iglob(os.path.normpath("/".join([path,'**','*'])),recursive=True) if i.endswith(key)] for key in arguments}

def LoadOnlyLandmarks(ldmk_path, ldmk_list=None):
    """
    Load landmarks from json file without using the img as input
    
    Parameters
    ----------
    ldmk_path : str
        Path to the json file
    gold : bool, optional
        If True, load gold standard landmarks, by default False
    
    Returns
    -------
    dict
        Dictionary of landmarks
    
    Raises
    ------
    ValueError
        If the json file is not valid
    """
    with open(ldmk_path) as f:
        data = json.load(f)
    
    markups = data["markups"][0]["controlPoints"]
    
    landmarks = {}
    for markup in markups:
        try:
            lm_ph_coord = np.array([markup["position"][0],markup["position"][1],markup["position"][2]])
            #lm_coord = ((lm_ph_coord - origin) / spacing).astype(np.float16)
            lm_coord = lm_ph_coord.astype(np.float64)
            landmarks[markup["label"]] = lm_coord
        except:
            continue
    if ldmk_list is not None:
        return {key:landmarks[key] for key in ldmk_list if key in landmarks.keys()}
    
    return landmarks

def applyTransformLandmarks(landmarks, transform):
    """Apply a transform to a set of landmarks."""
    copy = landmarks.copy()
    for lm, pt in landmarks.items():
        copy[lm] = transform.TransformPoint(pt)
    return copy

def ResampleImage(image, transform):
    '''
    Resample image using SimpleITK
    
    Parameters
    ----------
    image : SimpleITK.Image
        Image to be resampled
    target : SimpleITK.Image
        Target image
    transform : SimpleITK transform
        Transform to be applied to the image.
        
    Returns
    -------
    SimpleITK image
        Resampled image.
    '''
    # Create resampler
    resampler = sitk.ResampleImageFilter()
    resampler.SetReferenceImage(image)
    resampler.SetInterpolator(sitk.sitkLinear)
    resampler.SetDefaultPixelValue(0)
    resampler.SetTransform(transform)

    # Resample image
    resampled_image = resampler.Execute(image)

    return resampled_image

def GenDictLandmarks(data_dir):
    DATA = {}
    GROUP_LABELS = {
    'CB' : ['Ba', 'S', 'N', 'RPo', 'LPo', 'RFZyg', 'LFZyg', 'C2', 'C3', 'C4'],

    'U' : ['RInfOr', 'LInfOr', 'LMZyg', 'RPF', 'LPF', 'PNS', 'ANS', 'A', 'UR3O', 'UR1O', 'UL3O', 'UR6DB', 'UR6MB', 'UL6MB', 'UL6DB', 'IF', 'ROr', 'LOr', 'RMZyg', 'RNC', 'LNC', 'UR7O', 'UR5O', 'UR4O', 'UR2O', 'UL1O', 'UL2O', 'UL4O', 'UL5O', 'UL7O', 'UL7R', 'UL5R', 'UL4R', 'UL2R', 'UL1R', 'UR2R', 'UR4R', 'UR5R', 'UR7R', 'UR6MP', 'UL6MP', 'UL6R', 'UR6R', 'UR6O', 'UL6O', 'UL3R', 'UR3R', 'UR1R'],

    'L' : ['RCo', 'RGo', 'Me', 'Gn', 'Pog', 'PogL', 'B', 'LGo', 'LCo', 'LR1O', 'LL6MB', 'LL6DB', 'LR6MB', 'LR6DB', 'LAF', 'LAE', 'RAF', 'RAE', 'LMCo', 'LLCo', 'RMCo', 'RLCo', 'RMeF', 'LMeF', 'RSig', 'RPRa', 'RARa', 'LSig', 'LARa', 'LPRa', 'LR7R', 'LR5R', 'LR4R', 'LR3R', 'LL3R', 'LL4R', 'LL5R', 'LL7R', 'LL7O', 'LL5O', 'LL4O', 'LL3O', 'LL2O', 'LL1O', 'LR2O', 'LR3O', 'LR4O', 'LR5O', 'LR7O', 'LL6R', 'LR6R', 'LL6O', 'LR6O', 'LR1R', 'LL1R', 'LL2R', 'LR2R'],

    'CI' : ['UR3OIP','UL3OIP','UR3RIP','UL3RIP'],

    'TMJ' : ['AF', 'AE']
}
    ALL_LANDMARKS = [value for key, value in GROUP_LABELS.items()]
    ALL_LANDMARKS = ALL_LANDMARKS[0] + ALL_LANDMARKS[1] + ALL_LANDMARKS[2] + ALL_LANDMARKS[3] #+ ALL_LANDMARKS[4]

    normpath = os.path.normpath("/".join([data_dir, '**', '*']))

    for img in glob.iglob(normpath, recursive=True):
        basename = os.path.basename(img)
        patient = '_'.join(img.split('/')[-3:-1]).split('_dataset')[0] + '_' + basename.split('.')[0].split('_scan')[0].split('_Or')[0].split('_OR')[0].split("_Scan")[0].split("_MERGED")[0].split("_lm")[0] #
        if os.path.isfile(img) and True in [ext in img for ext in [".nrrd", ".nii", ".nii.gz", ".nrrd.gz", ".gipl", 'gipl.gz']]:
            if patient not in DATA:
                DATA[patient] = {}
            if '_HD' in basename:
                DATA[patient]['img_HD'] = img
            else:
                DATA[patient]['img_LD'] = img

            
        if os.path.isfile(img) and True in [ext in img for ext in [".json"]]:
            if 'MERGED' in img:
                if patient not in DATA:
                    DATA[patient] = {}
                DATA[patient]['LM'] = img
                Landmarks = LoadOnlyLandmarks(img).keys()
                is_Landmarks = [True if i in Landmarks else False for i in ALL_LANDMARKS]
                for i,lm in enumerate(ALL_LANDMARKS):
                    DATA[patient][lm] = is_Landmarks[i]

    return DATA

def GetListNamesSegType(segmentationType):
    dic = {'CB':['cb'],
           'MAND':['mand','md'],
           'MAX':['max','mx'],}
    return dic[segmentationType]

def GetListFiles(folder_path, file_extension):
    """Return a list of files in folder_path finishing by file_extension"""
    file_list = []
    for extension_type in file_extension:
        file_list += search(folder_path,file_extension)[extension_type]
    return file_list

def GetPatients(folder_path, time_point='T2', segmentationType=None):
    """Return a dictionary with patient id as key"""
    file_extension = ['.nii.gz','.nii','.nrrd','.nrrd.gz','.gipl','.gipl.gz']
    json_extension = ['.json']
    file_list = GetListFiles(folder_path, file_extension+json_extension)

    patients = {}
    
    for file in file_list:
        basename = os.path.basename(file)
        patient = basename.split('_Scan')[0].split('_scan')[0].split('_Or')[0].split('_OR')[0].split('_MAND')[0].split('_MD')[0].split('_MAX')[0].split('_MX')[0].split('_CB')[0].split('_lm')[0].split('_T2')[0].split('_T1')[0].split('_Cl')[0].split('.')[0].split("_Cropped")[0]
        
        if patient not in patients:
            patients[patient] = {}
        
        if True in [i in basename for i in file_extension]:
            # if segmentationType+'MASK' in basename:
            if True in [i in basename.lower() for i in ['mask','seg','pred']]:
                if segmentationType is None:
                    patients[patient]['seg'+time_point] = file
                else:
                    if True in [i in basename.lower() for i in GetListNamesSegType(segmentationType)]:
                        patients[patient]['seg'+time_point] = file
                
            else:
                patients[patient]['scan'+time_point] = file

        if True in [i in basename for i in json_extension]:
            if time_point == 'T2':
                patients[patient]['lm'+time_point] = file

    return patients

def GetMatrixPatients(folder_path):
    """Return a dictionary with patient id as key and matrix path as data"""
    file_extension = ['.h5','.tfm','.mat']
    file_list = GetListFiles(folder_path, file_extension)

    patients = {}
    for file in file_list:
        basename = os.path.basename(file)
        patient = basename.split("_T1_Left")[0]
        if patient not in patients and True in [i in basename for i in file_extension]:
            patients[patient] = {}
            patients[patient]['mat'] = file  

    return patients

def GetDictPatients(folder_path, matrix_folder=None):
    """Return a dictionary with patients for both time points"""
    patients = GetPatients(folder_path)
    # patients_t2 = GetPatients(folder_t2_path, time_point='T2', segmentationType=segmentationType)
        
    if matrix_folder is not None:
        patient_matrix = GetMatrixPatients(matrix_folder)
        patients = MergeDicts(patients,patient_matrix)
    return patients

def MergeDicts(dict1,dict2):
    """Merge t1 and t2 dictionaries for each patient"""
    patients = {}
    for patient in dict1:
        patients[patient] = dict1[patient]
        try:
            patients[patient].update(dict2[patient])
        except KeyError:
            continue
    return patients

def GenControlePoint(landmarks):
    lm_lst = []
    false = False
    true = True
    id = 0
    for landmark,data in landmarks.items():
        id+=1
        controle_point = {
            "id": str(id),
            "label": landmark,
            "description": "",
            "associatedNodeID": "",
            "position": [data[0], data[1], data[2]],
            "orientation": [1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0],
            "selected": true,
            "locked": true,
            "visibility": true,
            "positionStatus": "defined"
        }
        lm_lst.append(controle_point)

    return lm_lst

def WriteJson(landmarks,out_path):
    false = False
    true = True
    file = {
    "@schema": "https://raw.githubusercontent.com/slicer/slicer/master/Modules/Loadable/Markups/Resources/Schema/markups-schema-v1.0.0.json#",
    "markups": [
        {
            "type": "Fiducial",
            "coordinateSystem": "LPS",
            "locked": false,
            "labelFormat": "%N-%d",
            "controlPoints": GenControlePoint(landmarks),
            "measurements": [],
            "display": {
                "visibility": false,
                "opacity": 1.0,
                "color": [0.4, 1.0, 0.0],
                "color": [0.5, 0.5, 0.5],
                "selectedColor": [0.26666666666666669, 0.6745098039215687, 0.39215686274509806],
                "propertiesLabelVisibility": false,
                "pointLabelsVisibility": true,
                "textScale": 2.0,
                "glyphType": "Sphere3D",
                "glyphScale": 2.0,
                "glyphSize": 5.0,
                "useGlyphScale": true,
                "sliceProjection": false,
                "sliceProjectionUseFiducialColor": true,
                "sliceProjectionOutlinedBehindSlicePlane": false,
                "sliceProjectionColor": [1.0, 1.0, 1.0],
                "sliceProjectionOpacity": 0.6,
                "lineThickness": 0.2,
                "lineColorFadingStart": 1.0,
                "lineColorFadingEnd": 10.0,
                "lineColorFadingSaturation": 1.0,
                "lineColorFadingHueOffset": 0.0,
                "handlesInteractive": false,
                "snapMode": "toVisibleSurface"
            }
        }
    ]
    }
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(file, f, ensure_ascii=False, indent=4)

    f.close

def ReadFCSV(filePath):
    """
    Read fiducial file ".fcsv" and return a liste of landmark dictionnary

    Parameters
    ----------
    filePath
     path of the .fcsv file 
    """
    Landmark_dic = {}
    with open(filePath, mode='r') as csv_file:
        csv_reader = csv.reader(csv_file)
        for row in csv_reader:
            if "#" not in row[0]:
                landmark = {}
                landmark["id"], landmark["x"], landmark["y"], landmark["z"], landmark["label"] = row[0], float(row[1]), float(row[2]), float(row[3]), row[11]
                Landmark_dic[row[11]] = landmark
    return Landmark_dic

def SaveJsonFromFcsv(file_path,out_path,Corresp):
    """
    Save a .fcsv in a .json file

    Parameters
    ----------
    file_path : path of the .fcsv file 
    out_path : path of the .json file 
    """
    groupe_data = ReadFCSV(file_path)
    # print(groupe_data)
    new_groupe_data = ChangeNameBis(groupe_data,file_path,Corresp)
    # print(new_groupe_data)
    lm_lst = GenControlePoint(new_groupe_data)
    WriteJson(lm_lst,out_path)

def ChangeNameBis(data,file_path,Type):
    dict = {
        "Bilateral":{
            'IF': 'IF',
            'ANS' : 'ANS',
            'UR6' : 'UR6MP',
            'UL6' : 'UL6MP',
            'UR1' : 'UR1O',
            'UL1' : 'UL1O', 
            'UR1A' : 'UR1R',
            'UR2' : 'UR2O',
            'UR2A' : 'UR2R',
            'UR3' : 'UR3OI',
            'UR3A' : 'UR3RI',
            'UL1A' : 'UL1R',
            'UL2' : 'UL2O',
            'UL2A' : 'UL2R',
            'UL3' : 'UL3OI',
            'UL3A' : 'UL3RI',
            'UR6_UL6' : 'Mid_UR6MP_UL6MP',
            'UR1_UL1' : 'Mid_UR1O_UL1O',
            },
        "Left":{
            'IF': 'IF',
            'ANS' : 'ANS',
            'UR6' : 'UR6MP',
            'UL6' : 'UL6MP',
            'UR1' : 'UR1O',
            'UL1' : 'UL1O', 
            'U1A' : 'UL1R',
            'U2' : 'UL2O',
            'U2A' : 'UL2R',
            'U3' : 'UL3OI',
            'U3A' : 'UL3RI',
            'UR6_UL6' : 'Mid_UR6MP_UL6MP',
            'UR1_UL1' : 'Mid_UR1O_UL1O',
        },
        "Right":{
            'IF': 'IF',
            'ANS' : 'ANS',
            'UR6' : 'UR6MP',
            'UL6' : 'UL6MP',
            'UR1' : 'UR1O',
            'UL1' : 'UL1O', 
            'U1A' : 'UR1R',
            'U2' : 'UR2O',
            'U2A' : 'UR2R',
            'U3' : 'UR3OI',
            'U3A' : 'UR3RI',
            'UR6_UL6' : 'Mid_UR6MP_UL6MP',
            'UR1_UL1' : 'Mid_UR1O_UL1O',},

    }

    new_data = {}
    for key, value in data.items():
        try:
            new_data[dict[Type][key]] = value
        except:
            continue
            # print("KEY {} doesnt exist in {}".format(key,file_path))
    return new_data

def ChangeName(data,type_reg,file_path):
    dict = {
        "CB":
        {
            "MX-1": "A",
            "MX-2": "ANS",
            "MX-3": "PNS",
            "CB-1": "Ba",
            "CB-2": "S",
            "CB-3": "N",
            "MD-1": "B",
            "MD-2": "Pog",
            "MD-3": "Gn",
            "MD-4": "Me",
            "MD-5": "RGo",
            "MD-6": "LGo",
            "MD-7": "C2",
            "MD-8": "RCo",
            "MD-9": "LCo",
            "MD-10": "Mid_Ba_S",
        },
        "MAND":
        {
            "1": "LR1O",
            "2": "LR1R",
            "3": "LR6MB",
            "4": "LR6R",
            "5": "LL6MB",
            "6": "LL6R",
            "7": "Me",
            "8": "RGo",
            "9": "LGo",
            "10": "C2",
            "11": "RCo",
            "12": "LCo",
            "13": "Mid_Ba_S",
        },
        "MAX":
        {
            "1": "UR1O",
            "2": "UR1R",
            "3": "UR6MB",
            "4": "UR6R",
            "5": "UL6MB",
            "6": "UL6R",
        },
    }

    new_data = {}
    for key, value in data.items():
        KEY = key.split('T1-')[-1].split('T2-')[-1].split('T1')[-1].split('T2')[-1]
        try:
            new_data[dict[type_reg][KEY]] = value
        except:
            print("KEY {} doesnt exist in {}".format(KEY,file_path))
    return new_data


def GenControlePoint(groupe_data):
    lm_lst = []
    false = False
    true = True
    id = 0
    for landmark,data in groupe_data.items():
        id+=1
        controle_point = {
            "id": str(id),
            "label": landmark,
            "description": "",
            "associatedNodeID": "",
            "position": [-data["x"], -data["y"], data["z"]],
            "orientation": [1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0],
            "selected": true,
            "locked": true,
            "visibility": true,
            "positionStatus": "defined"
        }
        lm_lst.append(controle_point)

    return lm_lst


def ChangeName(data,type_reg,file_path):
    dict = {
        "CB":
        {
            "MX-1": "A",
            "MX-2": "ANS",
            "MX-3": "PNS",
            "CB-1": "Ba",
            "CB-2": "S",
            "CB-3": "N",
            "MD-1": "B",
            "MD-2": "Pog",
            "MD-3": "Gn",
            "MD-4": "Me",
            "MD-5": "RGo",
            "MD-6": "LGo",
            "MD-7": "C2",
            "MD-8": "RCo",
            "MD-9": "LCo",
            "MD-10": "Mid_Ba_S",
        },
        "MAND":
        {
            "1": "LR1O",
            "2": "LR1R",
            "3": "LR6MB",
            "4": "LR6R",
            "5": "LL6MB",
            "6": "LL6R",
            "7": "Me",
            "8": "RGo",
            "9": "LGo",
            "10": "C2",
            "11": "RCo",
            "12": "LCo",
            "13": "Mid_Ba_S",
        },
        "MAX":
        {
            "1": "UR1O",
            "2": "UR1R",
            "3": "UR6MB",
            "4": "UR6R",
            "5": "UL6MB",
            "6": "UL6R",
        },
    }

    new_data = {}
    for key, value in data.items():
        KEY = key.split('T1-')[-1].split('T2-')[-1].split('T1')[-1].split('T2')[-1]
        try:
            new_data[dict[type_reg][KEY]] = value
        except:
            print("KEY {} doesnt exist in {}".format(KEY,file_path))
    return new_data

def CheckSharedList(shared_list,maxvalue):
    for i in tqdm(range(maxvalue)):
        while sum(shared_list) < i+1:
            time.sleep(1)
        # print("{} / {} Done".format(sum(shared_list),maxvalue))