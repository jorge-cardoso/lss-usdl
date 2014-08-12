from rdflib import Graph, RDF, URIRef,  RDFS #, Literal, BNode
from SPARQLWrapper import SPARQLWrapper, JSON

        
class ServiceSystem:
    'A API to a Service Systems'
    filename = ''
    g = Graph()

    def __init__(self, filename):
        ServiceSystem.filename = filename
        ServiceSystem.g.parse("file:ITIL_IM_service.ttl", format='n3')
      
    #------------------------------------------------------------------
    #---------- Show information about the Service System ------------- 
    #------------------------------------------------------------------
    def getServiceInformation(self):
       
       URIServiceSystem = URIRef("http://w3id.org/lss-usdl/v1#ServiceSystem")
       if ( None, RDF.type, URIServiceSystem ) in ServiceSystem.g:
           lss = ServiceSystem.g.value(predicate = RDF.type, object = URIServiceSystem, any = False)
           #print "Service System found! " + lss
       else:
           raise Exception("Cannot find Service System!!")

       if ( None, RDF.type, URIServiceSystem ) in ServiceSystem.g:
           lss_description = ServiceSystem.g.value(predicate = RDFS.comment, subject = lss, any = False)
           #print "Service System description found! " + lss_description
       else:
           raise Exception("Cannot find Service System description!!")

# Can also be done this way   
#       for lss in ServiceSystem.g.subjects(RDF.type, URIRef("http://w3id.org/lss-usdl/v1#ServiceSystem")):    
#           print "Service System Name: ", lss.rsplit("#", 2)[1]          
#       for lss_description in ServiceSystem.g.objects(lss, RDFS.comment):
#           print "Description:", lss_description    

       information=[]
       information.append(lss)
       information.append(lss_description)

       return information


    #------------------------------------------------------------------
    #-------------- Get Interactions   -------------------------------- 
    #------------------------------------------------------------------
    def getInteractions(self):
        qres = ServiceSystem.g.query(
            """PREFIX  lss-usdl:  <http://w3id.org/lss-usdl/v1#>
                SELECT DISTINCT ?a ?b
                WHERE {
                  ?a lss-usdl:hasInteraction ?b .
                }""")

        results = []
        for row in qres:
            s, r = row
            sl = s.rsplit("#", 2)[1]
            rl = r.rsplit("#", 2)[1]
            results.append(rl)
            #print sl, "hasInteraction", rl
    
        return results

# Can also be done this way            
#       print("")
#       print "--- Interaction Points: ---" 
#       for sub, obj in ServiceSystem.g.subject_objects(URIRef("http://w3id.org/lss-usdl/v1#hasInteraction")):
#          interaction = obj.rsplit("#", 2)[1]
#          print interaction            


    #------------------------------------------------------------------
    #-------------- Connectors ---------------------------------------- 
    #------------------------------------------------------------------
    def getConnectors(self):
        qres = ServiceSystem.g.query(
            """PREFIX  lss-usdl:  <http://w3id.org/lss-usdl/v1#>
                SELECT DISTINCT ?src ?tgt ?cond
                WHERE {
                  ?ss lss-usdl:hasControlFlow ?cf.
                  ?cf lss-usdl:hasSource ?src  .
                  ?cf lss-usdl:hasTarget ?tgt .
                  ?cf lss-usdl:hasCondition ?cond .
                }""")

        results = []
        for row in qres:
            src, tgt, cond = row
            source = src.rsplit("#", 2)[1]
            target = tgt.rsplit("#", 2)[1]
            condition = cond
            results.append([source, target, condition])
            #str = 'ControlFlow (' + source + ' -> ' + target + ') with condition "' + condition + '"'''
            #print str
            
        return results

    
    #------------------------------------------------------------------
    #-------------- Get Service Roles --------------------------------- 
    #------------------------------------------------------------------
    def getRoles(self):
        qres = ServiceSystem.g.query(
            """PREFIX  lss-usdl:  <http://w3id.org/lss-usdl/v1#>
                SELECT DISTINCT ?role
                WHERE {
                  ?s ?prop ?o .
                  ?lss lss-usdl:hasInteraction ?int .
                  ?int lss-usdl:performedBy ?role .
                }""")

        results = []
        for row in qres:
            r=getattr(row, "role")
            role = r.rsplit("#", 2)[1]
            results.append(role)

        return results

        

