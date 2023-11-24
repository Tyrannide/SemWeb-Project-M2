import os
import json
import requests
from rdflib import Graph, URIRef, Literal
from rdflib.namespace import RDF, XSD, RDFS

def findfile(name, path):
    for dirpath, dirname, filename in os.walk(path):
        if name in filename:
            return os.path.join(dirpath, name)
        
def parseProfessionalServiceJson(d, g):
    sh = "https://schema.org/"
    ex = "http://www.example.com/"
    d['name'] = d['name'].replace(" ", "-")
    g.add((URIRef(ex+d['name']), RDF.type, URIRef(sh+"ProfessionalService")))
    g.add((URIRef(ex+d['name']), URIRef(sh+"legalName"), Literal(d['name'])))
    if 'latitude' in d:
        g.add((URIRef(ex+d['name']), URIRef(sh+"latitude"), Literal(d['latitude'], datatype=XSD.decimal)))
    if 'longitude' in d:
        g.add((URIRef(ex+d['name']), URIRef(sh+"longitude"), Literal(d['longitude'], datatype=XSD.decimal)))
    if 'url' in d:
        g.add((URIRef(ex+d['name']), URIRef(sh+"url"),  Literal(d['url'])))
        #TODO Fouille et collecte des données des sites pour avoir les restaurants
    if 'mail' in d:
        g.add((URIRef(ex+d['name']), URIRef(sh+"email"), Literal(d['mail'])))
        g.add((URIRef(ex+d['name']), URIRef(sh+"contactPoint"), Literal(d['mail'])))
    if 'city' in d:
        g.add((URIRef(ex+d['name']), URIRef(sh+"location"), Literal(d['city'])))
        g.add((URIRef(ex+d['name']), URIRef(sh+"areaServed"), Literal(d['city'])))
    if 'country' in d:
        g.add((URIRef(ex+d['name']), URIRef(sh+"knowsLanguage"), Literal(d['country'])))
        g.add((URIRef(ex+d['name']), URIRef(sh+"containedInPlace"), Literal(d['country'])))
    if 'facebook_url' in d:
        g.add((URIRef(ex+d['name']), URIRef(sh+"contactPoint"), Literal(d['facebook_url'])))
    if 'twitter_url' in d:
        g.add((URIRef(ex+d['name']), URIRef(sh+"contactPoint"), Literal(d['twitter_url'])))
    if 'text' in d:
        for k, v in d['text'].items():
            g.add((URIRef(ex+d['name']), RDFS.label, Literal(v, lang=k)))
    #g.add(())
            



# ProfessionalService

if __name__ == "__main__":
    print("let's start")

    directory = os.listdir()
    g = Graph()

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
        if url[1:4] != "http":
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