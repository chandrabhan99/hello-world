import re
from helpers.llm_utils import match_resume, execute_prompts

def get_match_reason(summary_1, skills_1, summaries, skills):
    json_responses = []


    prompts = []
    for i in range(len(summaries)):
        prompts.append(match_resume(summary_1, skills_1, summaries[i], skills[i]))
    
    responses = execute_prompts(prompts)
    
    for response in responses:
        json_response = get_json_response(response)
        json_responses.append(json_response)

    return json_responses

def get_json_response(response):
    json_data = response.replace("'", '"')
    json_data = get_formatted_data(json_data)
    return json_data

def get_formatted_data(resume_text):
    lines = resume_text.strip().split('\n')
    capture_summary = False
    capture_skills = False

    formatted_data = {}
    formatted_data["matching_explaination"] = []
    formatted_data["matching_skills"] = []
    for line in lines:
        if line.startswith("skill_match_score:"):
            formatted_data["skill_match_score"] = line.split(":")[1].strip()
        if line.startswith("experience_match_score:"):
            formatted_data["experience_match_score"] = line.split(":")[1].strip()
        elif line.startswith("matching_explaination:"):
            capture_summary = True
            capture_skills = False
        elif line.startswith("matching_skills:"):
            capture_skills = True
            capture_summary = False
        else:
            line = line.strip("-").strip()
            if line:
                if capture_summary:   
                    formatted_data["matching_explaination"].append(line)
                elif capture_skills:                  
                    formatted_data["matching_skills"] += [skill.strip() for skill in line.split(",")]

    formatted_data["matching_skills"] = list(set(formatted_data["matching_skills"]))

    return formatted_data