#------------------------------------------------------------------
#-------------- Interactions done by Role ------------------------- 
#------------------------------------------------------------------
    def getInterationsByRole(self):
        qres = ServiceSystem.g.query(
            """PREFIX  lss-usdl:  <http://w3id.org/lss-usdl/v1#>
                SELECT DISTINCT ?lss ?int ?role
                WHERE {
                  ?lss lss-usdl:hasInteraction ?int .
                  ?int lss-usdl:performedBy ?role .
                }""")

        results = []
        for row in qres:
            s, i, r = row
            service = s.rsplit("#", 2)[1]
            interaction = i.rsplit("#", 2)[1]
            role = r.rsplit("#", 2)[1]
            results.append([interaction, role])
           
        return results


#------------------------------------------------------------------
#-------------- Interactions that receive and returns Resources --- 
#------------------------------------------------------------------
    def getInteractionResources(self):
        qres = ServiceSystem.g.query(
        """PREFIX  lss-usdl:  <http://w3id.org/lss-usdl/v1#>
            SELECT DISTINCT ?lss ?int ?resource
            WHERE {
              ?lss lss-usdl:hasInteraction ?int .
              ?int lss-usdl:receivesResource ?resource .
              ?int lss-usdl:returnsResource ?resource .
            }""")

        results = []
        for row in qres:
            s, i, r = row
            service = s.rsplit("#", 2)[1]
            interaction = i.rsplit("#", 2)[1]
            resource = r.rsplit("#", 2)[1]
            results.append([interaction, resource])
           
        return results

#------------------------------------------------------------------
#-------------- Interactions that only receive Resources: --------- 
#------------------------------------------------------------------
    def getInteractionResourcesReceived(self):
        qres = ServiceSystem.g.query(
            """PREFIX  lss-usdl:  <http://w3id.org/lss-usdl/v1#>
                SELECT DISTINCT ?lss ?int ?role
                WHERE {
                  ?lss lss-usdl:hasInteraction ?int .
                  ?int lss-usdl:receivesResource ?role .
                }""")

        results = []
        for row in qres:
            s, i, r = row
            service = s.rsplit("#", 2)[1]
            interaction = i.rsplit("#", 2)[1]
            resource = r.rsplit("#", 2)[1]
            results.append([interaction, resource])
           
        return results


#------------------------------------------------------------------
#-------------- Print first interaction: -------------------------- 
#------------------------------------------------------------------
# Look for an interaction which is a source but not the target of any connector
#
    def getFirstInteraction(self):
        qres = ServiceSystem.g.query(
            """PREFIX  lss-usdl: <http://w3id.org/lss-usdl/v1#>
               PREFIX time: <http://www.w3.org/2006/time/>
                SELECT DISTINCT ?lss ?tgt
                WHERE {
                  ?lss lss-usdl:hasControlFlow ?cf.
                  ?cf lss-usdl:hasSource ?src  .
                  ?cf lss-usdl:hasTarget ?tgt .
                  MINUS {?temp lss-usdl:hasTarget ?src .}
                }""")

        interaction = ''
        for row in qres:
            s, i= row
            service = s.rsplit("#", 2)[1]
            interaction = i.rsplit("#", 2)[1]
           
        return interaction



