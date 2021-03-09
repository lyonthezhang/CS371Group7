import datetime
from constants import *
from wikidata.entity import Entity
from wikidata.globecoordinate import GlobeCoordinate
from wikidata.quantity import Quantity
from wikidata.commonsmedia import File
from wikidata.multilingual import MonolingualText


# Get the id of an entity from the url
def extract_id_from_url(url_string):
	return url_string.split('/')[-1]


# Check if the entity id is one of the entites pre-selected to be relevant
def valid_id(entity_id):
    return entity_id in VALID_IDS


# Get the time zone given an entity id. This is because wikidata does not have a standard for storing the time_zone for places
def get_time_zone(entity_id):

    for zone in TIME_ZONES:
        if entity_id in zone:
            return zone[0]
    
    return entity_id


# Helper for get_state. Param is a list of entities. It goes through and check if each entity is an istance of a us_state or a us_territory.
# If it is then you know that it is a state
def get_state_helper(potential_states):
    
    for p_state in potential_states:
        # ************************************** note ******************************************************
        # doing .lists() sometimes fails for some reason (it is because of an error in the wikidata library)
        # not sure how to fix this but wanted to point it out
        # **************************************************************************************************
        attribute_data = p_state.lists()

        for attribute, values in attribute_data:
            if get_identifier(attribute) == INSTANCE_OF:
                for value in values:
                    if get_identifier(value) == US_STATE or get_identifier(value) == US_TERRITORY:
                        return get_identifier(p_state)
    
    return None


# Gets the state given a list of potential states. Param is a list of entities
def get_state(potential_states):

    state_id = get_state_helper(potential_states)
    
    if state_id:
        return state_id

    # All p_states in potential_states are counties
    # Work with the first county
    county = potential_states[0]

    # ************************************** note ******************************************************
    # doing .lists() sometimes fails for some reason (it is because of an error in the wikidata library)
    # not sure how to fix this but wanted to point it out
    # **************************************************************************************************
    attribute_data = county.lists()

    # Get the located in administrative body stuff
    potential_states2 = []
    for attribute, values in attribute_data:
        if get_identifier(attribute) == LOCATED_IN_TERRITORY:
            for value in values:
                potential_states2.append(value)
    
    state_id = get_state_helper(potential_states2)

    return state_id


# Returns an identifer given an object (entity or others). It will return values of int, str, and float
def get_identifier(dat):
    if type(dat) == Entity:
        return(dat.id)
    elif type(dat) == GlobeCoordinate:
        return(f"Latitude: {dat.latitude}, Longitude: {dat.longitude}")
    elif type(dat) == int or type(dat) == str:
        return(dat)
    elif type(dat) == Quantity:
        return(dat.amount)
    elif type(dat) == File or type(dat) == MonolingualText:
        return "INVALID"
    elif type(dat) == datetime.date:
        return(dat.year)
    else:
        print(dat)
        print(type(dat))
        return "UNKNOWN"

# Maps a continous numerical population to a category
def get_population(num):
    if num < 1000:
        return LESS_THAN_1000
    elif num < 50000:
        return BETWEEN_1000_AND_500000
    elif num < 100000:
        return BETWEEN_50000_AND_100000
    elif num < 500000:
        return BETWEEN_100000_AND_500000
    elif num < 1000000:
        return BETWEEN_500000_AND_1MIL
    else:
        return MORE_THAN_1_MIL

# Maps a continous numerical inception year to a category
def get_inception(num):
    if num < 1600:
        return BEFORE_1600S
    elif num < 1700:
        return DURING_1600S
    elif num < 1800:
        return DURING_1700S
    elif num < 1900:
        return DURING_1800S
    elif num < 2000:
        return DURING_1900S
    else:
        return DURING_2000S

# Maps a continous numerical area to a category
def get_area(num):
    if num < 100:
        return UNDER_100
    elif num < 500:
        return BETWEEN_100_AND_500
    elif num < 1000:
        return BETWEEN_500_AND_1000
    elif num < 1500:
        return BETWEEN_1000_AND_1500
    else:
        return OVER_15000

def print_matrix(matrix):
    f = open("matrix.txt","w")
    for line in matrix:
        for item in line:
            f.write(str(item) + " "*(25-len(str(item))) + "|" )
        f.write("\n")
    f.close()

def print_df(df):
    f = open("matrix_one_hot.txt","w")
    df.to_string(f)
    f.close()


# Take a selection and outputs a question (string) that the user can understand
# See column names in "matrix_one_hot.txt" to see what the selections are going to look like
# Note: the column names in "matrix_one_hot.txt" are not an all inclusive list on the possible selections
def format_question(selection):

    raise NotImplementedError


# Take an old_query, selection, and an answer from the user and return a new_query(string) with the answer to the selection appended
# on to the old_query that can be run on SPARQL
# See column names in "matrix_one_hot.txt" to see what the selections are going to look like
# Note: the column names in "matrix_one_hot.txt" are not an all inclusive list on the possible selections
def construct_new_query(old_query, selection, answer):
    
    raise NotImplementedError


# Take a really long query that has narrowed down the options to some degree.
# Can implement this one of two ways:
#   1. Format the query into some sort of text that is readable by the user
#   2. Run the query. Get the first 10 results or so. And return them as potential answers
# Second option is easier IMO
# Make sure you retun a string either way
def get_final_answer(query):
    
    raise NotImplementedError