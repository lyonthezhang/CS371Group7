# Constants to be used

# Queries
INITIAL_QUERY = """
SELECT ?item ?itemLabel WHERE {
  ?item wdt:P31 wd:Q1093829.
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}
LIMIT 10
"""

QUERY_FOR_CAPITALS = """
SELECT ?item ?itemLabel WHERE {
  ?item wdt:P31 wd:Q1093829.
  ?item wdt:P1376 ?capitalPlace.
  ?capitalPlace wdt:P31 wd:Q35657.
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}
"""

# P- wikidata codes
INSTANCE_OF = "P31"
LOCATED_IN_TERRITORY = "P131"
LOCATED_IN_TIME_ZONE = "P421"
POPULATION = "P1082"
AREA = "P2046"
CAPITAL_OF = "P1376"
INCEPTION_DATE = "P571"

# Q- wikidata codes
US_STATE = "Q35657"
US_TERRITORY = "Q1352230"

# List of valid ids to be used
# Instance of, Inception Date, Capital of, Located in Administrative, Located body of water, population,
# Contains administrative enties (boroughs), Located in time zone, Area, Postal Code
VALID_IDS = set(["P31","P571","P1376","P131","P206","P1082","P150","P421","P2046","P281"])

# Eastern, Central, Mountain, Western, Alaskan, Hawaii
TIME_ZONES = [["Q941023", "Q5390"], ["Q2086913", "Q5385"], ["Q3134980", "Q2212"], ["Q847142", "Q2204"], ["Q3238805", "Q2183"], ["Q3241537", "Q2163"]]
