# pip install sparqlwrapper
# pip install geopy
import SPARQLWrapper as spq
from datetime import datetime, time
from geopy import Nominatim
from geopy.distance import geodesic
import sys
import os
from rdflib import Graph, URIRef
import random
import string
import shutil
import requests


def affiche_restau(l):

    for r in l:
        print("|\tRestaurant : ", r['restaurant']['value'].split('/')[-1])
        print("|\t\t| Opening hours : ", r['hours']['value'])
        print("|\t\t| Delivery price : ", r['deliveryPrice']['value'])
        print("|\t\t| Minimal cost for delivery : ", r['deliveryMinimalCost']['value'])
        if 'food' in r:
            if r['food']['value'] != "":
                print("|\t\t| Type of food served : ", r['food']['value'])



def generate_random_string(length):
    letters_and_digits = string.ascii_letters + string.digits
    return ''.join(random.choice(letters_and_digits) for _ in range(length))

def usage():
    print("Wrong parameters for the program query:\nYou should call it like:\n\tpython query.py --ranked-by (distance|price) [--schema-pref] [file]")

def convert_co(adress):
    convert = Nominatim(user_agent=generate_random_string(15))
    co = convert.geocode(adress)

    if co:
        lat, long = co.latitude, co.longitude
        return lat, long
    else:
        print("Adress not found.")
        return None

