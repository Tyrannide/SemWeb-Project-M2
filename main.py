import os
import json
import requests
from rdflib import Graph, URIRef, Literal
from rdflib.namespace import RDF, XSD, RDFS
from collect import parseProfessionalServiceJson, findfile, parseRestaurantData, parseMenu
from restaurant_checker import check_through_restaurants
from server_data.server import init_serv
import uvicorn


# ProfessionalService

if __name__ == "__main__":



    print("let's start")

    directory = os.listdir()
    g = Graph()
    app = None
    add = 0

    print("Looking for existing data\n")
    if os.path.exists("server_data/data_semweb.db"):
        g.load("server_data/data_semweb.db")
        print("Existing data loaded : \n")
        #print(g.serialize())
    else:
        print("No existing data found\n")

    sh = "https://schema.org/"
    ex = "http://www.example.com/"

    # Setting up variable
    g.bind("sh", sh)
    g.bind("ex", ex)

    process_mode = input("Do you want to query online sources (1) or personal data file (2)?\n>>>")
    # Default data file
    if process_mode not in ["1","2"]: process_mode = "2"

    if process_mode == "1":
        url = input("Please enter the URL you want :\nPlease be sure to use a URL with a JSON format\naccording to the format seen in the course\n>>>")
        if url[0:4] != "http":
            print("Wrong url Format, going with default\nhttps://coopcycle.org/coopcycle.json?_=1700830898800\n")
            url = "https://coopcycle.org/coopcycle.json?_=1700830898800"
        response = requests.get(url)
        data = json.loads(response.text)
        if 'coopcycle_url' in data:
            print("Identified data as coopcycle information\n")
            for city in data:
                add += parseProfessionalServiceJson(city, g)
            else:
                print(f"We added {add} element from coopcycle partnership")
        else:
            print("Considering data as restaurant data\n")
            if '@context' in data:
                if data['@context'] == '/api/contexts/Menu':
                    add += parseMenu(data, g)
                elif data['@context'] == '/api/contexts/Restaurant':
                    add += parseRestaurantData(data, g)
                else:
                    print("Unknown context, can't process the data")
            else :
                print("No context found in web response, data isn't considered as processable")

    else:   
        file_name = input("Please enter the name of the file:\n>>>")
        if file_name == "":
            print("Wrong file name, going with default\ndata.json\n")
            file_name = "data.json" 
        if file_name in directory:
            file_path = file_name
        else:
            file_path = findfile(file_name, "../../../")

        if file_path[-5:-1] == ".json":
            with open(file_path, 'r', encoding="UTF-8") as f:
                data = json.load(f)
                for city in data:
                    parseProfessionalServiceJson(city, g)

            r = input("Do you want to save the current data parsed ? (y/n)")

            if r in ["y", "Y", "yes", "YES", "Yes", "o", "oui", "Oui", "OUI"]:
                g.serialize(destination=".server_data/data_semweb.db", format="turtle")
        else :
            print("Given file wasn't from an expected format, please use JSON files\n")

    #print(g.serialize())

    #check_through_restaurants(g)

    
    if len(g) != 0:
        rep = input("Do you want to run the TripleStore ? (y/n)")

        if rep in ["y", "Y", "yes", "YES", "Yes", "o", "oui", "Oui", "OUI"]:
            app = init_serv(app=app, g=g)
            uvicorn.run(app, host="localhost", port=8000)

    else:
        print("No data available, quitting program...\n")