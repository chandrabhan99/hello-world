import logging
from app.helpers.elastic_search_utils import get_search_client

def get_genus_hist_res(analysis):
  resp = search_similar_resumes(analysis)
  gen_keys = []
  gen_pair = []
  for hit in resp["hits"]["hits"]:
      if hit["_score"] > 1:
          if hit["_source"]["genus0"] not in gen_keys:
              gen_keys.append(hit["_source"]["genus0"])
              gen_pair.append((hit["_source"]["genus0"], hit["_score"]))

  buckets = {}
  for b in resp["aggregations"]["genuses"]["buckets"]:
     if b["key"] in gen_keys:
        buckets[b["key"]] = b["doc_count"]
  
  return gen_pair, buckets

def search_similar_resumes(analysis):
  try:    
    resp = get_search_client().search(source=["genus0"], 
    index="resumes",
    size=20,
    query=get_resume_query(analysis), 
    aggs=get_resume_aggregation_query(),
    preference="consistent")
  except Exception as ex:
    logging.error('Failed to get similar resume. %s', ex, exc_info=True)
  return resp

def get_resume_query(analysis):
  return {
        "bool": 
        {
            "should" : 
            [{
                "query_string": {
                "query": ", ".join(analysis["Skills"]).replace("/", " "),
                "default_field": "skills",
                "boost": 0.01
                }
            },
            {
                "script_score" : {
                "query" : {"exists": {
                    "field": "summary_embedding"
                }},
                "script" : {
                    "source": "cosineSimilarity(params.query_vector, 'summary_embedding')",
                    "params": {
                        "query_vector": analysis['embedding'] 
                    }
                    },
                    "min_score": "0.8"
                }
            }]
        }
    }

def get_resume_aggregation_query():
  return {
    "genuses": {
      "terms": {
        "field": "genus0_k",
        "size": 500
      }
    }
  }