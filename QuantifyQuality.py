import os
import decimal
import sys

liste_files = os.listdir("./")
threshold = 0
size = str(sys.argv[1])
##size = "1000"
nb_cls = 0
nb_subclasses = 0
sum_qual  = 0
nb_qual = 0
for file in liste_files:
    general = 0
    if file == "Resume" + size + ".txt":
        result_structure = open(file+"_Structure.owl",'w')
        result_structure.write("""<?xml version="1.0"?>
        <Ontology xmlns="http://www.w3.org/2002/07/owl#"
        xml:base="http://www.semanticweb.org/root/ontologies/2017/5/untitled-ontology-72"
        xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
        xmlns:xml="http://www.w3.org/XML/1998/namespace"
        xmlns:xsd="http://www.w3.org/2001/XMLSchema#"
        xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"
        ontologyIRI="http://www.semanticweb.org/root/ontologies/2017/5/untitled-ontology-72">
        <Prefix name="owl" IRI="http://www.w3.org/2002/07/owl#"/>
        <Prefix name="rdf" IRI="http://www.w3.org/1999/02/22-rdf-syntax-ns#"/>
        <Prefix name="xml" IRI="http://www.w3.org/XML/1998/namespace"/>
        <Prefix name="xsd" IRI="http://www.w3.org/2001/XMLSchema#"/>
        <Prefix name="rdfs" IRI="http://www.w3.org/2000/01/rdf-schema#"/>\n\n""")
        print file
        qualityfile = open("Quality"+file,'w')
        lignes = open(file,'r').readlines()
        for ligne in range(len(lignes)):
            if "average confidence:" in lignes[ligne]:
                nb_qual += 1
                confidence = decimal.Decimal(lignes[ligne].split("average confidence:")[1].replace("\n",""))
                sum_qual += confidence
##                if confidence >= threshold:
##                        print confidence
##                        print lignes[ligne]
            if "class:" in lignes[ligne] and "subclass:" not in lignes[ligne]:
                try:
                    cla = lignes[ligne].split("class:")[1].replace("\n","")
                    cls = cla.replace("[","").replace("]","").replace("\"","").replace("%","").replace("#","").replace("\\","").replace("{","").replace("}","").replace("|","").replace("['","").replace("']","").replace("\n","").replace("'","").lstrip(" ").rstrip(" ")
                except:
                    continue
                print "class:|" + cls + "|"
                nb_cls += 1
                if cls != "":
##                    print lignes[ligne]
                    result_structure.write("""<Declaration>\n\t<Class IRI="#%s"/>\n</Declaration>\n""" % (cls.replace(" ","_")))
                    result_structure.write("""<AnnotationAssertion>\n\t<AnnotationProperty abbreviatedIRI="rdfs:label"/>\n\t<IRI>#%s</IRI>\n\t<Literal datatypeIRI="http://www.w3.org/1999/02/22-rdf-syntax-ns#PlainLiteral">%s\n\t</Literal>\n</AnnotationAssertion>\n""" %(cls.replace(" ","_"),cls))
##                        print "----> subclass:" + lignes[ligne+2]
            if "subclass:" in lignes[ligne]:
##                    print lignes[ligne]
                    try:
                        sub = lignes[ligne].split("subclass:")[1].replace("\n","")
                        ss_cls = sub.replace("[","").replace("]","").replace("\"","").replace("%","").replace("#","").replace("\\","").replace("{","").replace("}","").replace("|","").replace("['","").replace("']","").replace("\n","").replace("'","").lstrip(" ").rstrip(" ")
                        if ss_cls == "":
                            continue
                        print "---> subclass:|" + ss_cls  + "|"
                        nb_subclasses += 1
                        result_structure.write("""<Declaration>\n\t<Class IRI="#%s"/>\n</Declaration>\n""" % (ss_cls.replace(" ","_")))
                        result_structure.write("""<SubClassOf>\n\t<Class IRI="#%s"/>\n\t<Class IRI="#%s"/>\n\t</SubClassOf>\n""" % (ss_cls.replace(" ","_"),cls.replace(" ","_")))
                        result_structure.write("""<AnnotationAssertion>\n\t<AnnotationProperty abbreviatedIRI="rdfs:label"/>\n\t<IRI>#%s</IRI>\n\t<Literal datatypeIRI="http://www.w3.org/1999/02/22-rdf-syntax-ns#PlainLiteral">%s\n\t</Literal>\n</AnnotationAssertion>\n""" %(ss_cls.replace(" ","_"),ss_cls))
                    except:
                        pass
        result_structure.write("""</Ontology>\n""")
print str(nb_cls) + " classes"
print str(nb_subclasses) + " sub-classes"
print str(decimal.Decimal(sum_qual)/nb_qual) + " average confidence"