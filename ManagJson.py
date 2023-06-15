import json 
import os
import glob
import argparse
import shutil 

from utils import LoadOnlyLandmarks

def GetJsonFiles(data_dir):

    normpath = os.path.normpath("/".join([data_dir, '**', '']))
    json_file = [i for i in sorted(glob.iglob(normpath, recursive=True)) if i.endswith('.json')]

    return json_file


def MergeJson(data_dir,second_dir=None,extension='MERGED'):
    """
    Create one MERGED json file per scans from all the different json files (Upper, Lower...)
    """

    normpath = os.path.normpath("/".join([data_dir, '**', '']))
    json_file = [i for i in sorted(glob.iglob(normpath, recursive=True)) if i.endswith('.json')]

    # ==================== ALL JSON classified by patient  ====================
    dict_list = {}
    for file in json_file:
        patient = '_'.join(file.split('/')[-3:-1])+'#'+file.split('/')[-1].split('.')[0].split('_lm')[0].split('_Scan')[0].split('_Or')[0].split('_Midpoint')[0]#.split('_T1')[0].split('_T2')[0]
        if patient not in dict_list:
            dict_list[patient] = []
        dict_list[patient].append(file)

    if second_dir is not None:
            
        normpath = os.path.normpath("/".join([second_dir, '**', '']))
        json_file_bis = [i for i in sorted(glob.iglob(normpath, recursive=True)) if i.endswith('.json')]

        for file in json_file_bis:
            patient = os.path.basename(file).split('_Midpoint')[0]
            for key in dict_list.keys():
                if patient in key.split('#')[1]:
                    dict_list[key].append(file)
                    
    # ==================== MERGE JSON  ====================``
    for key, files in dict_list.items():
        file1 = files[0]
        with open(file1, 'r') as f:
            data1 = json.load(f)
            data1["@schema"] = "https://raw.githubusercontent.com/slicer/slicer/master/Modules/Loadable/Markups/Resources/Schema/markups-schema-v1.0.0.json#"
        for i in range(1,len(files)):
            with open(files[i], 'r') as f:
                data = json.load(f)
            data1['markups'][0]['controlPoints'].extend(data['markups'][0]['controlPoints'])
        outpath = os.path.normpath("/".join(files[0].split('/')[:-1]))        # Write the merged json file
        with open(outpath+'/'+key.split('#')[1] + '_lm_'+ extension +'.mrk.json', 'w') as f: 
            json.dump(data1, f, indent=4)

    # ==================== DELETE UNUSED JSON  ====================
    for key, files in dict_list.items():
        for file in files:
            if extension not in os.path.basename(file):
                os.remove(file)

def MergeJsonBis(data_dir,second_dir,output_dir, extension='MERGED'):
    """
    Create one MERGED json file per scans from all the different json files (Upper, Lower...)
    """

    normpath = os.path.normpath("/".join([data_dir, '**', '']))
    json_file = [i for i in sorted(glob.iglob(normpath, recursive=True)) if i.endswith('.json')]

    # ==================== ALL JSON classified by patient  ====================
    dict_list = {}
    for file in json_file:
        patient = '_'.join(file.split('/')[-3:-1])+'#'+file.split('/')[-1].split('.')[0].split('_lm')[0].split('_Scan')[0].split('_Or')[0].split('_Midpoint')[0]#.split('_T1')[0].split('_T2')[0]
        if patient not in dict_list:
            dict_list[patient] = {'dir1':[],'dir2':[]}
        dict_list[patient]['dir1'].append(file)

    normpath = os.path.normpath("/".join([second_dir, '**', '']))
    json_file_bis = [i for i in sorted(glob.iglob(normpath, recursive=True)) if i.endswith('.json')]
    for file in json_file_bis:
        patient = os.path.basename(file).split('_lm')[0].split('_Midpoint')[0]
        for key in dict_list.keys():
            if patient == key.split('#')[1]:
                dict_list[key]['dir2'].append(file)
                    
    # ==================== MERGE JSON  ====================``
    for key, data in dict_list.items():
        file1 = data['dir1'][0]
        lm_list = LoadOnlyLandmarks(file1).keys()
        with open(file1, 'r') as f:
            data1 = json.load(f)
            data1["@schema"] = "https://raw.githubusercontent.com/slicer/slicer/master/Modules/Loadable/Markups/Resources/Schema/markups-schema-v1.0.0.json#"
        for file in data['dir2']:
            lm_list_bis = LoadOnlyLandmarks(file).keys()
            with open(file, 'r') as f:
                data = json.load(f)
                # remove landmark already present
                for i,point in enumerate(data['markups'][0]['controlPoints']):
                    if point['label'] not in lm_list:
                        data1['markups'][0]['controlPoints'].append(point)
            # data1['markups'][0]['controlPoints'].extend(data['markups'][0]['controlPoints'])
        outpath = os.path.normpath("/".join(file1.split('/')[:-1]))        # Write the merged json file
        with open(output_dir+'/'+key.split('#')[1] + '_lm_'+ extension +'.mrk.json', 'w') as f: 
            json.dump(data1, f, indent=4)

    # ==================== DELETE UNUSED JSON  ====================
    # for key, files in dict_list.items():
    #     for file in files:
    #         if extension not in os.path.basename(file):
    #             os.remove(file)   

