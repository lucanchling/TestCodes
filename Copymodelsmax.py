import shutil
import os
import glob

FROM = '/home/luciacev/Desktop/Maxime_Gillot/Data/ALI_CBCT/MODELS/'
WHERE = '/home/luciacev/Desktop/Luc_Anchling/TRAINING/ALI_CBCT/data/ALI_models/'

normpath = os.path.normpath("/".join([FROM, '**', '']))
for file in sorted(glob.iglob(normpath,recursive=True)):
    if file.endswith('_1.pth'):
        shutil.copy(file,(os.path.join(WHERE,file.split(FROM)[1])))


