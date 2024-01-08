import os
import json
import requests
from rdflib import Graph, URIRef, Literal, BNode
from rdflib.namespace import RDF, XSD, RDFS
import pyshacl
from urllib.parse import urlsplit

def findfile(name, path):
    print("file not found in direct directory, looking in the near respository\n")
    for dirpath, dirname, filename in os.walk(path):
        if name in filename:
            print(f"File found : {os.path.join(dirpath, name)}")
            return os.path.join(dirpath, name)
        


# ProfessionalService
def parseProfessionalServiceJson(d, g):
    sh = "https://schema.org/"
    ex = "http://www.example.com/"
    d['name'] = d['name'].replace(" ", "-")
    g_to_be_checked = Graph()
    added = 0


    subject_uri = URIRef(ex + d['name'])

    # Checking for duplicate
    if  (subject_uri, None, None) not in g:
        g_to_be_checked.add((URIRef(ex+d['name']), RDF.type, URIRef(sh+"ProfessionalService")))
        g_to_be_checked.add((URIRef(ex+d['name']), URIRef(sh+"legalName"), Literal(d['name'])))
        if 'coopcycle_url' in d:
            # Create a blank node for the membership information
            membership_node = BNode()
            g_to_be_checked.add((URIRef(ex + d['name']), URIRef(sh + "memberOf"), membership_node))
            g_to_be_checked.add((membership_node, RDF.type, URIRef(sh + "Organization")))
            g_to_be_checked.add((membership_node, URIRef(sh + "name"), Literal("coopcycle")))
            g_to_be_checked.add((membership_node, URIRef(sh + "url"), Literal(d['coopcycle_url'])))
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
            
        if len(g_to_be_checked) != 0:
            #print(g_to_be_checked.serialize())
            shapes_graph = Graph()
            shapes_graph.parse("shacl_template/coopcycle_shape.ttl", format="turtle")

            conforms, _, _ = pyshacl.validate(g_to_be_checked, shacl_graph=shapes_graph, inference="rdfs", serialize_report_graph="turtle")
            if not conforms:
                print(f"Data for {subject_uri} does not conform to the SHACL model. Skipping...")

            else:
                added += 1
                g += g_to_be_checked
    return added

def parseRestaurantData(d, g):

    print("Start of parsing restaurant")

    added = 0
    g_to_be_checked = Graph()
    sh = "https://schema.org/"
    ex = "http://www.example.com/"

    if 'specialOpeningHoursSpecification' in d:
        d.pop('specialOpeningHoursSpecification')

    # Pre-set up
    g_to_be_checked.add((URIRef(ex+d['name']), RDF.type, URIRef(sh+"Restaurant")))
    g_to_be_checked.add((URIRef(ex+d['name']), RDFS.label, Literal(d['description'])))
    # Process the address
    address_node = BNode()
    g_to_be_checked.add((URIRef(ex+d['name']), URIRef(sh+"address"), address_node))
    g_to_be_checked.add((address_node, RDF.type, URIRef(sh+"Place")))
    g_to_be_checked.add((address_node, URIRef(sh+"latitude"), Literal(d['address']['geo']['latitude'], datatype=XSD.decimal)))
    g_to_be_checked.add((address_node, URIRef(sh+"longitude"), Literal(d['address']['geo']['longitude'], datatype=XSD.decimal)))
    g_to_be_checked.add((address_node, URIRef(sh+"address"), Literal(d['address']['streetAddress'])))
    if 'tags' in d:     
        g_to_be_checked.add((URIRef(ex+d['name']), URIRef(sh+"servesCuisine"), Literal(', '.join(d['tags']))))

    if 'fulfillmentMethods' in d:
        for el in d['fulfillmentMethods']:
            if el['type'] == 'delivery':
                g_to_be_checked.add((URIRef(ex+d['name']), URIRef(sh+"openingHours"), Literal(', '.join(el['openingHours']))))

    if 'hasMenu' in d:
        if 'potentialAction' in d:
            print("Trying to read Menu")
            urlOfMenu = "{0.scheme}://{0.netloc}".format(urlsplit(d['potentialAction']['target']['urlTemplate'])) + d['hasMenu']
            response = requests.get(urlOfMenu)
            data = json.loads(response.text)
            menu_node = BNode()
            g_to_be_checked.add((URIRef(ex+d['name']), URIRef(sh+'hasMenu'), menu_node))
            print(data)
            for item in data['hasMenuSection']:
                for food in item['hasMenuItem']:
                    added += parseMenu(food, g_to_be_checked, menu_node)


    if len(g_to_be_checked) != 0:
            print(g_to_be_checked.serialize())
            shapes_graph = Graph()
            shapes_graph.parse("shacl_template/restaurant_shape.ttl", format="turtle")

            conforms, _, _ = pyshacl.validate(g_to_be_checked, shacl_graph=shapes_graph, inference="rdfs", serialize_report_graph="turtle")
            if not conforms:
                print(f"Data for {added} does not conform to the SHACL model. Skipping...")

            else:
                added += 1
                g += g_to_be_checked

    #if  (subject_uri, None, None) not in g:

    return added




def parseMenu(d,g,n):

    sh = "https://schema.org/"
    ex = "http://www.example.com/"


    item_node = BNode()
    g.add((n, URIRef(sh+'hasMenuItem'), item_node))
    g.add((item_node, RDF.type, URIRef(sh+'MenuItem')))
    g.add((item_node, URIRef(sh+'name'), Literal(d['name'])))
    g.add((item_node, URIRef(sh+'description'), Literal(d['description'])))
    offer_node = BNode()
    g.add((item_node, URIRef(sh+'offers'), offer_node))
    g.add((offer_node, RDF.type, URIRef(sh+'offers')))
    g.add((offer_node,URIRef(sh+'price'),Literal(float(d['offers']['price'])/100., datatype=XSD.decimal)))


    return 1



if __name__ == "__main__":

    directory = os.listdir()
    g = Graph()
    run = True

    print("Looking for existing data\n")
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