if __name__ == "__main__":

    #print(len(sys.argv))
    urlWorked = False
    adressPart1 = None
    adressPart2 = None
    longitude = 0
    latitude = 0
    sortingMethod = ""
    fileFound = False
    file = ""
    sh = "http://schema.org/"

    if len(sys.argv) >= 3:
        #print("Requête simple trier soit par prix, soit par distance")
        if ('--ranked-by' in sys.argv) and ('distance' in sys.argv):
            #print("Filtre par distance")
            sortingMethod = "distance"
            if '--schema-pref' in sys.argv:
                for param in sys.argv[3:]:
                    if param[-4:] == ".ttl" and os.path.isfile(param):
                        fileFound = True
                        file = param
                    elif param[0:4] == "http":
                        headers = {
                            "Accept": "text/turtle"
                        }
                        url = "http://193.49.165.77:3000/semweb/BONNEFOY-MARINE-data"
                        try:
                            response = requests.get(url, headers=headers)
                            if response.status_code == 200:
                                print("Request successful.")
                                urlWorked = True
                            else:
                                print(f"Request failed with status code: {response.status_code}")
                                print(response.text)

                        except requests.RequestException as e:
                            print(f"Request failed: {e}")
                else:
                    if fileFound:
                        print("A preference file was found")
                    else:
                        print("No preference file found, going classical process")
            else:
                print("Classical running")
        elif ('--ranked-by' in sys.argv) and ('price' in sys.argv):
            #print("Filtre par prix")
            sortingMethod = "price"
            if '--schema-pref' in sys.argv:
                for param in sys.argv[3:]:
                    if param[-4:] == ".ttl" and os.path.isfile(param):
                        fileFound = True
                        file = param
                else:
                    if fileFound:
                        print("A preference file was found")
                    else:
                        print("No preference file found, classical process running")
            else:
                print("Classical running")
        else:
            usage()
            exit()
    else:
        usage()
        exit()

    #print('Argument List:', str(sys.argv))
        
    day_index = {"Mo" : 1,"Tu": 2, "We": 3, "Th": 4, "Fr": 5, "Sa": 6, "Su": 7}
        
    if not fileFound:


        max_range = int(input("Can you give the maximum range for the restaurant, format (km)\n>>>"))
        

        max_price = float(input("Can you give the maximum price you must spent for a delivery\n>>>"))
        date = input("Can you give the hour expected for the delivery, format (dd-mm-aaaa)\n>>>")
        date = datetime.strptime(date, "%d-%m-%Y")
        date = str(date.strftime("%A"))[:2]
        hours = input("Can you give the hour expected for the delivery, format (hh:mm)\n>>>")
        hours = hours.split(":")
        # test : "50 rue Conte Grandchamp, 42000 Saint-Étienne"
        address = input("Can you give your address?\n>>>")
        adress = convert_co(address)

    elif urlWorked:
        g = Graph()
        g.parse(response.text, format='turtle')

        for sub, pred, obj in g.triples((None, None, None)):
                if pred == URIRef(sh+'streetAddress'):
                    adressPart1 = str(obj[:])
                if pred == URIRef(sh+'addressLocality'):
                    adressPart3 = str(obj[:])
                if pred == URIRef(sh+'postalCode'):
                    adressPart2 = str(obj[:])
                if pred == URIRef(sh+'itemOfferred'):
                    items = obj[:]
                if pred == URIRef(sh+'maxPrice'):
                    max_price = float(obj[:])
                if pred == URIRef(sh+'geoRadius'):
                    max_range = float(obj[:])/1000
                if pred == URIRef(sh+'longitude'):
                    longitude = float(obj[:])
                if pred == URIRef(sh+'latitude'):
                    latitude = float(obj[:])
        else:
                if adressPart1 is not None and adressPart2 is not None and adressPart3 is not None:
                    address = adressPart1 + ", " + adressPart2 + " " + adressPart3
                    adress = convert_co(address)
                elif adressPart1 is not None and adressPart2 is not None:
                    address = adressPart1 + ", " + adressPart2
                else:
                    adress = (longitude, latitude)

    else:
        print("Lecture préférence")
        if os.path.exists(file):
            g = Graph()
            g.parse(file, format='turtle')
            #print(g.serialize())

            for sub, pred, obj in g.triples((None, None, None)):
                if pred == URIRef(sh+'streetAddress'):
                    adressPart1 = str(obj[:])
                if pred == URIRef(sh+'addressLocality'):
                    adressPart3 = str(obj[:])
                if pred == URIRef(sh+'postalCode'):
                    adressPart2 = str(obj[:])
                if pred == URIRef(sh+'itemOfferred'):
                    items = obj[:]
                if pred == URIRef(sh+'maxPrice'):
                    max_price = float(obj[:])
                if pred == URIRef(sh+'geoRadius'):
                    max_range = float(obj[:])/1000
                if pred == URIRef(sh+'longitude'):
                    longitude = float(obj[:])
                if pred == URIRef(sh+'latitude'):
                    latitude = float(obj[:])
            else:
                if adressPart1 is not None and adressPart2 is not None and adressPart3 is not None:
                    address = adressPart1 + ", " + adressPart2 + " " + adressPart3
                    adress = convert_co(address)
                elif adressPart1 is not None and adressPart2 is not None:
                    address = adressPart1 + ", " + adressPart2
                else:
                    adress = (longitude, latitude)
        else:
            print("The file given wasn't found, or couldn't be opened, exiting...")
            exit()
        date = input("Can you give the hour expected for the delivery, format (dd-mm-aaaa)\n>>>")
        date = datetime.strptime(date, "%d-%m-%Y")
        date = str(date.strftime("%A"))[:2]
        hours = input("Can you give the hour expected for the delivery, format (hh:mm)\n>>>")
        hours = hours.split(":")



    if adress is not None:

        
        # doc : https://sparqlwrapper.readthedocs.io/en/latest/main.html#command-line-script
        sparq = spq.SPARQLWrapper("http://localhost:8000")


        sparq.setQuery(f"""
            PREFIX sh1: <http://schema.org/>
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

            SELECT DISTINCT ?restaurant ?longitude ?latitude ?deliveryPrice ?deliveryMinimalCost ?hours ?food
            WHERE {{
                ?restaurant a sh1:Restaurant ;
                sh1:address ?add;
                sh1:openingHours ?hours;
                sh1:servesCuisine ?food;
                sh1:potentialAction ?pa.

                ?add a sh1:Place ;
                sh1:latitude ?latitude ;
                sh1:longitude ?longitude .

                ?pa sh1:PriceSpecification ?ps.

                ?ps sh1:price ?deliveryPrice.

                ?ps sh1:eligibleTransactionVolume ?etv.

                ?etv sh1:price ?deliveryMinimalCost .

            }}
            LIMIT 1000
            OFFSET 0
            """)

        sparq.setReturnFormat(spq.JSON)
        res = sparq.query().convert()

        # res_hours -> all restaurant mathcing the hour condition

        res_hours = []
        for r in res["results"]["bindings"] :
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

                        
        # res_distance -> all restaurant matching distance constraint
                        

        res_distance = [r for r in res["results"]["bindings"] if geodesic(adress, (float(r["latitude"]["value"]),float(r["longitude"]["value"]))).kilometers <= max_range]
        
        # res_price -> all restaurant matching price constraint

        res_price = [r for r in res["results"]["bindings"] if float(r["deliveryMinimalCost"]["value"]) <= max_price]

        # convertir en set pour débloquer le pouvoir du .intersection


        hoursSet = {r['restaurant']['value'] for r in res_hours}
        distanceSet = {r['restaurant']['value'] for r in res_distance}
        priceSet = {r['restaurant']['value'] for r in res_price}

        distance_hourSet = hoursSet.intersection(distanceSet)
        price_hourSet = hoursSet.intersection(priceSet)
        allSet = hoursSet.intersection(distanceSet, priceSet)

        price_hourSet = price_hourSet.difference(allSet)
        distance_hourSet = distance_hourSet.difference(allSet)

        res_priceHour = [r for r in res_hours if r["restaurant"]["value"] in price_hourSet]
        res_distHour = [r for r in res_hours if r["restaurant"]["value"] in distance_hourSet]
        res_all = [r for r in res_hours if r["restaurant"]["value"] in allSet]

        if sortingMethod == "distance":
            res_all.sort(key = lambda r: geodesic(adress, (float(r["latitude"]["value"]), float(r["longitude"]["value"]))).kilometers)
            res_distHour.sort(key = lambda r: geodesic(adress, (float(r["latitude"]["value"]), float(r["longitude"]["value"]))).kilometers)
            res_priceHour.sort(key = lambda r: geodesic(adress, (float(r["latitude"]["value"]), float(r["longitude"]["value"]))).kilometers)
        else:
            res_all.sort(key = lambda r: float(r["deliveryMinimalCost"]["value"]))
            res_distHour.sort(key = lambda r: float(r["deliveryMinimalCost"]["value"]))
            res_priceHour.sort(key = lambda r: float(r["deliveryMinimalCost"]["value"]))


        terminal_width, _ = shutil.get_terminal_size()
        print("#" * terminal_width)
        print("All restaurant meeting all requirements :")
        affiche_restau(res_all)
        print("#" * terminal_width)
        print("Restaurants meeting both price and hours :")
        affiche_restau(res_priceHour)
        print("#" * terminal_width)
        print("Restaurant meeting both distance and hours :")
        affiche_restau(res_distHour)
        print("#" * terminal_width)


        if input("Do you want to export the result in a file? [ it has better visibility ](y/n)") in ["y", "Y", "yes", "YES", "Yes", "o", "oui", "Oui", "OUI"]:
            with open('log_file.txt', 'w', encoding='utf-8') as f:
                f.write("#" * terminal_width+ "\n")
                f.write("All restaurant meeting all requirements :\n")
                for r in res_all:
                    f.write("|\tRestaurant : " + r['restaurant']['value'].split('/')[-1] + "\n")
                    f.write("|\t\t| Opening hours : " + r['hours']['value'] + "\n")
                    f.write("|\t\t| Delivery price : " + r['deliveryPrice']['value'] + "\n")
                    f.write("|\t\t| Minimal cost for delivery : " + r['deliveryMinimalCost']['value'] + "\n")
                    if 'food' in r:
                        if r['food']['value'] != "":
                           f.write("|\t\t| Type of food served : " + r['food']['value'] + "\n")
                f.write("#" * terminal_width + "\n")
                f.write("Restaurants meeting both price and hours :\n")
                for r in res_priceHour:
                    f.write("|\tRestaurant : " + r['restaurant']['value'].split('/')[-1] + "\n")
                    f.write("|\t\t| Opening hours : " + r['hours']['value'] + "\n")
                    f.write("|\t\t| Delivery price : " + r['deliveryPrice']['value'] + "\n")
                    f.write("|\t\t| Minimal cost for delivery : " + r['deliveryMinimalCost']['value'] + "\n")
                    if 'food' in r:
                        if r['food']['value'] != "":
                           f.write("|\t\t| Type of food served : " + r['food']['value'] + "\n")
                f.write("#" * terminal_width + "\n")
                f.write("Restaurant meeting both distance and hours :\n")
                for r in res_distHour:
                    f.write("|\tRestaurant : " + r['restaurant']['value'].split('/')[-1] + "\n")
                    f.write("|\t\t| Opening hours : " + r['hours']['value'] + "\n")
                    f.write("|\t\t| Delivery price : " + r['deliveryPrice']['value'] + "\n")
                    f.write("|\t\t| Minimal cost for delivery : " + r['deliveryMinimalCost']['value'] + "\n")
                    if 'food' in r:
                        if r['food']['value'] != "":
                           f.write("|\t\t| Type of food served : " + r['food']['value'] + "\n")
            print("Export done!")
        
    else:
        exit(-1)


