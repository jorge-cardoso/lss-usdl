import urllib2
import re
import regex
import sys
from BeautifulSoup import BeautifulSoup
from rdflib import Graph, Namespace, Literal, URIRef
from rdflib.namespace import RDF, RDFS, SKOS, OWL, FOAF, DC

#page = urllib2.urlopen('http://www.itil.org/en/glossar/glossarkomplett.php')
#page=f.read()

soup = BeautifulSoup(open("ITIL Roles | IT Process Wiki.html"))
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
itil_role = Namespace("http://eden.dei.uc.pt/~jcardoso/rdf/itil/roles.ttl#")
itil_proc = Namespace("http://eden.dei.uc.pt/~jcardoso/rdf/itil/processes.ttl#")
itil_glos = Namespace("http://eden.dei.uc.pt/~jcardoso/rdf/itil/glossary.ttl#")

g.add( (URIRef("http://eden.dei.uc.pt/~jcardoso/rdf/itil/roles.ttl"), RDF.type, OWL.ontology) )
g.add( (itil_role["jcardoso"], RDF.type, FOAF.Person) )
g.add( (itil_role["jcardoso"], FOAF.name, Literal("Jorge Cardoso") ))
g.add( (itil_role["jcardoso"], FOAF.homepage, URIRef("http://eden.dei.uc.pt/~jcardoso/") ))
g.add( (itil_role[""], DC.creator, itil_role["jcardoso"] ))

g.add( (itil_role["ITIL_Roles"], RDF.type, SKOS.concept) )
g.add( (itil_role["ITIL_Roles"], SKOS.prefLabel, Literal("ITIL Roles")))
g.add( (itil_role["ITIL_Roles"], RDFS.label,     Literal("ITIL Roles")))

print ""
print "===== Parsing ITIL Roles \"ITIL Roles | IT Process Wiki.html\" ======"

i = 0
phase = ''
process = ''
subprocess = ''

for ITIL_phase in soup.findAll('span', {"class" : "ITIL_phase"}):
    #print ITIL_phase
    
    #<h3><span class="mw-headline" id="ITIL_roles_-_Service_Strategy">ITIL roles - <a href="/index.php/ITIL_Service_Strategy" title="ITIL Service Strategy">Service Strategy</a></span></h3>
    # get the name of the ITIL phase
    phase_name =  ITIL_phase.find('span', {"class" : "mw-headline"}).a.string
    #print phase_name
    print "-------------------------"
    for headline in ITIL_phase.findAll('span', {"class" : "headline"}):
         #print headline
                
         if headline.has_key('id'):
             role_name = headline['id'] 
             #print role_name
    
         i = i + 1
         role_uri = itil_role[role_name.replace (" ", "_")]
         g.add( (role_uri, RDF.type, SKOS.concept) )
         g.add( (role_uri, SKOS.prefLabel, Literal(role_name.replace ("_", " "))))
         g.add( (role_uri, RDFS.label, Literal(role_name.replace ("_", " "))))
         g.add( (role_uri, SKOS.member, itil_role["ITIL_Roles"] ))
         g.add( (role_uri, SKOS.member, itil_proc[phase_name.replace (" ", "_")] ))

         for li in headline.findAll('li'):
             description = li.text 
             #print description
             g.add( (role_uri, SKOS.definition, Literal(description) ))

         
         #print phase
         print phase_name + " : " + role_name + " : " + description


print ""
print "%s concepts created"%i
print "RDF/turtle ontology stored in roles.ttl"

g.serialize("roles.ttl", format='turtle')





