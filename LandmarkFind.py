from utils import GenDictLandmarks

if __name__ == '__main__':
    DATA = GenDictLandmarks("/home/luciacev/Desktop/Luc_Anchling/DATA/ALI_CBCT/DATA_RESAMPLED")
    
    landmarks = ["IF","ANS","PNS","UR6O","UL6O","UR1O"]

    listePatient = []

    for i,(patient,data) in enumerate(DATA.items()):
        count = 0
        for ldmk in landmarks:
            if data[ldmk]:
                count += 1
        if count == 0:
            listePatient.append(patient)

    liste = sorted(listePatient)
    for i in liste:
        print(i)
    print(len(liste))