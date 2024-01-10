from rdflib_endpoint import SparqlEndpoint
import os
from rdflib import Graph
import uvicorn

def init_serv(app, g):

    example_query = """
            PREFIX sh1: <http://schema.org/>
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

            SELECT DISTINCT ?restaurant ?longitude ?latitude ?deliveryPrice ?deliveryMinimalCost ?hours ?food
            WHERE {{
                ?restaurant a sh1:Restaurant ;
                sh1:address ?add;
                sh1:openingHours ?hours;
                sh1:servesCuisine ?food;
                sh1:potentialAction ?pa.

                ?add a sh1:Place ;
                sh1:latitude ?latitude ;
                sh1:longitude ?longitude .

                ?pa sh1:PriceSpecification ?ps.

                ?ps sh1:price ?deliveryPrice.

                ?ps sh1:eligibleTransactionVolume ?etv.

                ?etv sh1:price ?deliveryMinimalCost .

            }}
            LIMIT 1000
            OFFSET 0
    """
    example_queries = {
    }

    app = SparqlEndpoint(
    graph=g,
    title="BONNEFOY and MARINE - SPARQL endpoint for RDFLib graph for Semantic Web Project",
    description="A SPARQL endpoint created by B and M",
    version="0.0.1",
    path="/",
    public_url="https://semantic-web-BP-MA-DSCM2/",
    cors_enabled=True,
    example_query=example_query,
    example_queries=example_queries,)

    return app



# On a lancé le tripleStore manuellement
if __name__ == "__main__":
    
    app = None
    g = Graph()

    if os.path.exists("server_data/data_semweb.db"):
        try:
            g.parse("server_data/data_semweb.db", format='turtle')
        except Exception as e:
            pass
        print("Existing data loaded : \n")
        exist = True
        #print(g.serialize())
    else:
        print("No existing data found\n")
        exist = False

    if exist:
        app = init_serv(app, g=g)
        uvicorn.run(app, host="localhost", port=8000)

    else:
        print("No data found, exiting program...")