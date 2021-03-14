# Imports up here
from SPARQLWrapper import SPARQLWrapper, JSON
from wikidata.client import Client
from helpers import *
from constants import *
import datetime
import pandas as pd
from sklearn.preprocessing import OneHotEncoder


# From https://www.wikidata.org/wiki/Wikidata:SPARQL_query_service/queries/examples#Cats
# Querying Wikidata

# Run a sparql query
def run_sparql_query(query):
    sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
    sparql.setQuery(query)

    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()

    return results


# Initialize wikidata client once
wiki_data_client = Client()

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

# THE END RESULT
# info contains P:Q mappings (instance of: big city for example for New York)
# info is a list, where each entry is a tuple of size 2 containing a 1) value containing the P and 2) another list containing relevant entities


# Constructs a matrix (list of lists) given a list of data_points
def construct_matrix(cities_data):
    columns = ["city"]
    columns_set = set(columns)
    column_location = {"city": 0}

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
                col_val = get_population(
                    max([get_identifier(population) for population in values]))

            elif a_id == LOCATED_IN_TIME_ZONE:
                index = column_location[a_id]
                col_val = get_time_zone([get_identifier(val)
                                         for val in values])

            elif a_id == LOCATED_IN_TERRITORY:
                index = column_location[a_id]
                col_val = get_state(values)

            city_info[index] = col_val

        table.append(city_info)

    return table

# Returns a one hot encoded pandas df given a matrix(list of lists)


def one_hot_encode(matrix):

    # Make pandas df
    df = pd.DataFrame(matrix[1:], columns=matrix[0])
    encoder = OneHotEncoder()
    print_df_for_demo(df)

    # Some cities don't have timezone or inception date (wikidata is whack)
    has_time_zone = False
    has_inception_date = False
    has_area = False
    has_state = False
    has_population = False

    categorical_cols = []
    
    for col_name in df.columns:
        if col_name in CATEGORICAL_IDS:
            categorical_cols.append(col_name)

    for i in range(df.shape[0]):

        if LOCATED_IN_TIME_ZONE in categorical_cols and df.loc[i, LOCATED_IN_TIME_ZONE] == 0:
            df.loc[i, LOCATED_IN_TIME_ZONE] = "NA"
        
        if INCEPTION_DATE in categorical_cols and df.loc[i, INCEPTION_DATE] == 0:
            df.loc[i, INCEPTION_DATE] = "NA"
        
        if AREA in categorical_cols and df.loc[i, AREA] == 0:
            df.loc[i, AREA] = "NA"
        
        if LOCATED_IN_TERRITORY in categorical_cols and df.loc[i, LOCATED_IN_TERRITORY] == 0:
            df.loc[i, LOCATED_IN_TERRITORY] = "NA"
        
        if POPULATION in categorical_cols and df.loc[i, POPULATION] == 0:
            df.loc[i, POPULATION] = "NA"

    # Get one hot encoded df for catergorical variables
    oe_results = encoder.fit_transform(df[categorical_cols])
    new_column_names = encoder.get_feature_names(categorical_cols)

    # Add one hot encoded data to original df
    one_hot_encoded_df = df.join(pd.DataFrame(
        oe_results.toarray(), columns=new_column_names))

    # Drop the orginial catergorical columns (repalced with one hot encoded columns) and the NA ones
    drop_cols = []
    for col_name in POTENTIAL_DROP_COLS:
        if col_name in one_hot_encoded_df.columns:
            drop_cols.append(col_name)

    one_hot_encoded_df = one_hot_encoded_df.drop(columns=drop_cols)

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
def find_attribute_to_split_on(query, size):
    # First run a sparql with 20 cities
    # ******* MAKE SURE TO INCLUDE LIMIT 20 in the query ******
    results = run_sparql_query(query)

    # Get the data for them (pick off the first 20 just in case)
    data = results['results']['bindings'][:size]

    # Get all of the cities data for every city in data
    cities_data = []
    for city in data:
        city_id, attribute_data = get_attributes(city)
        if city_id and attribute_data:
            cities_data.append((city_id, attribute_data))

    # Construct a matrix
    matrix = construct_matrix(cities_data)

    # Uncomment/Comment this if you want it to print the matrix in "matrix.txt"
    print_matrix(matrix)

    # Get the one hot encoded pandas df of the matrix
    one_hot = one_hot_encode(matrix)

    # Uncomment/Comment this if you want it to print the matrix in "matrix_one_hot.txt"
    print_df(one_hot)

    # Select the attribute to split on
    selection = select_attribute(one_hot)

    # Return the selection
    return selection

# This is the game. Run this to run the game


def game():

    print("Welcome to our 20 Questions Bot")

    query = INITIAL_QUERY
    prev_questions = set()
    
    for question_number in range(NUM_QUESTIONS):
        # Find a selection based on the query
        #print(query)
        selection = find_attribute_to_split_on(query, SAMPLE_SIZE)
        # Ask user a question based on the selection
        question = format_question(selection)
        
        if question in prev_questions:
            print(f"The bot determined that the best question to ask is the same as a previous question.")
            print(f"Making a new query with a bigger sample size ...")

            selection = find_attribute_to_split_on(query, BIGGER_SAMPLE_SIZE)
            question = format_question(selection)

            if question in prev_questions:
                print("Could not find a better question to split on.\nBot is ending the game now ...")
                break
            
        prev_questions.add(question)

        print(question)
        answer = input("(y/n): ")

        # Append to the query based on the selection and the answer
        query = construct_new_query(query, selection, answer)

    # query is now a long query that has narrowed down the cities to some degree. Get some sort of final answer from that query
    final_results = run_sparql_query(query)
    final_answer = get_final_answer(final_results)

    print(f"Is your answer of of the following: {final_answer}")
    answer = input("(y/n): ")

    if answer == "y":
        print("Awesome! Thank you for playing the game")
    else:
        print("We're sorry. Please play again or increase sample size in constants.py for better results.")


game()