def GetDic(data_dir):
    json_file = GetJsonFiles(data_dir)

    dict_list = {} 
    for file in json_file:
        patient = '_'.join(file.split('/')[-3:-1])
        if patient not in dict_list:
            dict_list[patient] = []
        dict_list[patient].append(file)
    return dict_list

def MoveJsonToFolder(args):

    data_dir = args.data_dir

    dict_list = GetDic(data_dir)

    for key in dict_list.keys():
        for lm_file in dict_list[key]:
            shutil.copy(lm_file,os.path.join(args.out_dir,key,'_'.join([key,'lm',os.path.basename(lm_file).split('_lm_')[1]])))

def CleanJson(json_path):
    '''
    Remove labels that dont have any position attribute'''
    with open(json_path) as f:
        data = json.load(f)
    
    markups = data["markups"][0]["controlPoints"]

    new_markups = [markup for markup in markups if isinstance(markup['position'],list)]

    data["markups"][0]["controlPoints"] = new_markups

    with open(json_path,'w') as f:
        json.dump(data,f,indent=4)

def RenameLandmarksJson(data_dir,dict_rename):
    normpath = os.path.normpath("/".join([data_dir, '**', '']))
    json_file = [i for i in sorted(glob.iglob(normpath, recursive=True)) if i.endswith('.json')]

    # ==================== ALL JSON classified by patient  ====================
    dict_list = {}
    for file in json_file:
        patient = '_'.join(file.split('/')[-3:-1])+'#'+file.split('/')[-1].split('.')[0].split('_lm')[0].split('_Scan')[0].split('_Or')[0].split('_Midpoint')[0]#.split('_T1')[0].split('_T2')[0]
        if patient not in dict_list:
            dict_list[patient] = []
        dict_list[patient] = file

    # ==================== REPLACE LABELS  ====================
    for key, file in dict_list.items():
        with open(file, 'r') as f:
            data = json.load(f)
            for i,point in enumerate(data['markups'][0]['controlPoints']):
                if point['label'] in dict_rename.keys():
                    data['markups'][0]['controlPoints'][i]['label'] = dict_rename[point['label']]
        with open(file, 'w') as f:
            json.dump(data, f, indent=4)


def main(args):

    # data_dir = '/home/luciacev/Downloads/Separated/'
    # dir_mid = '/home/luciacev/Downloads/Sara_midpoints/'
    # json_files = GetJsonFiles(data_dir)

    # for file in json_files:
    #     CleanJson(file)

    # MergeJson(data_dir,dir_mid,args.extension)
    pass

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_dir',help='directory where json files to merge are',type=str,default='/home/luciacev/Desktop/Luc/DATA/AReg_CBCT/JJ/Landmarks/')#required=True)
    parser.add_argument('--second_dir',help='directory where json files to merge are',type=str,default='/home/luciacev/Desktop/Luc/DATA/AReg_CBCT/JJ/BATES_REGISTERED/Landmarks/FOR_NEW_MERGED_T2/MAND/CB')#required=True)
    parser.add_argument('--out_dir',help='output',type=str,default='/home/luciacev/Desktop/Luc/DATA/AReg_CBCT/JJ/BATES_REGISTERED/Landmarks/NEW_MERGED_T2/MAND')#required=True)
    parser.add_argument('--extension',help='extension of new merged json files',type=str,default='MERGED')
    args = parser.parse_args()

    # main(args)
    # MergeJson(args.data_dir,args.extension)
    # MergeJsonBis(args.data_dir,args.second_dir,args.out_dir,args.extension)
    dict_rename = {"C2": "Mid_RGo_LGo",
                   "Mid_Ba_S": "Mid_RCo_LCo"}
    RenameLandmarksJson(args.data_dir,dict_rename)