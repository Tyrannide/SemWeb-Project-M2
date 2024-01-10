import os
import json
import requests
from rdflib import Graph, URIRef, Literal, BNode
from rdflib.namespace import RDF, XSD, RDFS
import pyshacl
from urllib.parse import urlsplit
from restaurant_checker import  parseRestaurantData, parseMenu

def findfile(name, path):
    print("file not found in direct directory, looking in the near respository\n")
    for dirpath, dirname, filename in os.walk(path):
        if name in filename:
            print(f"File found : {os.path.join(dirpath, name)}")
            return os.path.join(dirpath, name)
    else:
        return ""
        


# ProfessionalService
def parseProfessionalServiceJson(d, g):
    sh = "http://schema.org/"
    ex = "http://www.example.com/"
    d['name'] = d['name'].replace(" ", "-")
    d['name'] = d['name'].replace('"', "")
    d['name'] = d['name'].replace('|', "")
    g_to_be_checked = Graph()
    added = 0

    g_to_be_checked.bind("sh", sh)
    g_to_be_checked.bind("ex", ex)

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
            g_to_be_checked.add((membership_node, URIRef(sh + "url"), Literal(d['coopcycle_url'], datatype=XSD.anyURI)))
        if 'latitude' in d:
            g_to_be_checked.add((URIRef(ex+d['name']), URIRef(sh+"latitude"), Literal(str(d['latitude']), datatype=XSD.decimal)))
        if 'longitude' in d:
            g_to_be_checked.add((URIRef(ex+d['name']), URIRef(sh+"longitude"), Literal(str(d['longitude']), datatype=XSD.decimal)))
        if 'url' in d:
            g_to_be_checked.add((URIRef(ex+d['name']), URIRef(sh+"url"),  Literal(d['url'], datatype=XSD.anyURI)))
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

    else:
        print("Data already existing")


    #g.add(())
            
    if len(g_to_be_checked) != 0:
        #print(g_to_be_checked.serialize())
        shapes_graph = Graph()
        shapes_graph.parse("shacl_template/coopcycle_shape.ttl", format="turtle")

        conforms, _, result_text = pyshacl.validate(g_to_be_checked, shacl_graph=shapes_graph, inference="rdfs", serialize_report_graph="turtle")
        if not conforms:
            print(f"Data for {subject_uri} does not conform to the SHACL model. Skipping...")
            #print(result_text)

        else:
            added += 1
            g += g_to_be_checked

    return added


