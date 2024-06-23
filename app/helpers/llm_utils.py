import os
from openai import AzureOpenAI

import aiohttp
import asyncio

from helpers.prompts import get_resume_information, get_resume_skills_prompt, get_resume_summary_prompt

api-key = os.environ["api-key"]
azure_openai_endpoint = os.environ["azure-openai-endpoint"]
openai-model-name = os.environ["openai-model-name"]
openai-embedding-model-name=os.environ["openai-embedding-model-name"]

openai_client = AzureOpenAI(
  api-key = api-key,
  api_version = "2024-02-01",
  azure_endpoint = azure_openai_endpoint
)

def get_embeddings(text):
  response = openai_client.embeddings.create(
    input=text,
    model=openai-embedding-model-name
    )
  return response.data[0].embedding


async def make_openai_request(prompt):
    r = openai_client.completions.create(
        model=openai-model-name,
        prompt=prompt,
        temperature=0,
        max_tokens=2048,
        seed=12345
    )
    return r.choices[0].text

async def execute_prompts_async(prompts):
    tasks = [make_openai_request(prompt) for prompt in prompts]
    results = await asyncio.gather(*tasks)
    return results

def extract_resume_key_details(text):
    prompts = [
        get_resume_summary_prompt(text),
        get_resume_skills_prompt(text),
        get_resume_information(text)
    ]
    return "\n".join(execute_prompts(prompts))

def execute_prompts(prompts):
    return asyncio.run(execute_prompts_async(prompts))    

def get_reasoning_prompt(summary_1, skills_1, summary_e, skill_e):
    g_e = []
    if summary_1 is not None:
        g_e.append(summary_1)
    if skills_1 is not None:
        g_e.append(", ".join(skills_1))

    g_e = "\n".join(g_e)

    m_e = []
    if summary_e is not None:
        m_e.append(summary_e)
    if skill_e is not None:
        m_e.append(skill_e)

    m_e = "\n".join(m_e)
    
    prompt = f"""Your task is to compare 'Given cv experience' and 'Given jd experience'. 
Return why the given cv is a match for the given jd experience, as matching_explaination and matching_skills.

Response format 
1. matching_explaination - 3 bullet points explanation of why the given cv is a match for the given jd experience.
2. Each bullet point should only explain the aspects that are match with jd experience.
matching aspects like experience, skills, proficiency, domain worked on.
e.g. 
- Matched 9 years of experience in backend development.
- Matched relevant skills in Machine Learning, Python, Streamlit, Computer Vision.
3. matching_skills - 10 important skills possesed in the cv that are matching the given jd experience.
5. Strictly return in this format only .
skill_match_score: [score in percentage]
experience_match_score: [score in percentage]
matching_explaination:
[matching_explaination]
matching_skills: 
[matching_skills]

Given cv experience 
{g_e}
 
Given jd experience
{m_e}

"""
    return prompt
 
def match_resume(summary_1, skills_1, summary, skill):
    prompt = get_reasoning_prompt(summary_1, skills_1, summary, skill)
    return prompt