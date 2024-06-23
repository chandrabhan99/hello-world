from elasticsearch import Elasticsearch
import os

elastic_url = os.environ["elastic-url"]
elastic_api_key = os.environ["elastic-api-key"]
e_client = Elasticsearch([elastic_url], api_key=elastic_api_key)

def get_search_client():
   return e_client