if __name__ == "__main__":

    directory = os.listdir()
    g = Graph()
    app = None
    add = 0
    added = []
    exist = False

    print("Looking for existing data\n")
    if os.path.exists("server_data/data_semweb.db"):
        g.parse("server_data/data_semweb.db", format='turtle')
        print("Existing data loaded : \n")
        exist = True
        #print(g.serialize())
    else:
        print("No existing data found\n")
        exist = False

    sh = "http://schema.org/"
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
        #print(data)
        if isinstance(data, list):
            to_check = data[0]
        else:
            to_check = data
        if 'coopcycle_url' in to_check:
            print("Identified data as coopcycle information\n")
            for city in data:
                if parseProfessionalServiceJson(city, g) > 0:
                    add += 1
                    added.append(city)
            else:
                print(f"We added {add} element from coopcycle partnership")

            process = input("Do you want to read the data of all partner registered ?(y/n)\n>>>")
            if process in ["y", "Y", "yes", "YES", "Yes", "o", "oui", "Oui", "OUI"]:
                for c in added:
                    urlGroupOfRestaurant = c['coopcycle_url'] + '/api/restaurants'
                    response = requests.get(urlGroupOfRestaurant)
                    data = json.loads(response.text)
                    if 'hydra:member' in data:
                        for item in data['hydra:member']:
                                urlOfRestaurant = "{0.scheme}://{0.netloc}".format(urlsplit(urlGroupOfRestaurant)) +  item['@id']
                                try:
                                    rResponse = requests.get(urlOfRestaurant)
                                    rResponse.raise_for_status()
                                    rData = json.loads(rResponse.text)
                                    add += parseRestaurantData(rData, g)
                                except requests.exceptions.HTTPError as errh:
                                    print ("HTTP Error:", errh)
                                except requests.exceptions.ConnectionError as errc:
                                    print ("Error Connecting:", errc)
                                    # Handle connection error

                                except requests.exceptions.Timeout as errt:
                                    print ("Timeout Error:", errt)
                                    # Handle timeout error

                                except requests.exceptions.RequestException as err:
                                    print ("Something went wrong:", err)
                                
                    else:
                        print(f"No Restaurants found for {c['name']}, request sent :\n{response.text}")

        else:
            print("Considering data as restaurant data\n")
            if '@context' in data:
                if data['@context'] == '/api/contexts/Menu':
                    restau = input("Menu context found, from what Restaurant does the menu comes ?\n>>>")
                    subject_uri = URIRef(ex + restau)
                    if  (subject_uri, None, None) not in g:
                        print(f"Restaurant {restau} was not found, cannot add the menu data to inexistant element")
                    else:
                        menu_node = BNode()
                        g.add((subject_uri, URIRef(sh+'hasMenu'), menu_node))
                        add += parseMenu(data, g, menu_node)
                elif data['@context'] == '/api/contexts/Restaurant':
                    #print(data)
                    if 'hydra:member' in data:
                        for item in data['hydra:member']:
                            urlOfRestaurant = "{0.scheme}://{0.netloc}".format(urlsplit(url)) + item['@id']
                            rResponse = requests.get(urlOfRestaurant)
                            rData = json.loads(rResponse.text)
                            add += parseRestaurantData(rData, g)
                    else:
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


        if  os.path.isfile(file_path):
            if file_path[-5:] == ".json":
                with open(file_path, 'r', encoding="UTF-8") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        to_check = data[0]
                    else:
                        to_check = data
                    if 'coopcycle_url' in to_check:
                        print("Identified data as coopcycle information\n")
                        for city in data:
                            if parseProfessionalServiceJson(city, g) > 0:
                                add += 1
                                added.append(city)
                        else:
                            print(f"We added {add} element from coopcycle partnership")

                        process = input("Do you want to read the data of all partner registered ?(y/n)\n>>>")
                        if process in ["y", "Y", "yes", "YES", "Yes", "o", "oui", "Oui", "OUI"]:
                            for c in added:
                                urlGroupOfRestaurant = c['coopcycle_url'] + '/api/restaurants'
                                response = requests.get(urlGroupOfRestaurant)
                                data = json.loads(response.text)
                                if 'hydra:member' in data:
                                    for item in data['hydra:member']:
                                            urlOfRestaurant = "{0.scheme}://{0.netloc}".format(urlsplit(urlGroupOfRestaurant)) +  item['@id']
                                            try:
                                                rResponse = requests.get(urlOfRestaurant)
                                                rResponse.raise_for_status()
                                                rData = json.loads(rResponse.text)
                                                add += parseRestaurantData(rData, g)
                                            except requests.exceptions.HTTPError as errh:
                                                print ("HTTP Error:", errh)
                                            except requests.exceptions.ConnectionError as errc:
                                                print ("Error Connecting:", errc)
                                                # Handle connection error

                                            except requests.exceptions.Timeout as errt:
                                                print ("Timeout Error:", errt)
                                                # Handle timeout error

                                            except requests.exceptions.RequestException as err:
                                                print ("Something went wrong:", err)
                                            
                                else:
                                    print(f"No Restaurants found for {c['name']}, request sent :\n{response.text}")

                    else:
                        print("Considering data as restaurant data\n")
                        if '@context' in data:
                            if data['@context'] == '/api/contexts/Menu':
                                restau = input("Menu context found, from what Restaurant does the menu comes ?\n>>>")
                                subject_uri = URIRef(ex + restau)
                                if  (subject_uri, None, None) not in g:
                                    print(f"Restaurant {restau} was not found, cannot add the menu data to inexistant element")
                                else:
                                    menu_node = BNode()
                                    g.add((subject_uri, URIRef(sh+'hasMenu'), menu_node))
                                    add += parseMenu(data, g, menu_node)
                            elif data['@context'] == '/api/contexts/Restaurant':
                                #print(data)
                                if 'hydra:member' in data:
                                    for item in data['hydra:member']:
                                        urlOfRestaurant = "{0.scheme}://{0.netloc}".format(urlsplit(item['image'])) + item['@id']
                                        rResponse = requests.get(urlOfRestaurant)
                                        rData = json.loads(rResponse.text)
                                        add += parseRestaurantData(rData, g)
                                else:
                                    add += parseRestaurantData(data, g)
                            else:
                                print("Unknown context, can't process the data")
            else :
                print("Given file wasn't from an expected format, please use JSON files\n")
        else:
            print("Given input doesnt reach a file\n")


    if len(g) > 0:
        r = input("Do you want to save the current data parsed ? (y/n)")

        if r in ["y", "Y", "yes", "YES", "Yes", "o", "oui", "Oui", "OUI"]:
            if exist:
                os.remove("server_data/data_semweb.db")
            g.serialize(destination="server_data/data_semweb.db", format="turtle")