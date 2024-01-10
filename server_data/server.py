from rdflib_endpoint import SparqlEndpoint
import os
from rdflib import Graph
import uvicorn

def init_serv(app, g):

    example_query = """
            SELECT DISTINCT ?s ?p ?o WHERE {
                    ?s ?p ?o 
            }
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