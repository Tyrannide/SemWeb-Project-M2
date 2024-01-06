# pip install sparqlwrapper
# pip install geopy
import SPARQLWrapper as spq
from geopy import Nominatim
from geopy.distance import geodesic

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
    max_range = 5 # km

    adress = None
    while not adress :
        # test : "50 rue Conte Grandchamp, 42000 Saint-Étienne"
        adress = convert_co(input("Please enter your adresse : "))
    
    price = input("Please enter your max price : ")
    # format à voir
    date = input("Please enter the date on the delivery (dd/mm/yyyy) : ")
    time = input("Please enter a time (hh:mm)")

    # doc : https://sparqlwrapper.readthedocs.io/en/latest/main.html#command-line-script
    sparq = spq.SPARQLWrapper("chemin du fichier") # /!\

    # à compléter 
    sparq.setQuery(f"""
        SELECT *
        WHERE {{
            [...]
        }}
    """)

    sparq.setReturnFormat(spq.JSON)
    res = sparq.query().convert()

    # voir à quoi le retour ressemble pour la boucle de tri (distance)
    print(res)
    
    exit()
    results = []
    for i in res :
        if geodesic(adress, i["coordonates"]).kilometers <= max_range :
            results.append(i)
    
    print(i)

    