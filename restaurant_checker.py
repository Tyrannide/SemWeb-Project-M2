import rdflib
import requests

def check_through_restaurants(g):
    print("================================================")
    valid = 0
    responses = []
    total = 0
    for q in g.triples((None,rdflib.term.URIRef('https://schema.org/url'), None)):
        total+=1
        try:
            response = requests.get(q[2], timeout = 7)
            responses.append(response)
            valid +=1
        except requests.exceptions.ReadTimeout:
            print(f"Site {q[2]} was unresponsive (timed out after 7s)")
        except requests.exceptions.SSLError:
            print(f"Site {q[2]} doesn't have a valid certificate, are you sure it is created and configured?")
        except requests.exceptions.ConnectionError:
            print(f"Site {q[2]} doesn't exist")
        except requests.exceptions.TooManyRedirects:
            print(f"Site {q[2]} had too many redirects, couldn't reach the endpoint")
    
    print(f"{valid}/{total} of urls responded")

    for r in responses:
        if not r.ok:
            print(f"Error {r.status_code}: {r.reason}")

    return response