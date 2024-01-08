import os
import json
import requests
from rdflib import Graph, URIRef, Literal, BNode
from rdflib.namespace import RDF, XSD, RDFS
import pyshacl
from urllib.parse import urlsplit

def parseRestaurantData(d, g):

    

    added = 0
    g_to_be_checked = Graph()
    sh = "https://schema.org/"
    ex = "http://www.example.com/"

    if 'specialOpeningHoursSpecification' in d:
        d.pop('specialOpeningHoursSpecification')

    d['name'] = d['name'].replace(" ", "-")
    d['name'] = d['name'].replace('"', "")

    print(f"Start of parsing restaurant : {d['name']}")

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
            if 'hasMenuSection' in data:
                for item in data['hasMenuSection']:
                    for food in item['hasMenuItem']:
                        added += parseMenu(food, g_to_be_checked, menu_node)
            else:
                print(f"No menu found for {d['name']}")
                

    if len(g_to_be_checked) != 0:
            #print(g_to_be_checked.serialize())
            shapes_graph = Graph()
            shapes_graph.parse("shacl_template/restaurant_shape.ttl", format="turtle")

            conforms, _, _ = pyshacl.validate(g_to_be_checked, shacl_graph=shapes_graph, inference="rdfs", serialize_report_graph="turtle")
            if not conforms:
                print(f"Data for {d['name']} does not conform to the SHACL model. Skipping...")

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
