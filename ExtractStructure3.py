# -*- coding: utf-8 -*-
"""
===================================

===================================

Finds a structure inside sentences.

"""
print(__doc__)

import numpy as np
import StringDist
import decimal
import nltk
import difflib
import time
import sys
import jellyfish
from gensim.models import Word2Vec

from sklearn.cluster import AffinityPropagation
from sklearn.cluster import MeanShift, estimate_bandwidth
from sklearn.cluster import DBSCAN
from sklearn import metrics
from sklearn.datasets.samples_generator import make_blobs
from sklearn.preprocessing import StandardScaler

class MySentences(object):
    def __init__(self, filename):
        self.filename = filename
 
    def __iter__(self):
        for line in open(self.filename):
                yield line.split()
            
class Extraction(object):
    def __init__(self,size,sentences_file,distance,algo):
        self.size = size
        self.sentences_file = sentences_file
        self.distance = distance
        self.algo = algo
        if distance == "w2vec":
            self.train_W2vecmodel()
        self.run_extraction()
        
    def train_W2vecmodel(self):
        sentences = MySentences(self.sentences_file)
        self.model = Word2Vec(sentences)
        
                   
    def define_matrix(self,lignes):
        """
        lines: the lines of the file to analyze
        size: the maximum size of the matrix (square)
        method: method used for computing distances between lines
        """
        Dict_desciption_indexes = {}
        infoindexes = ""
        
        #Matrix is inferior than max size: end of clustering
        X = np.zeros((len(lignes),len(lignes)))
        XW2V = np.zeros((len(lignes),len(lignes)))
        id_hierarch = -1
        for index1 in range(len(lignes)):
            id_hierarch2 = -1
            mat_line = np.array([])
            ligne = lignes[index1]
            DictWord = {}
            nonsense = [" a "," of "," the "," for "," not "," by "," be "," in "]
            id_hierarch += 1
            info = ligne.rstrip("\n").lower()
            for non in nonsense:
                info = info.replace(non," ")
            Dict_desciption_indexes[id_hierarch] = info
            infoindexes += "Elt"+str(id_hierarch)+": "+info+"\n"
            words = info.split(" ")
            #only generates the lower triangle
            for index2 in range (index1 +1):
                caseline  = 0
                ligne2 = lignes[index2]
                id_hierarch2 += 1
                info2 = ligne2.rstrip("\n").lower()
                for non in nonsense:
                    info2 = info2.replace(non," ")
                words2 = info2.split(" ")
                if self.distance == "stringdist":
                    caseline = StringDist.compare(words,words2)
                if self.distance == "levensthein":
                    caseline = 1- float (jellyfish.levenshtein_distance(unicode(info2),unicode(info)))
    ##                print "levensthein distance:" + str(caseline)
                if self.distance == "jaro":
                    caseline = jellyfish.jaro_distance(unicode(info2),unicode(info))
    ##                print "Jaro distance:" + str(caseline)
                if self.distance == "jaro-winkler":
                    caseline = jellyfish.jaro_winkler(unicode(info2),unicode(info))
    ##                print "jaro-winkler distance:" + str(caseline)
                if self.distance == "w2vec":
                    caseline = StringDist.compare_Word2vec(words,words2,self.model)                
                if id_hierarch > (size -1) or id_hierarch2 > (size -1):
                    break
                X[id_hierarch][id_hierarch2] = decimal.Decimal(round(caseline,1))
                X[id_hierarch2][id_hierarch] = decimal.Decimal(round(caseline,1))
        print "matrix size:"
        print X.shape
        np.set_printoptions(threshold='nan')
        print "test symetric: "
        print (X.transpose() == X).all()
        return [X,Dict_desciption_indexes]

    def matches(self,list1,list2):
        while True:
            mbs = difflib.SequenceMatcher(None, list1, list2).get_matching_blocks()
            if len(mbs) == 1: break
            for i, j, n in mbs[::-1]:
                if n > 0: yield list1[i: i + n]
                del list1[i: i + n]
                del list2[j: j + n]
                
    def sort_patterns(self,Dict_patterns,Dict_desciption_indexes):
        """
        Returns a dictionary Dict_pattern_classes with
        Key is the number of the cluster
        value is a list of lists of lists:
        Each toplevel list identifies a given pattern in the cluster inside which:
        list 0 is two elements long: the pattern and the number of occurences of the pattern
        list 1 is the list of identified classes for the pattern
        """
        Dict_pattern_classes = {}
        for key in Dict_patterns:
            Dict_pattern_classes[key] = []
            nb = -1
            for elt in Dict_patterns[key]:
                if elt[0] == "pattern":
                    continue
                if elt[1] > 1:
                    nb += 1
                    p = []
                    for index in elt[2]:
                        p.append(Dict_desciption_indexes[index].split(" "))
                    if Dict_pattern_classes.has_key(key):
                        Dict_pattern_classes[key].append([[elt[0],elt[1]],[]])
                    else:
                        Dict_pattern_classes[key] = [[elt[0],elt[1] ],[]]
                    for index_list in range(len(p) - 1):
                        # Find matchings between pattern instances
                        result_list = list(self.matches(p[index_list],p[index_list+1]))
                        if result_list != []:
                            for l in result_list:
                                Dict_pattern_classes[key][nb][1].append((" ").join(l))
        return Dict_pattern_classes

    def plotting_clusters():
        # #############################################################################
        # Plot result
        import matplotlib.pyplot as plt
        # Black removed and is used for noise instead.
        unique_labels = set(labels)
        colors = [plt.cm.Spectral(each)
                  for each in np.linspace(0, 1, len(unique_labels))]
        for k, col in zip(unique_labels, colors):
            if k == -1:
                # Black used for noise.
                col = [0, 0, 0, 1]
        
            class_member_mask = (labels == k)
        
            xy = X[class_member_mask & core_samples_mask]
            plt.plot(xy[:, 0], xy[:, 1], 'o', markerfacecolor=tuple(col),
                     markeredgecolor='k', markersize=14)
        
            xy = X[class_member_mask & ~core_samples_mask]
            plt.plot(xy[:, 0], xy[:, 1], 'o', markerfacecolor=tuple(col),
                     markeredgecolor='k', markersize=6)
        
        plt.title('Estimated number of clusters: %d' % n_clusters_)
        plt.show()

    def run_clustering(self,X):
        """
        Runs the clustering algorithm on the similarity matrix
        """
        if self.algo == "affinity":
            # #############################################################################
            # Compute Affinity Propagation
            af = AffinityPropagation().fit(X)
            cluster_centers_indices = af.cluster_centers_indices_
            labels = af.labels_
            n_clusters_ = len(cluster_centers_indices)
        if self.algo == "dbscan":
            # #############################################################################
            # Compute DBSCAN
            db = DBSCAN(metric ='precomputed', eps=0.3, min_samples=5).fit(X)
            core_samples_mask = np.zeros_like(db.labels_, dtype=bool)
            core_samples_mask[db.core_sample_indices_] = True
            labels = db.labels_
            # Number of clusters in labels, ignoring noise if present.
            n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)
        if self.algo == "meanshift":
            bandwidth = estimate_bandwidth(X, quantile=0.2, n_samples=500)
            ms = MeanShift(bandwidth=bandwidth, bin_seeding=True)
            ms.fit(X)
            labels = ms.labels_
            # Number of clusters in labels, ignoring noise if present.
            n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)
        return [n_clusters_, labels]

    def extraction (self,lignes):
        """
        Extract classes from clusters
        """
        # Dictionnary of classes for each cluster
        Dict_clusters_classes = {}
        # Dictionary of classes. key is the class, value is the confidence
        Dict_classes = {}
        result = self.define_matrix(lignes)
        X = result[0]
        Dict_desciption_indexes = result[1] 
        clust_result = self.run_clustering(X)
        n_clusters_ = clust_result[0]
        labels = clust_result[1]
        index_cluster = 0
        # Dictionary of patterns for each cluster
        Dict_patterns = {}
        # Dictionnary of descriptions for each cluster
        Dict_descriptions_clusters = {}
        while index_cluster < n_clusters_:
            list_patterns = [["pattern","nb of occurences",["matrix index 0","matrix index n"]]]
            for lab in range(len(labels)):
                if labels[lab] == index_cluster:
                    if Dict_descriptions_clusters.has_key(index_cluster):
                        Dict_descriptions_clusters[index_cluster].append(Dict_desciption_indexes[lab])
                    else:
                        Dict_descriptions_clusters[index_cluster] = []
                        Dict_descriptions_clusters[index_cluster].append(Dict_desciption_indexes[lab])
                    # ##############
                    # Identify pattern from each cluster element
                    try:
                        tokens = nltk.word_tokenize(Dict_desciption_indexes[lab])
                    except:
                        continue
                    tagged = nltk.pos_tag(tokens)
                    known_pattern = 0
                    tags = ""
                    for elt in tagged:
                        tags +=  elt[1] + " "
                    for patt in range (len(list_patterns)):
                        if patt == 0:
                            continue
                        if tags == list_patterns[patt][0]:
                            known_pattern = 1
                            list_patterns[patt][1] = list_patterns[patt][1] + 1
                            list_patterns[patt][2].append(lab)
                    if known_pattern == 0:
                        listlab = []
                        listlab.append(lab)
                        list_patterns.append([tags,1,listlab])
            Dict_patterns[index_cluster] = list_patterns
            index_cluster += 1
        for key in Dict_descriptions_clusters:
            if Dict_clusters_classes.has_key(key) == 0:
                Dict_clusters_classes[key]= []
            for elt in range(len(Dict_descriptions_clusters[key])-1):
                result_list = list(self.matches(Dict_descriptions_clusters[key][elt].split(" "),\
                    Dict_descriptions_clusters[key][elt+1].split(" ")))
                if result_list != []:
                    for l in result_list:
                        Dict_clusters_classes[key].append((" ").join(l))
        Dict_pattern_classes = self.sort_patterns(Dict_patterns,Dict_desciption_indexes)
        pattern_multiplier = 0.7
        cluster_multiplier = 0.3
        for key in Dict_pattern_classes:
            csize = len(Dict_descriptions_clusters[key])
            for list_pattern in range(len(Dict_pattern_classes[key])):
                pat = Dict_pattern_classes[key][list_pattern][0][0]
                occur = Dict_pattern_classes[key][list_pattern][0][1]
                for elt in Dict_pattern_classes[key][list_pattern][1]:
                    if elt != '':
                        if Dict_classes.has_key(elt):
                            Dict_classes[elt] += \
                            decimal.Decimal(pattern_multiplier) * \
                            (decimal.Decimal(occur)/decimal.Decimal(csize))
                        else:
                            Dict_classes[elt] = \
                            decimal.Decimal(pattern_multiplier) * \
                            (decimal.Decimal(occur)/decimal.Decimal(csize))
            for elt in Dict_clusters_classes[key]:
                if elt != '':
                    if Dict_classes.has_key(elt):
                        Dict_classes[elt] += \
                        decimal.Decimal(cluster_multiplier) * (1/decimal.Decimal(csize))
                    else:
                        Dict_classes[elt] = decimal.Decimal(cluster_multiplier) * (1/decimal.Decimal(csize))
        list_values = []
        for key in Dict_classes:
            list_values.append(Dict_classes[key])
        # Eliminate duplicates
        list_values = list(set(list_values))
        # Sort by descending values
        list_values.sort(reverse=True)
        return [list_values,Dict_classes]
   
    def run_extraction(self):
        """
        Runs the extraction of structure from a file
        """
        ##print "Number of arguments:",len(sys.argv),'arguments'
        ##print 'Arguments list:', str(sys.argv)
        size = int(sys.argv[1])
        sentences_file = str(sys.argv[2])
        distance = str(sys.argv[3])
        algo = str(sys.argv[4])
        timefile = open("Timestamps_Results_"+str(self.sentences_file)+"_"+str(self.size)+".txt",'w')
        print ("Time at beginning")
        print time.asctime( time.localtime(time.time()))
        timefile.write("Time at beginning\n")
        timefile.write(str(time.asctime( time.localtime(time.time()))) + "\n")
        time.asctime( time.localtime(time.time()))
        fic_handler = open(self.sentences_file,'r')
        lignes = fic_handler.readlines()
        if len(lignes) > self.size:
            nb_packets = len(lignes) / self.size
            modulo = len(lignes) % self.size
            print str(nb_packets) + " of size " \
                + str(self.size) + " and one packet of " + str(modulo)
            nb_packet = 0
            while nb_packet < nb_packets:
                print "analysing lines: " + str(self.size*nb_packet) + " to " + str(self.size*(nb_packet+1))
                return_values = self.extraction(lignes[self.size*nb_packet:self.size*(nb_packet+1)])
                list_values = return_values[0]
                Dict_classes = return_values[1]
                file = open("Results_"+str(self.sentences_file)+"_"+str(self.size)+"_"+str(nb_packet)+".txt",'w')
                for elt in list_values:
                    print("Confidence value:") + str(elt)
                    file.write("Confidence value:" + str(elt) + "\n")
                    for key in Dict_classes:
                        if Dict_classes[key] == elt:
                            print key
                            file.write(key + "\n")
                            for key2 in Dict_classes:
                                if (key in key2) and (key != key2) and (Dict_classes[key] >= Dict_classes[key2]):
                                    print "possible subclass:" + str(key2)
                                    file.write("possible subclass:" + str(key2)+ "\n")
                nb_packet += 1
            file.close()
            try:
                return_values = self.extraction(lignes[self.size*nb_packet:])
                list_values = return_values[0]
                Dict_classes = return_values[1]
                file = open("Results_"+str(self.sentences_file)+"_"+str(self.size)+"_"+str(nb_packet)+".txt",'w')
                for elt in list_values:
                    print("Confidence value:") + str(elt)
                    file.write("Confidence value:" + str(elt) + "\n")
                    for key in Dict_classes:
                        if Dict_classes[key] == elt:
                            print key
                            file.write(key + "\n")
                            for key2 in Dict_classes:
                                if (key in key2) and (key != key2) and (Dict_classes[key] >= Dict_classes[key2]):
                                    print "possible subclass:" + str(key2)
                                    file.write("possible subclass:" + str(key2)+ "\n")
            except: 
                print "No more lines to analyze"
            file.close()
        else:
            return_values = self.extraction(lignes)
            list_values = return_values[0]
            Dict_classes = return_values[1]
            file = open("Results_"+str(sentences_file)+"_"+str(size)+".txt",'w')
            for elt in list_values:
                print("Confidence value:") + str(elt)
                file.write("Confidence value:" + str(elt) + "\n")
                for key in Dict_classes:
                    if Dict_classes[key] == elt:
                        print key
                        file.write(key + "\n")
                        for key2 in Dict_classes:
                            if (key in key2) and (key != key2) and (Dict_classes[key] >= Dict_classes[key2]):
                                print "possible subclass:" + str(key2)
                                file.write("possible subclass:" + str(key2)+ "\n")
            file.close()
        print ("Time at end")
        print time.asctime( time.localtime(time.time()))
        timefile.write("Time at end\n")
        timefile.write(str(time.asctime( time.localtime(time.time()))) + "\n")
        timefile.close()
size = int(sys.argv[1])
sentences_file = str(sys.argv[2])
distance = str(sys.argv[3])
algo = str(sys.argv[4])
Extraction(size,sentences_file,distance,algo)