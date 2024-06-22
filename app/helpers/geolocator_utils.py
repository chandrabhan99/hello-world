from geopy.geocoders import Nominatim
from geopy.distance import geodesic

geolocator = Nominatim(user_agent="my_user_agent")

def get_lon_lat(loc):
  lon_lat = None
  if type(loc) == str:
      if 'Remote' in loc:
          l = loc.split(',')[-1].strip()
      else:
          l = loc
      
      c = geolocator.geocode(l)
      if c is None:
          l = loc.split(',')[-1].strip()        
          c = geolocator.geocode(l)
      if c is not None:
          lon_lat = {  "lat": c.latitude, "lon": c.longitude}
  return lon_lat

def get_distance(loc1, loc2):
    loc1_ll = get_lon_lat(loc1)
    loc2_ll = get_lon_lat(loc2)
    return geodesic((loc1_ll['lat'], loc1_ll['lon']), (loc2_ll['lat'], loc2_ll['lon'])).miles