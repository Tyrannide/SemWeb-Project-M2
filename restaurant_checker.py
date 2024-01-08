import os
import json
import requests
from rdflib import Graph, URIRef, Literal, BNode
from rdflib.namespace import RDF, XSD, RDFS
from rdflib.plugins.sparql import prepareQuery
import pyshacl
from urllib.parse import urlsplit
from bs4 import BeautifulSoup

def parseRestaurantData(d, g):

    

    added = 0
    g_to_be_checked = Graph()
    sh = "https://schema.org/"
    ex = "http://www.example.com/"

    if 'specialOpeningHoursSpecification' in d:
        d.pop('specialOpeningHoursSpecification')

    d['name'] = d['name'].replace(" ", "-")
    d['name'] = d['name'].replace('"', "")
    d['name'] = d['name'].replace('|', "")

    print(f"Start of parsing restaurant : {d['name']}")
    subject_uri = URIRef(ex + d['name'])
    # Pre-set up
    if  (subject_uri, None, None) not in g:
        g_to_be_checked.add((URIRef(ex+d['name']), RDF.type, URIRef(sh+"Restaurant")))
        g_to_be_checked.add((URIRef(ex+d['name']), RDFS.label, Literal(d['description'])))
        g_to_be_checked.add((URIRef(ex+d['name']), URIRef(sh+"nextOpeningDate"), Literal(d['nextOpeningDate'])))
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

        sorting = list(g.triples((None, URIRef(sh+ "legalName"), None)))
        for s in sorting:
            first_level = list(g.triples((s[0], URIRef(sh+ "memberOf"), None)))
            #print("debugging", first_level)
            if len(first_level) > 0:
                for el in first_level:
                    final_level = list(g.triples((el[2], URIRef(sh+ "url"), None)))
                    for e in final_level:
                        check = "{0.scheme}://{0.netloc}".format(urlsplit(d['potentialAction']['target']['urlTemplate']))
                        #print(e[2], "/", check)
                        if check == str(e[2]):
                            membership_node = BNode()
                            g_to_be_checked.add((URIRef(ex + d['name']), URIRef(sh + "memberOf"), membership_node))
                            g_to_be_checked.add((membership_node, RDF.type, URIRef(sh + "ProfessionalService")))
                            #print(el)
                            g_to_be_checked.add((membership_node, URIRef(sh + "name"), Literal(str(list(g.triples((el[0], URIRef(sh+"legalName"), None)))[0][2]))))
                            g_to_be_checked.add((membership_node, URIRef(sh + "url"), Literal(str(e[2]), datatype=XSD.anyURI)))
                    
    else:

        #print(g_to_be_checked.serialize())
        print("Data already existing : Updating the old value")
        g.remove((subject_uri, None, None))
        g_to_be_checked.add((URIRef(ex+d['name']), RDF.type, URIRef(sh+"Restaurant")))
        g_to_be_checked.add((URIRef(ex+d['name']), RDFS.label, Literal(d['description'])))
        g_to_be_checked.add((URIRef(ex+d['name']), URIRef(sh+"nextOpeningDate"), Literal(d['nextOpeningDate'])))
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

        sorting = list(g.triples((None, URIRef(sh+ "legalName"), None)))
        for s in sorting:
            first_level = list(g.triples((s[0], URIRef(sh+ "memberOf"), None)))
            #print("debugging", first_level)
            if len(first_level) > 0:
                for el in first_level:
                    final_level = list(g.triples((el[2], URIRef(sh+ "url"), None)))
                    for e in final_level:
                        check = "{0.scheme}://{0.netloc}".format(urlsplit(d['potentialAction']['target']['urlTemplate']))
                        #print(e[2], "/", check)
                        if check == str(e[2]):
                            membership_node = BNode()
                            g_to_be_checked.add((URIRef(ex + d['name']), URIRef(sh + "memberOf"), membership_node))
                            g_to_be_checked.add((membership_node, RDF.type, URIRef(sh + "ProfessionalService")))
                            #print(el)
                            g_to_be_checked.add((membership_node, URIRef(sh + "name"), Literal(str(list(g.triples((el[0], URIRef(sh+"legalName"), None)))[0][2]))))
                            g_to_be_checked.add((membership_node, URIRef(sh + "url"), Literal(str(e[2]), datatype=XSD.anyURI)))

    if len(g_to_be_checked) != 0:
            #print(g_to_be_checked.serialize())
            shapes_graph = Graph()
            shapes_graph.parse("shacl_template/restaurant_shape.ttl", format="turtle")

            conforms, _, _ = pyshacl.validate(g_to_be_checked, shacl_graph=shapes_graph, inference="rdfs", serialize_report_graph="turtle")
            if not conforms:
                print(f"Data for {d['name']} does not conform to the SHACL model. Skipping...")

            else:
                added += 1
                
                list_site = check_through_restaurants(d)

                for site in list_site:
                    pc, p , etvpc , etvp = scrap(site)
                    if pc and p and etvpc and etvp:
                        potentAct = BNode()
                        priceSpec = BNode()
                        price_node = BNode()
                        g_to_be_checked.add((URIRef(ex+d['name']), URIRef(sh+"potentialAction"), potentAct))
                        g_to_be_checked.add((potentAct, RDF.type, URIRef(sh+"priceSpecification")))
                        g_to_be_checked.add((potentAct, URIRef(sh+"priceSpecification"), priceSpec))
                        g_to_be_checked.add((priceSpec, RDF.type, URIRef(sh+"priceSpecification")))
                        g_to_be_checked.add((priceSpec, URIRef(sh+"priceCurrency"), Literal(pc)))
                        g_to_be_checked.add((priceSpec, URIRef(sh+"price"), Literal(p)))
                        g_to_be_checked.add((priceSpec, URIRef(sh+"eligibleTransactionVolume"), price_node))
                        g_to_be_checked.add((price_node, RDF.type, URIRef(sh+"eligibleTransactionVolume")))
                        g_to_be_checked.add((price_node, URIRef(sh+"priceCurrency"), Literal(etvpc)))
                        g_to_be_checked.add((price_node, URIRef(sh+"price"), Literal(etvp)))


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




