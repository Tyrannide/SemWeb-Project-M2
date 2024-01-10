from geopy import Nominatim
from rdflib import Graph, URIRef, Literal, BNode
from rdflib.namespace import RDF, XSD
import random
import string


def generate_random_string(length):
    letters_and_digits = string.ascii_letters + string.digits
    return ''.join(random.choice(letters_and_digits) for _ in range(length))

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

    print("Please answer the following questions in order to build your preference schema")

    sh = "http://schema.org/"
    ex = "http://www.example.com/"

    name = input("Please enter your first name followed by your last name\n>>>")

    address = input("Where do you live ? Answer with your postal addresse and post code along the city, expected format (address, postcode city)\n>>>")
    adress = convert_co(address)

    if adress is not None:
        radius = float(input("At what maximum range do you want the restaurant to be? expected format as km\n>>>"))
        price = float(input("What is the maximum price you accept to pay without delivery fees?\n>>>"))
        seller = input("Please give us the seller you're looking for first. We expect the coopcycle url like : https://coursiers-stephanois.coopcycle.org/api/restaurants/24\n>>>")
        if seller[0:4] != "http":
            print("Wrong url format given")
            exit()
        else:
            itemInput = input("Please give us the kind of food you expect to be recommended the most\n We expect the wikidata entity code, for example Q177 for Pizza\n>>>")
            items = itemInput.split(' ')
            for i in items:
                if i[0] != 'Q' and not i[1:].isnumeric:
                    print(f"{i} ins't a valid item")
                    exit()
            else:
                print("Processing your data")
                g = Graph()
                g.bind("sh", sh)
                g.bind("ex", ex)
                g.add((URIRef(ex+ name.replace(" ", "-")), RDF.type, URIRef(sh+"Person")))
                g.add((URIRef(ex+ name.replace(" ", "-")), URIRef(sh+'name'), Literal(name)))
                address_node = BNode()
                g.add((URIRef(ex+ name.replace(" ", "-")), URIRef(sh+'address'), address_node))
                g.add((address_node, RDF.type, URIRef(sh+"PostalAddress")))
                g.add((address_node, URIRef(sh+'postalCode'), Literal(address.split(', ')[1].split(' ')[0])))
                g.add((address_node, URIRef(sh+'addressLocality'), Literal(address.split(', ')[1].split(' ')[1])))
                g.add((address_node, URIRef(sh+'streetAddress'), Literal(address.split(',')[0])))
                seek_node = BNode()
                g.add((URIRef(ex+ name.replace(" ", "-")), URIRef(sh+'seeks'), seek_node))
                g.add((seek_node, URIRef(sh+'seller'), Literal(seller)))
                pricespecif_node = BNode()
                g.add((seek_node, URIRef(sh+'priceSpecification'), pricespecif_node))
                g.add((pricespecif_node,URIRef(sh+'maxPrice'),Literal(str(price), datatype=XSD.decimal)))
                g.add((pricespecif_node, URIRef(sh+'priceCurrency'), Literal("EUR")))
                available_node = BNode()
                g.add((seek_node, URIRef(sh+'availableAtOrFrom'), available_node))
                geo_node = BNode()
                g.add((available_node, URIRef(sh+'geoWithin'), geo_node))
                g.add((geo_node, RDF.type, URIRef(sh+'GeoCircle')))
                geoPos_node = BNode()
                g.add((geo_node, URIRef(sh+'geoMidpoint'), geoPos_node))
                g.add((geoPos_node, URIRef(sh+'latitude'), Literal(str(adress[1]), datatype=XSD.decimal)))
                g.add((geoPos_node, URIRef(sh+'longitude'), Literal(str(adress[0]), datatype=XSD.decimal)))
                g.add((geo_node, URIRef(sh+'geoRadius'), Literal(str(radius*1000), datatype=XSD.decimal)))
                g.add((seek_node, URIRef(sh+'itemOfferred') , Literal(items)))

                g.serialize(destination="schema_pref/pref-"+ name.split(' ')[1] +".ttl", format="turtle")

    else:
        exit()