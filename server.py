from rdflib_endpoint import SparqlEndpoint
import uvicorn



def init_serv(app, g):

    example_query = """
            SELECT DISTINCT * WHERE {
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