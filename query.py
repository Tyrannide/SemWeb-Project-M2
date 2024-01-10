# pip install sparqlwrapper
# pip install geopy
import SPARQLWrapper as spq
from datetime import datetime
from geopy import Nominatim
from geopy.distance import geodesic
import sys


def usage():
    print("Wrong parmaters for the program query:\nYou should call it like:\n\tpython query.py --ranked-by (distance|price)")

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

    orderQuery = ""
    sortingDistance = False

    if len(sys.argv) == 3:
        print("Requête simple trier soit par prix, soit par distance")
        if '--ranked-by' and 'distance' in sys.argv:
            print("Filtre par distance")
            sortingDistance = True
        elif '--ranked-by' and 'price' in sys.argv:
            print("Filtre par prix")
            orderQuery = "ORDER BY ?deliveryPrice ?deliveryMinimalCost"
        else:
            usage()
            exit()
    else:
        usage()
        exit()

    print('Argument List:', str(sys.argv))

    day_index = {"Mo" : 1,"Tu": 2, "We": 3, "Th": 4, "Fr": 5, "Sa": 6, "Su": 7}

    max_range = 5
    
    # test : "50 rue Conte Grandchamp, 42000 Saint-Étienne"
    adress = convert_co("50 rue Conte Grandchamp, 42000 Saint-Étienne")
    
    # food = input("Please enter what type of food you want : ")
    max_price = 20
    
    date = "10-01-2024"
    date = datetime.strptime(date, "%d-%m-%Y")
    date = str(date.strftime("%A"))[:2]


    hours = "11:45:00"

    # doc : https://sparqlwrapper.readthedocs.io/en/latest/main.html#command-line-script
    sparq = spq.SPARQLWrapper("http://localhost:8000") 


    sparq.setQuery(f"""
        PREFIX sh1: <https://schema.org/>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT DISTINCT ?restaurant ?longitude ?latitude ?deliveryPrice ?deliveryMinimalCost ?hours 
        WHERE {{
            ?restaurant a sh1:Restaurant ;
            sh1:address ?add;
            sh1:openingHours ?hours;
            sh1:potentialAction ?pa.
            
            ?add a sh1:Place ;
            sh1:latitude ?latitude ;
            sh1:longitude ?longitude .
            
            ?pa sh1:PriceSpecification ?ps.
            
            ?ps sh1:price ?deliveryPrice.
            
            ?ps sh1:eligibleTransactionVolume ?etv.
            
            ?etv sh1:price ?deliveryMinimalCost .
                   
            FILTER (
                ?deliveryMinimalCost < {max_price}
            )
        
        }}
        {orderQuery}
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
    if sortingDistance:
        results.sort(key=lambda r: geodesic(adress, (float(r["latitude"]["value"]), float(r["longitude"]["value"]))).kilometers)
    for r in results :
        print(r)

    