#------------------------------------------------------------------
#-------------- get last interaction(s) ------------------------- 
#------------------------------------------------------------------
# Look for an interaction which is a target but not the source of any connector
#
    def getLastInteraction(self):
        qres = ServiceSystem.g.query(
            """PREFIX  lss-usdl: <http://w3id.org/lss-usdl/v1#>
               PREFIX time: <http://www.w3.org/2006/time/>
                SELECT DISTINCT ?lss ?tgt
                WHERE {
                  ?lss lss-usdl:hasControlFlow ?cf.
                  ?cf lss-usdl:hasSource ?src  .
                  ?cf lss-usdl:hasTarget ?tgt .
                  MINUS {?temp lss-usdl:hasSource ?tgt .}
                }""")

        interaction = ''
        for row in qres:
            s, i= row
            service = s.rsplit("#", 2)[1]
            interaction = i.rsplit("#", 2)[1]
           
        return interaction



#------------------------------------------------------------------
#-------------- get DBpedia Resources -----------------------------
#------------------------------------------------------------------
    def getDBPediaResources(self):
        qres = ServiceSystem.g.query(
            """PREFIX  lss-usdl: <http://w3id.org/lss-usdl/v1#>
               PREFIX dbpedia: <http://dbpedia.org/>
                SELECT DISTINCT ?int ?res ?dbres
                WHERE {
                  ?lss lss-usdl:hasInteraction ?int .
                  ?int lss-usdl:createsResource ?res .
                  ?res a ?dbres .
                }""")

        results = []
        for row in qres:
            i, r, dbr = row
            interaction = i.rsplit("#", 2)[1]
            resource = r.rsplit("#", 2)[1]
            results.append([interaction, resource, dbr])
           
        return results

#------------------------------------------------------------------
#-------------- get Abstract for DBpedia Resource -----------------
#------------------------------------------------------------------
    def getDBPediaAbstract(self, resource):

    #              ?dbres <http://dbpedia.org/ontology/abstract> ?abs .
        sparql=SPARQLWrapper("http://dbpedia.org/sparql")
        qs="""SELECT DISTINCT ?abs 
             WHERE { 
             <"""
        qe="""> dbpedia-owl:abstract ?abs . 
              FILTER(langMatches(lang(?abs), "EN")) 
             }"""

        q=qs+resource+qe
        sparql.setQuery(q)
        sparql.setReturnFormat(JSON)
        sparqlresults=sparql.query().convert()

        results = []
        for sparqlresult in sparqlresults["results"]["bindings"]:
            str = sparqlresult["abs"]["value"] + ''
            results.append(str)

        return results
        

ss = ServiceSystem("file:ITIL_IM_service.ttl")
results = ss.getServiceInformation()
print "Service System name: " + results[0].rsplit("#", 2)[1] 
print "Service System desc: " + results[1]
print("")        

results = ss.getInteractions()
for interation in results:
    print "Interaction: " + interation
print("")        

results = ss.getConnectors()
for result in results:
    str = 'getConnectors: (' + result[0] + ' -> ' + result[1] + ') with condition "' + result[2] + '"'''
    print str
print("")        

results = ss.getRoles()
for role in results:
    print "getRoles: " + role
print("")  

results = ss.getInterationsByRole()
for result in results:
    str = 'getInterationsByRole: ' + result[0] + ' with role ' + result[1]
    print str
print("") 

results = ss.getInteractionResources()
for result in results:
    str = 'getInteractionResources: ' + result[0] + ' with resource ' + result[1]
    print str
print("") 

results = ss.getInteractionResourcesReceived()
for result in results:
    str = 'getInteractionResourcesReceived: ' + result[0] + ' with resource ' + result[1]
    print str
print("") 

results = ss.getFirstInteraction()
str = 'getFirstInteraction: ' + results 
print str
print("") 

results = ss.getLastInteraction()
str = 'getLastInteraction: ' + results 
print str
print("") 

results = ss.getDBPediaResources()
for result in results:
    str = 'getDBPediaResources: ' + result[0] + ' with resource ' + result[1] + ' -> ' + result[2]
    print str
print("") 

results = ss.getDBPediaResources()
for result in results:
    dbpediaAbstracts = ss.getDBPediaAbstract(result[2])
    for dbpediaAbstract in dbpediaAbstracts:
        str = 'getDBPediaAbstract: ' + result[2] + ': ' +  dbpediaAbstract 
        print str
        print("") 
print("") 







