import StringDist
import jellyfish
import sys
import decimal
from gensim.models import Word2Vec

class MySentences(object):
    def __init__(self, filename):
        self.filename = filename
 
    def __iter__(self):
        for line in open(self.filename):
            yield line.split()
            
original_sentences = sys.argv[1]
proposed_classes = sys.argv[2]
distance = sys.argv[3]

sentences = open(original_sentences,'r').readlines()
classes = open(proposed_classes,'r').readlines()
dict_classes = {}

def train_W2vecmodel():
    sentences = MySentences(original_sentences)
    return Word2Vec(sentences)
#Number of individuals instanciated
nb_individuals = 0
for sentence in sentences:
    best_case = 0
    for classe in classes:
        if "average confidence" in classe:
            continue
        if "class:" in classe:
            cl = classe.split("class:")[1].replace("\n","")
        else:
            continue
        info = sentence.replace("\n","").split(" ")
##        print str(info) + " vs. " + str(cl)
        if distance == "stringdist":
            caseline = StringDist.compare(info,cl.split(" "))
        if distance == "levensthein":
            dist = jellyfish.levenshtein_distance(unicode(sentence.replace("\n","")),unicode(cl))
            caseline = (decimal.Decimal(max(len(sentence.replace("\n","")),len(cl))) - dist) / decimal.Decimal(max(len(sentence.replace("\n","")),len(cl)))
        ##                print "levensthein distance:" + str(caseline)
        ##                print "Jaro distance:" + str(caseline)
        if distance == "jaro-winkler":
            try:
                caseline = jellyfish.jaro_winkler(unicode(sentence.replace("\n","")),unicode(cl))
            except:
                caseline = 0
        ##                print "jaro-winkler distance:" + str(caseline)
        if distance == "w2vec":
            model = train_W2vecmodel()
            caseline = StringDist.compare_Word2vec(info,cl,model)
        #print caseline
        if caseline == 1:
            break
        if caseline > best_case:
            best_case = caseline
            decided_class = cl
    if best_case >= 0.3:
        nb_individuals += 1
        if dict_classes.has_key(decided_class):
            dict_classes[decided_class].append(sentence.replace("\n",""))
        else:
            dict_classes[decided_class] = [sentence.replace("\n","")]
        print sentence.replace("\n","") + " is under: " + decided_class + " with score " + str(best_case)

print "usefull classes:" + str(len(dict_classes))
print "number of instanciations:" + str(nb_individuals) + " on " + str(len(sentences))
