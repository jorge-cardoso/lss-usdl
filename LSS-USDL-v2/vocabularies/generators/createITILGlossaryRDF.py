import urllib2
import re
import regex
import sys
from BeautifulSoup import BeautifulSoup
from rdflib import Graph, Namespace, Literal, URIRef
from rdflib.namespace import RDF, RDFS, SKOS, OWL, FOAF, DC

#page = urllib2.urlopen('http://www.itil.org/en/glossar/glossarkomplett.php')
#page=f.read()

soup = BeautifulSoup(open("ITIL.org - Glossary Complete.html"))
#<tr>
#<th class="gs01th" valign="top">Account Manager</th>
#    <td class="gs01td" valign="top">(Service Strategy) A Role that is very similar to Business Relationship Manager, but includes more commercial aspects. Most commonly used when dealing with External Customers.</td>
#        </tr>

g = Graph()
g.namespace_manager.bind("itilrole", "http://eden.dei.uc.pt/~jcardoso/rdf/itil/roles.ttl#")
g.namespace_manager.bind("itilproc", "http://eden.dei.uc.pt/~jcardoso/rdf/itil/processes.ttl#")
g.namespace_manager.bind("itilglos", "http://eden.dei.uc.pt/~jcardoso/rdf/itil/glossary.ttl#")

g.namespace_manager.bind("foaf", FOAF)
g.namespace_manager.bind("skos", SKOS)
g.namespace_manager.bind("dc", DC)
itilglos = Namespace("http://eden.dei.uc.pt/~jcardoso/rdf/itil/glossary.ttl#")
itilproc = Namespace("http://eden.dei.uc.pt/~jcardoso/rdf/itil/processes.ttl#")

g.add( (URIRef("http://eden.dei.uc.pt/~jcardoso/rdf/itil/glossary.ttl"), RDF.type, OWL.ontology) )
g.add( ( itilglos["jcardoso"], RDF.type, FOAF.Person) )
g.add( ( itilglos["jcardoso"], FOAF.name, Literal("Jorge Cardoso") ))
g.add( ( itilglos["jcardoso"], FOAF.homepage, URIRef("http://eden.dei.uc.pt/~jcardoso/") ))
g.add( ( itilglos[""], DC.creator,  itilglos["jcardoso"] ))

g.add( ( itilglos["Service_Strategy"], RDF.type, SKOS.concept) )
g.add( ( itilglos["Service_Design"], RDF.type, SKOS.concept) )
g.add( ( itilglos["Service_Transition"], RDF.type, SKOS.concept) )
g.add( ( itilglos["Service_Operation"], RDF.type, SKOS.concept) )
g.add( ( itilglos["Continual_Service_Improvement"], RDF.type, SKOS.concept) )

print ""
print "===== Parsing ITIL Glossary \"ITIL.org - Glossary Complete.html\" ======"

i = 0
for row in soup.findAll('tr'):
     th = row.find("th", {"class" :"gs01th"})
     if(th == None):
        continue
     td = row.find("td", {"class" :"gs01td"})
     if(td == None):
        continue

     i = i + 1
     sys.stdout.write(".")
     sys.stdout.flush()

     term = th.string
     description = td.string
     if(description == None):
        continue
     description = description.replace("\r\n", " ").replace("\r", " ")
     #print term
     #print description
     term_uri =  itilglos[term.replace(" ", "_")]
     #print term_uri

     newdescription = ''

     # If the word "example" exists in a description, break the description into sentences.
     # Get the sentence that contains the word "example".
     # Use the sentence to add an example to the concept using the relationship SKOS.example
     if "example" in description.lower():
        sentences = regex.split("(?V1)(?<=[a-z])(?=[A-Z])|(?<=[.!?]) +(?=[A-Z])", description)
        #print(sentences)
        for sentence in sentences:
            if "example" in sentence.lower() and "(Service" not in sentence:
                g.add( (term_uri, SKOS.example, Literal(sentence)) )
            else:
                newdescription = newdescription + sentence.strip() + ' '
     else:
        newdescription = description.strip()

     # If a description of an ITIL concept contains "(Service Strategy)", then it is a concept which belongs to an ITIL phase.
     # Remove "(Service Strategy)" from the description and use to relationship SKOS.member to assign the concept to a phase.
     if "(Service Strategy)" in newdescription:
         g.add((term_uri,SKOS.member, itilproc["Service_Strategy"]))
         newdescription = newdescription.replace("(Service Strategy)", "")
     if "(Service Design)" in description:
         g.add((term_uri,SKOS.member, itilproc["Service_Design"]))
         newdescription = newdescription.replace("(Service Design)", "")
     if "(Service Transition)" in description:
         g.add((term_uri,SKOS.member, itilproc["Service_Transition"]))
         newdescription = newdescription.replace("(Service Transition)", "")
     if "(Service Operation)" in description:
         g.add((term_uri,SKOS.member, itilproc["Service_Operation"]))
         newdescription = newdescription.replace("(Service Operation)", "")
     if "(Continual Service Improvement)" in description:
         g.add((term_uri,SKOS.member, itilproc["Continual_Service_Improvement"]))
         newdescription = newdescription.replace("(Continual Service Improvement)", "")

     g.add( (term_uri, RDF.type, SKOS.concept) )
     g.add( (term_uri, SKOS.prefLabel, Literal(term)))
     g.add( (term_uri, RDFS.label, Literal(term)))
     g.add( (term_uri, SKOS.definition , Literal(newdescription.strip())) )


print ""
print "%s concepts created"%i

print ""
print "===== Creating relationships of type SKOS.related between concepts ======"
# Fetch all the RDFS concepts previously created
# Remove underscore of concepts and replace with a white space. These concepts are called clear concepts.
# Get all the definitions of concepts.
# Check if a clearconcept belongs to a definition.
# If it does, establish a link between the two using the relationship SKOS.related
i = 0
for concept in g.subjects(RDF.type, SKOS.concept):
     #        print "%s is a concept"%concept
     clearconcept = concept.rsplit("#", 2)[1].replace ("_", " ")
     i = i + 1
     sys.stdout.write(".")
     sys.stdout.flush()
        
     for target in g.subjects(RDF.type, SKOS.concept):
         i = i + 1
         definition = g.value(predicate = SKOS.definition, subject = target)
         if definition:
             #print "---------------------"
             #print clearconcept
             #print definition
             if clearconcept in definition:
                #print "found %s in a %s  concept"%(clearconcept,definition)
                g.add( (target, SKOS.related, concept) )

print ""
print "%s searches performed"%i
print "RDF/turtle ontology stored in glossary.ttl"


# Here we could create Jekyll posts. One for each concept.
# Need to check is the relationship of a concept contain the properties:
# RDF.type, SKOS.concept
# SKOS.prefLabel, Literal(term)
# RDFS.label, Literal(term)))
# SKOS.definition , Literal(newdescription.strip())
# SKOS.related, concept
#
# The two relationships with concepts can be establish using http links.
# Tis is only valuable if the search functionality is working


g.serialize("glossary.ttl", format='turtle')





