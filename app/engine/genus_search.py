from helpers.elastic_search_utils import get_search_client
from helpers.genus_utils import get_genus_info, get_suitable_genus
import re

def search_similar_genus(analysis, genus0_l):
  demand_list=[]
  resp = get_search_client().search(source=["genus", "skills"],
      index="genuses",
    explain=True,
    size=5,
    query=get_genus_query(analysis, genus0_l),
    preference="consistent")
  
  id=1
  for hit in resp["hits"]["hits"]:
    ggg = get_genus_info(hit["_source"]["genus"])
    output={}
    output['id']=id
    output['job_title']=ggg['designation']
    output['job_description']=ggg['jd']
    output['skills']=hit["_source"]["skills"]
    output['genus']=hit["_source"]["genus"]
    overall_score=hit["_score"]

    output["score"]={
        'total_score': str(round((overall_score * 10) + 50, 2)) + "%",
        'basedon': []
    }

    id=id+1
    demand_list.append(output)
  return demand_list


def get_genus_query(analysis, genus0_l):  
  q = {
      "bool": {      
        "filter": get_g_genus_preference(analysis), 
        "should": get_g_genus0_query(genus0_l),
        "must": [
          {
            "bool": {
              "should" : [
                {
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
                      "min_score": "0.9"
                    }
                }
              ]
            }  
        }]
      }
  }
  return q

def get_g_genus_preference(aa):
  gs_query = []
  if type(aa["Years of Experience"]) == int:
      ys_i = aa["Years of Experience"]
  else:
      ys = re.findall(r'^\D*(\d+)', aa["Years of Experience"])
      if len(ys) > 0:
          ys_i = int(ys[0])
  for g in get_suitable_genus(ys_i):
      gs_query.append({
          "term": {
            "genus1_k": {
              "value": g
            }
          }
        })

  return {
    "bool": {
      "minimum_should_match": 1, 
      "should": gs_query
    }
  }

def get_g_genus0_query(genus0_l):
  genus0_query = []
  for i in genus0_l:
      genus0_query.append({
          "constant_score": {
            "filter": {
                "term": {
                  "genus0_k": {
                    "value": i
                  }
                }
            },
            "boost": 3
          }        
      })
  return genus0_query