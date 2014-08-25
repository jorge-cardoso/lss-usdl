import urllib2
import re
import regex
import sys
from BeautifulSoup import BeautifulSoup
from rdflib import Graph, Namespace, Literal, URIRef
from rdflib.namespace import RDF, RDFS, SKOS, OWL, FOAF, DC

#page = urllib2.urlopen('http://www.itil.org/en/glossar/glossarkomplett.php')
#page=f.read()

soup = BeautifulSoup(open("ITIL-Processes.html"))
#<tr>
#<th class="gs01th" valign="top">Account Manager</th>
#    <td class="gs01td" valign="top">(Service Strategy) A Role that is very similar to Business Relationship Manager, but includes more commercial aspects. Most commonly used when dealing with External Customers.</td>
#        </tr>

g = Graph()
g.namespace_manager.bind("itil", "http://eden.dei.uc.pt/~jcardoso/rdf/itil/processes.ttl#")
g.namespace_manager.bind("itilrole", "http://eden.dei.uc.pt/~jcardoso/rdf/itil/roles.ttl#")
g.namespace_manager.bind("itilproc", "http://eden.dei.uc.pt/~jcardoso/rdf/itil/processes.ttl#")
g.namespace_manager.bind("itilglos", "http://eden.dei.uc.pt/~jcardoso/rdf/itil/glossary.ttl#")

g.namespace_manager.bind("foaf", FOAF)
g.namespace_manager.bind("skos", SKOS)
g.namespace_manager.bind("dc", DC)
itil = Namespace("http://eden.dei.uc.pt/~jcardoso/rdf/itil/processes.ttl#")


g.add( (URIRef("http://eden.dei.uc.pt/~jcardoso/rdf/itil/processes.ttl"), RDF.type, OWL.ontology) )
g.add( (itil["jcardoso"], RDF.type, FOAF.Person) )
g.add( (itil["jcardoso"], FOAF.name, Literal("Jorge Cardoso") ))
g.add( (itil["jcardoso"], FOAF.homepage, URIRef("http://eden.dei.uc.pt/~jcardoso/") ))
g.add( (itil[""], DC.creator, itil["jcardoso"] ))

g.add( (itil["ITIL_Processes"], RDF.type, SKOS.concept) )
g.add( (itil["ITIL_Processes"], SKOS.prefLabel, Literal("ITIL Processes")))
g.add( (itil["ITIL_Processes"], RDFS.label,     Literal("ITIL Processes")))

print ""
print "===== Parsing ITIL Processes \"ITIL-Processes.html\" ======"

i = 0
phase = ''
process = ''
subprocess = ''
tbody = soup.findAll("tbody")[1]
for tr in tbody.findAll('tr'):
    
     i = i + 1
     if i == 1:
        continue
     
     trs = tr.findAll('td')
     #print trs
     #print trs[0]
    
     # First column. The phase - not always with a value
     if trs[0]:
         if not trs[0].string:
            phase = trs[0].p.em.string
            phase_uri = itil[phase.replace (" ", "_")]
            g.add( (phase_uri, RDF.type, SKOS.concept) )
            g.add( (phase_uri, SKOS.prefLabel, Literal(phase)))
            g.add( (phase_uri, RDFS.label, Literal(phase)))
            g.add( (phase_uri, SKOS.member, itil["ITIL_Processes"] ))
            #print phase

     # The process - always with a value
     if trs[1]:
        process = trs[1].p.string
        process_uri = itil[process.replace (" ", "_")]
        g.add( (process_uri, RDF.type, SKOS.concept) )
        g.add( (process_uri, SKOS.prefLabel, Literal(process)))
        g.add( (process_uri, RDFS.label, Literal(process)))
        g.add( (process_uri, SKOS.member, phase_uri ))
        #print process

     if trs[2]:
        if not trs[2].string:
           lis = trs[2].find('ul').findAll('li')
           for li in lis:
               subprocess = li.string
               subprocess_uri = itil[subprocess.replace (" ", "_")]
               g.add( (subprocess_uri, RDF.type, SKOS.concept) )
               g.add( (subprocess_uri, SKOS.prefLabel, Literal(process)))
               g.add( (subprocess_uri, RDFS.label, Literal(process)))
               g.add( (subprocess_uri, SKOS.member, process_uri ))
               print phase + ":" + process_uri + ":" + subprocess_uri


print ""
print "%s concepts created"%i
print "RDF/turtle ontology stored in processes.ttl"

g.serialize("processes.ttl", format='turtle')





