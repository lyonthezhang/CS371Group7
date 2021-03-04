### Imports up here
from SPARQLWrapper import SPARQLWrapper, JSON
from wikidata.client import Client
from helpers import extract_id_from_url

# From https://www.wikidata.org/wiki/Wikidata:SPARQL_query_service/queries/examples#Cats
### Querying Wikidata

sparql = SPARQLWrapper("https://query.wikidata.org/sparql")

# Starter query here that looks for American Cities
sparql.setQuery("""
SELECT ?item ?itemLabel WHERE {
  ?item wdt:P31 wd:Q1093829.
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}
LIMIT 10
""")

sparql.setReturnFormat(JSON)
results = sparql.query().convert()

testresult = results['results']['bindings'][0]
print("Sample result from query: ", testresult)

### More detail about query result

client = Client()

sample_url = testresult['item']['value']
target_id = extract_id_from_url(sample_url)

entity = client.get(target_id, load=True)

# Keeping this commented in case we need to reference other functions for entities
# print(entity.__dir__())

###### THE END RESULT
###### info contains P:Q mappings (instance of: big city for example for New York)
###### info is a list, where each entry is a tuple of size 2 containing a 1) value containing the P and 2) another list containing relevant entities
info = entity.lists()

### Bot Loop
### COMMENTED OUT FOR NOW

# print("Welcome to our 20 Questions Bot")

# query = None
# answer = None
# final_answer = None

# for i in range(20):
# 	query = "TEMPORARY CHANGE ME"
# 	print("Question " + str(i + 1) + ": " + query)
# 	answer = input("(y/n): ")

# print("Is your answer blah blah blah")