def check_through_restaurants(d):
    valid = 0
    responses = []

    try:
        response = requests.get(d['potentialAction']['target']['urlTemplate'], timeout = 7)
        if response.ok:
            responses.append(response.text)
            valid +=1
        else:
            print(f"Error {response.status_code}: {response.reason}")
            
    except requests.exceptions.ReadTimeout:
        print(f"Site {d['potentialAction']['target']['urlTemplate']} was unresponsive (timed out after 7s)")
    except requests.exceptions.SSLError:
        print(f"Site {d['potentialAction']['target']['urlTemplate']} doesn't have a valid certificate, are you sure it is created and configured?")
    except requests.exceptions.ConnectionError:
        print(f"Site {d['potentialAction']['target']['urlTemplate']} doesn't exist")
    except requests.exceptions.TooManyRedirects:
        print(f"Site {d['potentialAction']['target']['urlTemplate']} had too many redirects, couldn't reach the endpoint")
    
    #print(f"{valid}/{total} of urls responded")

    return responses



def scrap(html_content):

    soup = BeautifulSoup(html_content, 'html.parser')

    script_tag = soup.find('script', {'type': 'application/ld+json'})

    price_specification = None

    if script_tag:
        json_ld_content = script_tag.string
        # Parse JSON-LD data
        try:
            data = json.loads(json_ld_content)

            price_currency = data.get("potentialAction", {}).get("priceSpecification", {}).get("priceCurrency")
            price = data.get("potentialAction", {}).get("priceSpecification", {}).get("price")
            eligible_transaction_volume = data.get("potentialAction", {}).get("priceSpecification", {}).get("eligibleTransactionVolume", {})


        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
    else:
        print("No script tag with type 'application/ld+json' found.")

    return price_currency, price, eligible_transaction_volume.get("priceCurrency"), eligible_transaction_volume.get("price")