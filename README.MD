# Steps need to run the programm

You need to install first some dependencies : 

```python

python => 3.12.0 64bits

pip install uvicorn==0.25.0
pip install rdflib==7.0.0
pip install bs4==0.0.1
pip install pyshacl==0.25.0
pip install urllib3==1.24.3
pip install requests==2.21.0
pip install rdflib-endpoint==0.5.0
pip install geopy==2.4.1
pip install sparqlwrapper==2.0.0

```

## Typical use case :
```
Usage of query.py : python query.py --ranked-by (distance|price) [--schema-pref] [file]

Usage of collect.py : python collect.py [data_file] (must be .json)
                      python collect.py [URL] (can be coopcycle url (default if url not found), or any coopcycle_url/api)

Usage of describe.py : python describe.py

Usage of main.py : same as collect.py

Usage of server.py : python server_data/server.py or if inside server_data -> python server.py

```