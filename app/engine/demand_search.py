from app.helpers.elastic_search_utils import get_search_client
from app.helpers.genus_utils import get_genus_info, get_suitable_genus
from app.helpers.geolocator_utils import get_lon_lat, get_distance
import re
import math

ranges = [
    (0, 1, 50, 60),
    (1, 2, 60, 70),
    (2, 3, 65, 75),
    (3, 4, 75, 85),
    (4, 500, 85, 95)
]

def get_percentage_by_range(max, min, i):
    s = 95
    for r in ranges:
        if i >= r[0] and i < r[1]:
            if min == max:
               s = r[3]
            else:
               s = r[2] + ((i - min) * (r[3] - r[2])) / (max - min)
            break
    return round(s, 2)

fields =  {
  'skills': "Sk", 
  'genus0.keyword': "R Sim",
  "summary_embedding": "JD Sim"
}

def print_scores(e):
  score_text = []
  score_keys = []
  scores = []
  a = get_scores(e, scores)
  if len(scores) == 0:
     scores = a
  for i in scores:
      perc = round(i[1] * 100 / e['value'], 2)
      if perc > 0 and i[0] not in score_keys:
          score_text.append(i[0] + "-" + str(round(i[1], 4)))
          score_keys.append(i[0])
  return score_text

def get_scores(e_d, scores):
  f_d = []
  for f in fields:
      if f in e_d['description']:
          f_d.append((fields[f], e_d['value']))
          break
          
  if len(f_d) == 0:
      for d in e_d['details']:
          f_k = get_scores(d, scores)
          f_d += f_k

  keys = set()
  for i in f_d:
      keys.add(i[0])

  if len(keys) == 1:
      f_d = [(f_d[0][0], e_d['value'])]
  
  n_f_d = {}
  if len(keys) > 1:
      for j in f_d:
          if j[0] not in n_f_d:
              scores.append(j)
          
  return f_d

def search_similar_demands(analysis, genus0_l, location):
  q = get_demand_query(analysis, genus0_l, location)

  resp = get_search_client().search(source=["genus", "summary", "location", "skills"],
      index="demand",
    explain=True,
    size=5,
    query=q,
    preference="consistent")
  
  id=1
  demand_list=[]
  demand_similar_list=[]
  min_score = resp["hits"]["hits"][-1]["_score"] 
  
  for hit in resp["hits"]["hits"]:
    ggg = get_genus_info(hit["_source"]["genus"])
    output={}
    output['id']=id
    output['job_title']=ggg['designation']
    output['job_description']=ggg['jd']
    output['skills']=hit["_source"]["skills"]
    output['genus']=hit["_source"]["genus"]
    output['location']=hit["_source"]["location"]
    overall_score = hit["_score"]    

    output["score"]= {
        'total_score': str(get_percentage_by_range(resp["hits"]["max_score"], min_score, overall_score)) + "%",
        'basedon': []
    }
    
    id=id+1
    
    d = None
    try:
      loc = None
      if location is not None and len(location) > 0:
        if location.lower() != "wfa" and location.lower() != "remote":
            loc = location
        else:
           loc = "Remote, India"
      else:
        if 'Most Recent Work Location' in analysis:
          loc = analysis['Most Recent Work Location']

      d = get_distance(output['location'], loc)
    except:
       pass
    
    output['location'] = output['location'] # + " - " + ", ".join(print_scores(hit["_explanation"])) + ", T-" + str(round(hit["_score"], 4))
    score_list=print_scores(hit["_explanation"])
    key_value_pairs = {entry.split('-')[0].replace('Sk', 'Skill').replace('JD Sim', 'JD').replace('R Sim', 'Resume'): float(entry.split('-')[1]) for entry in score_list}
    output['similarity_score']=key_value_pairs
    
    if overall_score > 1 and \
      (("Remote" in output['location'] and "India" in output['location']) or 
       (d is not None and d < 100)):
      demand_list.append(output)
    else:
      demand_similar_list.append(output)

  return demand_list, demand_similar_list


def get_demand_query(analysis, genus0_l, location):
  filters = get_filters(analysis, location) 
  sh = get_genus0_query(genus0_l)
  
  q = {
      "bool": {      
        "filter": filters, 
        "should": sh,
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
                      "min_score": "0.8"
                    }
                }
              ]
            }  
        }]
      }
  }

  return q

def get_filters(analysis, location):
  filters = []

  # loc = None
  # if location is not None and len(location) > 0:
  #    if location.lower() != "wfa" and location.lower() != "remote":
  #       loc = location
  # else:
  #   if 'Most Recent Work Location' in analysis:
  #     loc = analysis['Most Recent Work Location']
  
  # if loc is not None:
  #     lon_lat = get_lon_lat(loc)
  #     if lon_lat is not None:
  #         filters.append({
  #           "geo_distance": {
  #             "distance": 1000,
  #             "location_ll": lon_lat
  #           }
  #         })

  filters.append(get_genus_preference(analysis))
  return filters

def get_genus0_query(genus0_l):
  genus0_query = []
  for i in genus0_l:
      genus0_query.append({
          "constant_score": {
            "filter": {
                "term": {
                  "genus0.keyword": {
                    "value": i[0]
                  }
                }
            },
            "boost": i[1]
          }        
      })
  return genus0_query


def get_genus_preference(aa):
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
            "genus1.keyword": {
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