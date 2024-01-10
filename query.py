# pip install sparqlwrapper
# pip install geopy
import SPARQLWrapper as spq
from datetime import datetime
from geopy import Nominatim
from geopy.distance import geodesic
import sys

def convert_co(adress):
    convert = Nominatim(user_agent="ME_and_ME")
    co = convert.geocode(adress)

    if co:
        lat, long = co.latitude, co.longitude
        return lat, long
    else:
        print("Adress not found.")
        return None

if __name__ == "__main__":

    print(len(sys.argv))
    print('Argument List:', str(sys.argv))

    day_index = {"Mo" : 1,"Tu": 2, "We": 3, "Th": 4, "Fr": 5, "Sa": 6, "Su": 7}

    max_range = 5
    
    # test : "50 rue Conte Grandchamp, 42000 Saint-Étienne"
    adress = convert_co("50 rue Conte Grandchamp, 42000 Saint-Étienne")
    
    # food = input("Please enter what type of food you want : ")
    max_price = 18
    
    date = "10-01-2024"
    date = datetime.strptime(date, "%d-%m-%Y")
    date = str(date.strftime("%A"))[:2]


    hours = "11:45:00"

    # doc : https://sparqlwrapper.readthedocs.io/en/latest/main.html#command-line-script
    sparq = spq.SPARQLWrapper("http://localhost:8000") 


    sparq.setQuery(f"""
        PREFIX schema: <https://schema.org/>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT DISTINCT ?restaurant ?longitude ?latitude ?address ?accessPrice
        WHERE {{
                ?restaurant a schema:Restaurant ;
                schema:address ?add;
                schema:potentialAction ?pa.
                
                ?add a schema:Place ;
                schema:address ?address ;
                schema:latitude ?latitude ;
                schema:longitude ?longitude .  

                ?pa a schema:PriceSpecification .     
                
        }}
        LIMIT 1000
        OFFSET 0        
        """)

    # classique
    # sparq.setQuery(f"""
    #     PREFIX schema: <https://schema.org/>

    #     SELECT DISTINCT ?restaurant ?latitude ?longitude
    #     WHERE {{
    #             ?restaurant a schema:Restaurant ;
    #             schema:address ?ad ;
    #             schema:potentialAction ?p ;
    #             schema:openingHours ?open .

    #             ?p a schema:priceSpecification ;
    #             schema:eligibleTransactionVolume ?p2 .

    #             ?p2 schema:price ?price .
                
    #             BIND(STRBEFORE(?open, " ") AS ?days).
    #             BIND(MAP({
    #                 "Mo": 1, "Tu": 2, "We": 3, "Th": 4, "Fr": 5, "Sa": 6, "Su": 7
    #             })[STRBEFORE(?days, "-")] AS ?dayStart).
    #             BIND(MAP({
    #                 "Mo": 1, "Tu": 2, "We": 3, "Th": 4, "Fr": 5, "Sa": 6, "Su": 7
    #             })[STRAFTER(?days, "-")] AS ?dayEnd) .
                
    #             BIND(STRAFTER(?open, " ") AS ?hours).
    #             BIND(CONCAT(STRBEFORE(?hours, "-"),":00") AS ?hStart).
    #             BIND(CONCAT(STRAFTER(?hours, "-"),":00") AS ?hEnd).
                                
    #             ?ad a schema:Place ;
    #             schema:latitude ?latitude;
    #             schema:longitude ?longitude .
                
    #             FILTER (
    #                 ?price < {max_price} &&
    #                 ?dayStart <= {day_index[date]} &&
    #                 ?dayEnd >= {day_index[date]} &&
    #                 xsd:time(?hStart) <= xsd:time({hours}) &&
    #                 xsd:time(?hEnd) >= xsd:time({hours})
    #             )
    #     }} 
    # """)

    sparq.setReturnFormat(spq.JSON)
    res = sparq.query().convert()
    
    # voir à quoi le retour ressemble pour la boucle de tri (distance)
   
    #for r in res["results"]["bindings"]:
    #    print(geodesic(adress, (float(r["latitude"]["value"]),float(r["longitude"]["value"]))).kilometers)
    #    exit()
    
    results = [r for r in res["results"]["bindings"] if geodesic(adress, (float(r["latitude"]["value"]),float(r["longitude"]["value"]))).kilometers <= max_range]
    
    for r in results :
        print(r)

    