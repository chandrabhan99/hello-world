from elasticsearch import Elasticsearch
import os

elastic-url = os.environ["elastic-url"]
elastic-api-key = os.environ["elastic-api-key"]
e_client = Elasticsearch(elastic-url, api-key=elastic-api-key)

def get_search_client():
   return e_client