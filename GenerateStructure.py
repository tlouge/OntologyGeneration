import sys

result = open(str(sys.argv[1]),'r').readlines()
name = str(sys.argv[2])
individuals = open("population.txt",'r').readlines()
result_structure = open(name+"_Structure.owl",'w')

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
for ligne in result:
    if "class" in ligne and "subclass" not in ligne:
        cls = ligne.split("class:")[1].replace("\n","").replace("\"","")\
            .replace("[","").replace("]","")\
            .replace("'","").replace("'","").replace("\\xe2\\x80\\x99","")\
            .replace("\\","").replace("%","").replace(":","").replace("{","")\
            .replace("}","").replace("^","").replace(".","").replace("/","")\
            .replace("\"","").replace("*","").replace("(","").replace(")","")\
            .replace("+","").replace("\/","").replace("#","").replace("`","")\
            .replace("|","").replace("\n","")
        result_structure.write("""<Declaration>\n\t<Class IRI="#%s"/>"""\
        %(cls.replace(" ","_"))+"""\n</Declaration>\n""")
        result_structure.write("""<AnnotationAssertion>\n\t"""\
        +"""<AnnotationProperty abbreviatedIRI="rdfs:comment"/>\n\t"""\
        +"""<IRI>#%s</IRI>\n\t"""%(cls.replace(" ","_"))\
        +"""<Literal datatypeIRI="http://www.w3.org/1999/02/22-rdf-syntax-ns"""\
        +"""#PlainLiteral">%s</Literal>\n</AnnotationAssertion>\n""" \
        %(cls))

    
    if "subclass" in ligne:
        ss_cls = ligne.split("subclass:")[1].replace("\n","").replace("\"","")\
            .replace("[","").replace("]","")\
            .replace("'","").replace("'","").replace("\\xe2\\x80\\x99","")\
            .replace("\\","").replace("%","").replace(":","").replace("{","")\
            .replace("}","").replace("^","").replace(".","").replace("/","")\
            .replace("\"","").replace("*","").replace("(","").replace(")","")\
            .replace("+","").replace("\/","").replace("#","").replace("`","")\
            .replace("|","").replace("\n","")
        result_structure.write("""<SubClassOf>\n\t<Class IRI="#%s"/>"""\
        % (ss_cls.replace(" ","_"))\
        +"""\n\t<Class IRI="#%s"/>"""% (cls.replace(" ","_"))\
        +"""\n</SubClassOf>\n""")
        result_structure.write("""<AnnotationAssertion>\n\t"""\
        +"""<AnnotationProperty abbreviatedIRI="rdfs:comment"/>\n\t"""\
        +"""<IRI>#%s</IRI>\n\t"""%(ss_cls.replace(" ","_"))\
        +"""<Literal datatypeIRI="http://www.w3.org/1999/02/22-rdf-syntax-ns#"""\
        +"""PlainLiteral">%s</Literal>\n</AnnotationAssertion>\n""" \
        %(ss_cls))
for ligne in individuals:
    ind = ligne.split("is under:")[0].lstrip(" ").rstrip(" ").replace("[","")\
            .replace("]","")\
            .replace("'","").replace("'","").replace("\\xe2\\x80\\x99","")\
            .replace("\\","").replace("%","").replace(":","").replace("{","")\
            .replace("}","").replace("^","").replace(".","").replace("/","")\
            .replace("\"","").replace("*","").replace("(","").replace(")","")\
            .replace("+","").replace("\/","").replace("#","").replace("`","")\
            .replace("|","").replace("\n","")
    try:
        cls = ligne.split("is under:")[1].split("with score")[0].lstrip(" ")\
        .rstrip(" ").replace("[","").replace("]","")\
            .replace("'","").replace("'","").replace("\\xe2\\x80\\x99","")\
            .replace("\\","").replace("%","").replace(":","").replace("{","")\
            .replace("}","").replace("^","").replace(".","").replace("/","")\
            .replace("\"","").replace("*","").replace("(","").replace(")","")\
            .replace("+","").replace("\/","").replace("#","").replace("`","")\
            .replace("|","").replace("\n","")
    except:
        print ligne
        continue
    result_structure.write("""<Declaration>\n\t"""\
        +"""<NamedIndividual IRI="#%s"/>\n</Declaration>"""\
        %(ind.replace(" ","_"))\
        +"""\n<ClassAssertion>\n\t<Class IRI="#%s"/>\n\t"""\
        %(cls.replace(" ","_"))\
        +"""<NamedIndividual IRI="#%s"/>\n</ClassAssertion>\n""" \
        %(ind.replace(" ","_")))
    result_structure.write("""<AnnotationAssertion>\n\t"""\
        +"""<AnnotationProperty abbreviatedIRI="rdfs:comment"/>\n\t"""\
        +"""<IRI>#%s</IRI>\n\t"""%(ind.replace(" ","_"))\
        +"""<Literal datatypeIRI="http://www.w3.org/1999/02/22-rdf-syntax-ns#"""\
        +"""PlainLiteral">%s</Literal>\n</AnnotationAssertion>\n""" \
        %(ind))

result_structure.write("""</Ontology>\n""")