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