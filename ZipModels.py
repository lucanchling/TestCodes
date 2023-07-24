import os, shutil, glob
folder_path = '/home/luciacev/Desktop/Luc/Models/ALI_Models/'
out_folder = '/home/luciacev/Desktop/Luc/Models/ALI_Models_Zips/'

if not os.path.exists(out_folder):
    os.makedirs(out_folder)

normpath = os.path.join(folder_path, '**','*')
for path in glob.iglob(normpath):
    shutil.make_archive(os.path.join(out_folder, os.path.basename(path)), 'zip', path)