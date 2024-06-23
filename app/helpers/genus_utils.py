import pandas as pd
from bs4 import BeautifulSoup
import io
from app.helpers.blob_storage_utils import get_blob

blob_content = get_blob("genus-data", "genus.csv")
ge = pd.read_csv(io.BytesIO(blob_content))
ge['Genus0'] = ge['Genus'].str.split('-').str[1:].apply(lambda x: '-'.join(map(str, x)))
ge['Genus1'] = ge['Genus'].str[:1]
ge['Genus2'] = ge['Genus'].str[2:3]

blob_content = get_blob("genus-data", "jd.csv")
j = pd.read_csv(io.BytesIO(blob_content))
j['Genus0'] = j['Genus without subband'].str.split('-').str[1:].apply(lambda x: '-'.join(map(str, x)))
j['Genus1'] = j['Genus without subband'].str[:1]

def get_genus_info(g):
    g1 = g[0]
    g2 = g[2]
    g0 = g[4:]
    return {
        "designation": get_designation(g0, g1, g2),
        "jd": get_jd(g0, g1)
    }

def get_designation(genus0, genus1, genus2):
    d = ge[(ge['Genus0'] == genus0) & (ge['Genus1'] == genus1) & (ge['Genus2'] == genus2)]['Designation']
    if len(d) > 0:
        return d.iloc[0]
    else:
        return None

def get_jd(genus0, genus1):
    d = j[(j['Genus0'] == genus0) & (j['Genus1'] == genus1)]['Content']
    if len(d) > 0:
        t = d.iloc[0]
        t.split("\n")
        soup = BeautifulSoup(t, features="lxml")
        t = soup.text
        return ". ".join(t.split("\n"))
    else:
        return None
    

def get_suitable_genus(years_of_exp):
  genus = []
  if years_of_exp < 2:
    return ["1"]
    
  if years_of_exp < 5:
    genus.append("1")
  
  if years_of_exp < 8:
    genus.append("2")        
  
  if years_of_exp > 3 and years_of_exp < 11:
    genus.append("3")        
  
  if years_of_exp >= 9:
    genus.append("4")

  if years_of_exp >= 13:
    genus.append("5")
  
  return genus