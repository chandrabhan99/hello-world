from app.helpers.elastic_search_utils import get_search_client
from datetime import datetime, timezone

def post(cv_key, feedback):
    response = False
    try:
        doc = {
            "cv_id": cv_key,
            "response": feedback["response"],
            "create_date": datetime.now(timezone.utc)
        }
        if "comments" in feedback:
            doc["comments"] = feedback["comments"]
        if "recommendation_suggestion" in feedback:
            doc["recommendation_suggestion"] = feedback["recommendation_suggestion"]

        get_search_client().index(index="feedback", document=doc)
        
        response = True
    except:
        pass
    
    return response