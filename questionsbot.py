### Imports up here
from SPARQLWrapper import SPARQLWrapper, JSON
from wikidata.client import Client
from helpers import extract_id_from_url, get_identifier, get_state, get_time_zone, valid_id
from constants import *
import datetime


# From https://www.wikidata.org/wiki/Wikidata:SPARQL_query_service/queries/examples#Cats
### Querying Wikidata

# Run a sparql query
def run_sparql_query(query):
    sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
    sparql.setQuery(query)
    
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()

    return results


# Initialize wikidata client once
wiki_data_client  = Client()

# Get attributes of a data using wikidata library
def get_attributes(data):

    url = data['item']['value']
    target_id = extract_id_from_url(url)

    try:
        entity = wiki_data_client.get(target_id, load=True)
        attributes = entity.lists()
        return (target_id, attributes)
    except:
        return (None, None)

# Keeping this commented in case we need to reference other functions for entities
# print(entity.__dir__())

###### THE END RESULT
###### info contains P:Q mappings (instance of: big city for example for New York)
###### info is a list, where each entry is a tuple of size 2 containing a 1) value containing the P and 2) another list containing relevant entities  



def construct_matrix(cities_data):
    columns = ["city"]
    columns_set = set(columns)
    column_location = {"city" : 0}

    # This for loop goes through all of the cities_data and constructs all of the columns
    for city_data in cities_data:

        attribute_data = city_data[1]

        for attribute, values in attribute_data:
            a_id = get_identifier(attribute)

            if not(valid_id(a_id)):
                continue
        
            if a_id == INSTANCE_OF:
                for value in values:
                    col_name = a_id + "." + get_identifier(value)

                    if col_name not in columns_set:
                        column_location[col_name] = len(columns)
                        columns.append(col_name)
                        columns_set.add(col_name)

            if a_id == INCEPTION_DATE or a_id == CAPITAL_OF or a_id == POPULATION or a_id == LOCATED_IN_TIME_ZONE or a_id == AREA or a_id == LOCATED_IN_TERRITORY:
                col_name = a_id
                if col_name not in columns_set:
                    column_location[col_name] = len(columns)
                    columns.append(col_name)
                    columns_set.add(col_name)
                
    
    table = [columns]

    # Go through all of the cities_data and fill out each city's data for each column
    for city_data in cities_data:

        city_id, attribute_data = city_data[0], city_data[1]
        
        city_info = [0]*len(columns)
        city_info[0] = city_id

        for attribute, values in attribute_data:

            a_id = get_identifier(attribute)

            if not(valid_id(a_id)):
                continue
            
            if a_id == INSTANCE_OF:
                for value in values:
                    col_name = a_id + "." + get_identifier(value)
                    index = column_location[col_name]
                    col_val = 1

                    city_info[index] = col_val

            elif a_id == INCEPTION_DATE or a_id == CAPITAL_OF or a_id == AREA:
                index = column_location[a_id]
                col_val = get_identifier(values[0])
            
            elif a_id == POPULATION:
                index = column_location[a_id]
                col_val = max([get_identifier(population) for population in values])

            elif a_id == LOCATED_IN_TIME_ZONE:
                index = column_location[a_id]
                col_val = get_time_zone(get_identifier(values[0]))
            
            elif a_id == LOCATED_IN_TERRITORY:
                index = column_location[a_id]
                col_val = get_state(values)

            city_info[index] = col_val

        table.append(city_info)
    
    return table


def main():
    import time
    t0 = time.time()

    results = run_sparql_query(INITIAL_QUERY)
    data = results['results']['bindings'][0:10]
    t1 = time.time()

    print(f"Make query: {t1-t0}")

    cities_data = []
    for city in data:
        city_id, attribute_data = get_attributes(city)
        if city_id and attribute_data:
            cities_data.append((city_id, attribute_data))

    t2 = time.time()
    print(f"Get attributes: {t2-t1}")

    table = construct_matrix(cities_data)
    
    t3 = time.time()
    print(f"Construct Matrix: {t3-t2}")

    return table

matrix = main()
f = open("matrix.txt","w")
for line in matrix:
    for item in line:
        f.write(str(item) + " "*(14-len(str(item))) + "|" )
    f.write("\n")
f.close()

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