# pip install sparqlwrapper
# pip install geopy
import SPARQLWrapper as spq
from datetime import datetime, time
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

    """if len(sys.argv) == 3:
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
    """
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


    hours = "11:45"
    hours = hours.split(":")

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

    sparq.setReturnFormat(spq.JSON)
    res = sparq.query().convert()

    results = [r for r in res["results"]["bindings"] if geodesic(adress, (float(r["latitude"]["value"]),float(r["longitude"]["value"]))).kilometers <= max_range]
    if sortingDistance:
        results.sort(key=lambda r: geodesic(adress, (float(r["latitude"]["value"]), float(r["longitude"]["value"]))).kilometers)
    for r in results :
        print(r)
    
    res_hours = []
    for r in results :
        # print(r["hours"]["value"])
        
        for tmp in r["hours"]["value"].split(", ") :
            day_open = []
            # print("\t"+t)
            dtmp,htmp = tmp.split(" ")
            d = dtmp.split(",")

            for x in d :
                if len(x) == 2 :
                    tmptab = [day_index[x]]
                else :
                    x = x.split("-")
                    tmptab = [j for j in range(day_index[x[0]],day_index[x[1]]+1)]
                day_open += tmptab

            # print(f"\t\t{day_open}")
            if day_index[date] in day_open :
                htmp = htmp.split("-")
                htmpS = htmp[0].split(":")
                htmpE = htmp[1].split(":")
                #print(f"\t\t{htmpS[0]} : {htmpS[1]}")
                if time(int(htmpS[0]),int(htmpS[1])) <= time(int(hours[0]),int(hours[1])) <= time(int(htmpE[0]),int(htmpE[1])):
                    res_hours.append(r)
    
    for i in res_hours :
        print(i)


    