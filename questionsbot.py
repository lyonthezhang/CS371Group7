### Imports up here
from SPARQLWrapper import SPARQLWrapper, JSON
from wikidata.client import Client
from helpers import *
from constants import *
import datetime
import pandas as pd
from sklearn.preprocessing import OneHotEncoder


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

    # Sometimes doing lists() fail so just put it in a try except block
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


# Constructs a matrix (list of lists) given a list of data_points
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
                    col_name = a_id + "_" + get_identifier(value)

                    if col_name not in columns_set:
                        column_location[col_name] = len(columns)
                        columns.append(col_name)
                        columns_set.add(col_name)

            else:
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
                    col_name = a_id + "_" + get_identifier(value)
                    index = column_location[col_name]
                    col_val = 1

                    city_info[index] = col_val

            elif a_id == INCEPTION_DATE:
                index = column_location[a_id]
                col_val = get_inception(get_identifier(values[0]))
            
            elif a_id == AREA:
                index = column_location[a_id]
                col_val = get_area(get_identifier(values[0]))
            
            elif a_id == POPULATION:
                index = column_location[a_id]
                col_val = get_population(max([get_identifier(population) for population in values]))

            elif a_id == LOCATED_IN_TIME_ZONE:
                index = column_location[a_id]
                col_val = get_time_zone([get_identifier(val) for val in values])
            
            elif a_id == LOCATED_IN_TERRITORY:
                index = column_location[a_id]
                col_val = get_state(values)

            city_info[index] = col_val

        table.append(city_info)
    
    return table

# Returns a one hot encoded pandas df given a matrix(list of lists)
def one_hot_encode(matrix):
    
    # Make pandas df
    df = pd.DataFrame(matrix[1:], columns = matrix[0])
    encoder = OneHotEncoder()
    
    # Some cities don't have timezone (wikidata is whack)
    for i in range(df.shape[0]):
        time_zone_value = df.loc[i, LOCATED_IN_TIME_ZONE]
        if time_zone_value == 0:
            df.loc[i, LOCATED_IN_TIME_ZONE] = "NA"

    # Get one hot encoded df for catergorical variables
    oe_results = encoder.fit_transform(df[CATEGORICAL_IDS])
    new_column_names = encoder.get_feature_names(CATEGORICAL_IDS)

    # Add one hot encoded data to original df
    one_hot_encoded_df = df.join(pd.DataFrame(oe_results.toarray(), columns=new_column_names))

    # Drop the orginial catergorical columns (repalced with one hot encoded columns) and the NA timezone one
    one_hot_encoded_df = one_hot_encoded_df.drop(columns = CATEGORICAL_IDS+[LOCATED_IN_TIME_ZONE+"_NA"])

    return one_hot_encoded_df

# Give a one hot encoded pandas df, return a column name to split on
def select_attribute(df):
    best_diff = float("inf")
    best_col = ""
    target = df.shape[0]/2

    for col_name in df.columns[1:]:
        total = df[col_name].sum()
        diff = abs(total - target)
        if diff < best_diff:
            best_col = col_name
            best_diff = diff
    
    return best_col
        

# The following has the general workflow
# It takes a query, it finds an attribute to split on, and it returns it
def find_attribute_to_split_on(query):
    # First run a sparql with 20 cities
    # ******* MAKE SURE TO INCLUDE LIMIT 20 in the query ******
    results = run_sparql_query(query)

    # Get the data for them (pick off the first 20 just in case)
    data = results['results']['bindings'][:20]

    # Get all of the cities data for every city in data
    cities_data = []
    for city in data:
        city_id, attribute_data = get_attributes(city)
        if city_id and attribute_data:
            cities_data.append((city_id, attribute_data))

    # Construct a matrix
    matrix = construct_matrix(cities_data)

    print_matrix(matrix) # Uncomment/Comment this if you want it to print the matrix in "matrix.txt"
    
    # Get the one hot encoded pandas df of the matrix
    one_hot = one_hot_encode(matrix)

    print_df(one_hot) # Uncomment/Comment this if you want it to print the matrix in "matrix_one_hot.txt"

    # Select the attribute to split on
    selection  = select_attribute(one_hot)

    # Return the selection
    return selection

# This is the game. Run this to run the game
def game():
    
    print("Welcome to our 20 Questions Bot")
    
    query = INITIAL_QUERY

    for question_number in range(20):
        # Find a selection based on the query
        selection = find_attribute_to_split_on(query)
        # Ask user a question based on the selection
        question = format_question(selection)
        
        print(question)
        answer = input("(y/n): ")

        # Append to the query based on the selection and the answer
        query = construct_new_query(query, selection, answer)

    # query is now a long query that has narrowed down the cities to some degree. Get some sort of final answer from that query
    final_answer = get_final_answer(query)

    print(f"Is your answer {final_answer}")