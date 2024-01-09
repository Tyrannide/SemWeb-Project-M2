# pip install sparqlwrapper
# pip install geopy
import SPARQLWrapper as spq
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


    max_range = int(input("Please enter a max range in Km (default 5) : "))

    if max_range <= 0 :
        max_range = 5

    adress = None
    while not adress :
        # test : "50 rue Conte Grandchamp, 42000 Saint-Étienne"
        adress = convert_co(input("Please enter your adresse : "))
    
    food = input("Please enter what type of food you want : ")
    max_price = float(input("Please enter your max price : "))
    # format à voir
    date = input("Please enter the date on the delivery (dd/mm/yyyy) : ")
    time = input("Please enter a time (hh:mm) : ")

    # doc : https://sparqlwrapper.readthedocs.io/en/latest/main.html#command-line-script
    sparq = spq.SPARQLWrapper("http://localhost:8000") 


    # classique
    sparq.setQuery(f"""
        PREFIX schema: <https://schema.org/>

        SELECT DISTINCT ?restaurant ?latitude ?longitude
        WHERE {{
                ?restaurant a schema:Restaurant ;
                schema:address ?ad ;
                schema:potentialAction ?p .

                ?p a schema:priceSpecification ;
                schema:eligibleTransactionVolume ?p2 .

                ?p2 schema:price ?price .
                  
                ?ad a schema:Place ;
                schema:latitude ?latitude;
                schema:longitude ?longitude .
                
                FILTER (?price < {max_price})
        }} 
    """)

    sparq.setReturnFormat(spq.JSON)
    res = sparq.query().convert()
    
    # voir à quoi le retour ressemble pour la boucle de tri (distance)
   
    #for r in res["results"]["bindings"]:
    #    print(geodesic(adress, (float(r["latitude"]["value"]),float(r["longitude"]["value"]))).kilometers)
    #    exit()
    
    results = [r for r in res["results"]["bindings"] if geodesic(adress, (float(r["latitude"]["value"]),float(r["longitude"]["value"]))).kilometers <= max_range]
    
    for r in results :
        print(r)

    