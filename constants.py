# Constants to be used

# Queries
INITIAL_QUERY = """
SELECT ?item ?itemLabel WHERE {
  ?item wdt:P31 wd:Q1093829.
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}
LIMIT 20
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
# Instance of, Inception Date, Located in Administrative, population,
# Located in time zone, Area,
VALID_IDS = set(["P31","P571","P131","P1082","P421","P2046"])

# Categorical IDS
CATEGORICAL_IDS = ["P131", "P421", "P571", "P1082", "P2046"]

# Potentila ids. Capital of, Postal Code, Located body of water, Contains administrative enties (boroughs)
POTENTIAL_IDS = ["P1376", "P281", "P206", "P150"]

# Eastern, Central, Mountain, Western, Alaskan, Hawaii
TIME_ZONES = [["Q941023", "Q5390"], ["Q2086913", "Q5385"], ["Q3134980", "Q2212"], ["Q847142", "Q2204"], ["Q3238805", "Q2183"], ["Q3241537", "Q2163"]]

# Constants for population
LESS_THAN_1000 = "LESS_THAN_1000"
BETWEEN_1000_AND_500000 = "BETWEEN_1000_AND_500000"
BETWEEN_50000_AND_100000 = "BETWEEN_50000_AND_100000"
BETWEEN_100000_AND_500000 = "BETWEEN_100000_AND_500000"
BETWEEN_500000_AND_1MIL = "BETWEEN_500000_AND_1MIL"
MORE_THAN_1_MIL = "MORE_THAN_5_MIL"

# Constatns for Inception date
BEFORE_1600S = "BEFORE_1600S"
DURING_1600S = "DURING_1600S"
DURING_1700S = "DURING_1700S"
DURING_1800S = "DURING_1800S"
DURING_1900S = "DURING_1900S"
DURING_2000S = "AFTER_1900S"

# Cnstants for Area
UNDER_100 = "UNDER_100"
BETWEEN_100_AND_500 = "BETWEEN_100_AND_500"
BETWEEN_500_AND_1000 = "BETWEEN_500_AND_1000"
BETWEEN_1000_AND_1500 = "BETWEEN_1000_AND_1500"
OVER_15000 = "OVER_1500"