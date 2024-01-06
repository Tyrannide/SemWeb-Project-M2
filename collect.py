import os
import json
import requests
from rdflib import Graph, URIRef, Literal
from rdflib.namespace import RDF, XSD, RDFS
import pyshacl

def findfile(name, path):
    for dirpath, dirname, filename in os.walk(path):
        if name in filename:
            return os.path.join(dirpath, name)
        
def parseProfessionalServiceJson(d, g):
    sh = "https://schema.org/"
    ex = "http://www.example.com/"
    d['name'] = d['name'].replace(" ", "-")
    g_to_be_checked = Graph()


    subject_uri = URIRef(ex + d['name'])

    # Checking for duplicate
    if  (subject_uri, None, None) not in g:
        g_to_be_checked.add((URIRef(ex+d['name']), RDF.type, URIRef(sh+"ProfessionalService")))
        g_to_be_checked.add((URIRef(ex+d['name']), URIRef(sh+"legalName"), Literal(d['name'])))
        if 'latitude' in d:
            g_to_be_checked.add((URIRef(ex+d['name']), URIRef(sh+"latitude"), Literal(d['latitude'], datatype=XSD.decimal)))
        if 'longitude' in d:
            g_to_be_checked.add((URIRef(ex+d['name']), URIRef(sh+"longitude"), Literal(d['longitude'], datatype=XSD.decimal)))
        if 'url' in d:
            g_to_be_checked.add((URIRef(ex+d['name']), URIRef(sh+"url"),  Literal(d['url'])))
            #TODO Fouille et collecte des données des sites pour avoir les restaurants
        if 'mail' in d:
            g_to_be_checked.add((URIRef(ex+d['name']), URIRef(sh+"email"), Literal(d['mail'])))
            g_to_be_checked.add((URIRef(ex+d['name']), URIRef(sh+"contactPoint"), Literal(d['mail'])))
        if 'city' in d:
            g_to_be_checked.add((URIRef(ex+d['name']), URIRef(sh+"location"), Literal(d['city'])))
            g_to_be_checked.add((URIRef(ex+d['name']), URIRef(sh+"areaServed"), Literal(d['city'])))
        if 'country' in d:
            g_to_be_checked.add((URIRef(ex+d['name']), URIRef(sh+"knowsLanguage"), Literal(d['country'])))
            g_to_be_checked.add((URIRef(ex+d['name']), URIRef(sh+"containedInPlace"), Literal(d['country'])))
        if 'facebook_url' in d:
            g_to_be_checked.add((URIRef(ex+d['name']), URIRef(sh+"contactPoint"), Literal(d['facebook_url'])))
        if 'twitter_url' in d:
            g_to_be_checked.add((URIRef(ex+d['name']), URIRef(sh+"contactPoint"), Literal(d['twitter_url'])))
        if 'text' in d:
            for k, v in d['text'].items():
                g_to_be_checked.add((URIRef(ex+d['name']), RDFS.label, Literal(v, lang=k)))
    #g.add(())
            
        shapes_graph = Graph()
        shapes_graph.parse("shecl_template/coopcycle_shape.ttl", format="turtle")

        conforms, _, _ = pyshacl.validate(g_to_be_checked, shacl_graph=shapes_graph, inference="rdfs", serialize_report_graph="format")
        if not conforms:
            print(f"Data for {subject_uri} does not conform to the SHACL model. Skipping...")

        else:
            g += g_to_be_checked

# ProfessionalService

if __name__ == "__main__":

    directory = os.listdir()
    g = Graph()
    run = True
    if os.path.exists("server_data/data_semweb.db"):
        g.load("server_data/data_semweb.db")
        print("Existing data loaded : \n")
        print(g.serialize())
    else:
        print("No data found\n")

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
            print("Wrong url Format, exiting program...\n")
            run = False
        else:
            response = requests.get(url)
            print(response.text)
            data = json.loads(response.text)
            for city in data:
                parseProfessionalServiceJson(city, g)
    else:   
        file_name = input("Please enter the name of the file:\n>>>")
        if file_name == "":
            print("Wrong file name, exiting program...\n")
            run = False
        else:
            if file_name in directory:
                file_path = file_name
            else:
                file_path = findfile(file_name, "/")

            with open(file_path, 'r', encoding="UTF-8") as f:
                data = json.load(f)
                for city in data:
                    parseProfessionalServiceJson(city, g)

    if run:
        print(g.serialize())

        r = input("Do you want to save the current data parsed ? (y/n)")

        if r in ["y", "Y", "yes", "YES", "Yes", "o", "oui", "Oui", "OUI"]:
            g.serialize(destination=".server_data/data_semweb.db", format="turtle")