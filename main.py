import os
import json
import requests
from rdflib import Graph, URIRef, Literal
from rdflib.namespace import RDF, XSD, RDFS
from parse import parseProfessionalServiceJson, findfile
from restaurant_checker import check_through_restaurants
from server import init_serv
import uvicorn


# ProfessionalService

if __name__ == "__main__":
    print("let's start")

    directory = os.listdir()
    g = Graph()
    app = None

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
        if url[0:3] != "http":
            print("Wrong url Format, going with default\nhttps://coopcycle.org/coopcycle.json?_=1700830898800\n")
            url = "https://coopcycle.org/coopcycle.json?_=1700830898800"
        response = requests.get(url)
        data = json.loads(response.text)
        for city in data:
            parseProfessionalServiceJson(city, g)
    else:   
        file_name = input("Please enter the name of the file:\n>>>")
        if file_name == "":
            print("Wrong file name, going with default\ndata.json\n")
            file_name = "data.json" 
        if file_name in directory:
            file_path = file_name
        else:
            file_path = findfile(file_name, "/")

        with open(file_path, 'r', encoding="UTF-8") as f:
            data = json.load(f)
            for city in data:
                parseProfessionalServiceJson(city, g)

    print(g.serialize())

    #check_through_restaurants(g)


    app = init_serv(app=app, g=g)
    uvicorn.run(app, host="0.0.0.0", port=8000)