import os
import decimal
import sys

#print "enter"
liste_files = os.listdir("./")

analyze_size = str(sys.argv[1])
threshold = decimal.Decimal(sys.argv[2])
# Dictionnary with key = class, value = [[list of confidence values] [list of subclasses]]
dict_classes = {}
#print liste_files
for file in liste_files:
    #print file
    if "Results_AstroSentences" in file and analyze_size in file and "Timestamps" not in file:
        opened = open(file,'r')
        #print "Analyse"
        for ligne in opened.readlines():
            if "Confidence value:" in ligne:
                conf = ligne.replace("\n","").split("Confidence value:")[1]
            else:
                if "possible subclass:" in ligne:
                    dict_classes[cls][1].append(ligne.replace("\n","").split("possible subclass:")[1])
                else:
                    cls = ligne.replace("\n","")
                    if dict_classes.has_key(cls):
##                        print "new detection of class:" + cls
                        dict_classes[cls][0].append(conf)
                    else:
                        dict_classes[cls] = [[conf],[]]
##    for key in dict_classes:
##        print key
##        print dict_classes[key]
##print "################# General classes #####################"
dict_classes_moyenne = {}
for key in dict_classes:
    liste_confidence = dict_classes[key][0]
    sum_conf = 0
    for conf in dict_classes[key][0]:
        sum_conf += decimal.Decimal(conf)
    moyenne_conf = decimal.Decimal(sum_conf) / len(dict_classes[key][0])
##    print "average confidence:" + str(moyenne_conf)
##    print key
##    print dict_classes[key]
    if moyenne_conf > threshold:
        dict_classes_moyenne[key] = [moyenne_conf,dict_classes[key][1]]
for key in dict_classes_moyenne:
##    print "################################################"
    print "class:" + key
    print "average confidence:" + str(dict_classes_moyenne[key][0])
    for elt in dict_classes_moyenne[key][1]:
        if dict_classes_moyenne.has_key(elt):
            print "subclass:"+elt
    
