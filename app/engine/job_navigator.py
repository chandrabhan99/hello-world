from app.engine.demand_search import search_similar_demands
from app.engine.resume_search import get_genus_hist_res
from app.helpers.document_parser_utils import get_cv_and_analyze
from app.helpers.llm_utils import get_embeddings
from app.engine.match_explainer import get_match_reason

def get_recommendations(cv_key, location):
    extracted_info = get_cv_and_analyze(cv_key)
    if extracted_info == None:
        recommendations = {"error": "Unable to read the document."}
    else:
        extracted_info['embedding']=get_embeddings(extracted_info['Work Experience Summary'])
        recommendations = get_recommendations_internal(extracted_info, location)
    return recommendations

def get_recommendations_internal(extracted_info, location):

    genus0_l, genus_buc = get_genus_hist_res(extracted_info)
    matching_demands, similar_genus_demands = search_similar_demands(extracted_info, genus0_l, location)

    #similar_genus_demands = search_similar_genus(extracted_info, genus0_l)
    
    demand_skills=[]
    demand_summary=[]
    for i in range(len(matching_demands)):
        demand_summary.append(matching_demands[i]["job_description"])
    for i in range(len(matching_demands)):
        demand_skills.append(matching_demands[i]["skills"])

    genus_skills=[]
    genus_summary=[]
    for i in range(len(similar_genus_demands)):
        genus_summary.append(similar_genus_demands[i]["job_description"])
    for i in range(len(similar_genus_demands)):
        genus_skills.append(similar_genus_demands[i]["skills"])

    demand_matching_experiences = get_match_reason(extracted_info["Work Experience Summary"], extracted_info["Skills"], demand_summary, demand_skills)
    genus_matching_experiences = get_match_reason(extracted_info["Work Experience Summary"], extracted_info["Skills"], genus_summary, genus_skills)
    
    for i in range(len(matching_demands)):
        ind = i

        g0 = matching_demands[i]["genus"][4:]
        if g0 in genus_buc:
            matching_demands[i]["score"]["basedon"].append({
                "key": "similar_cv",
                'score': str(genus_buc[g0]),
                'match_title': "Based on similar cvs offered in the past",
                'match_description': str(genus_buc[g0]) + " Similar CVs offered in the past for this opening."
            })
        
        if len(demand_matching_experiences)>ind:

            #if demand_matching_experiences[ind]["skill_match_score"] != "0%":
            matching_demands[i]["score"]["basedon"].append({
                "key": "matched_skills",
                "score": demand_matching_experiences[ind]["skill_match_score"],                
                "match_title": "Matched relevant skills",
                "match_description": demand_matching_experiences[ind]["matching_skills"]
            })

            #if demand_matching_experiences[ind]["experience_match_score"] != "0%":
            matching_demands[i]["score"]["basedon"].append({                    
                "key": "matched_experience",
                "score": demand_matching_experiences[ind]["experience_match_score"],
                'match_title': "Matched similar experience",
                "match_description": demand_matching_experiences[ind]["matching_explaination"]
            })

    for i in range(len(similar_genus_demands)):
        ind = i

        g0 = similar_genus_demands[i]["genus"][4:]
        if g0 in genus_buc:
            
            similar_genus_demands[i]["score"]["basedon"].append({
                "key": "similar_cv",
                'score': str(genus_buc[g0]),
                'match_title': "Based on similar cvs offered in the past",
                'match_description': str(genus_buc[g0]) + " Similar CVs offered in the past for this opening."
            })
            
        if len(genus_matching_experiences)>ind:
            #if genus_matching_experiences[ind]["skill_match_score"] != "0%":
            similar_genus_demands[i]["score"]["basedon"].append({
                "key": "matched_skills",
                "score": genus_matching_experiences[ind]["skill_match_score"],                
                "match_title": "Matched relevant skills",
                "match_description": genus_matching_experiences[ind]["matching_skills"]
            })

            #if genus_matching_experiences[ind]["experience_match_score"] != "0%":
            similar_genus_demands[i]["score"]["basedon"].append({
                "key": "matched_experience",
                "score": genus_matching_experiences[ind]["experience_match_score"],
                'match_title': "Matched similar experience",
                "match_description": genus_matching_experiences[ind]["matching_explaination"]
            })

    response = {
        "cv_key": extracted_info["Candidate ID"],
        'cv_info': {
            "cv_cand_name": extracted_info["Name"],
            "cv_years_exp": extracted_info["Years of Experience"],
            "cv_location": extracted_info["Most Recent Work Location"],
            "cv_summary": extracted_info["Work Experience Summary"],
            "cv_skill": extracted_info["Skills"],
        },
        'matching_job_recommendations': matching_demands, 
        'other_similar_recommendations': similar_genus_demands
    }

    return response
