def get_resume_summary_prompt(resume_text):
    return f"""You are an AI assistant tasked with generating a concise work experience summary based on the provided resume text.
Your response should be structured as follows:
Work Experience Summary:
[A concise summary of the work experience, focusing solely on the roles held and domains worked in, in 3-4 sentences. Do not mention the number of years of experience, certifications, awards, achievements, work location and skills in this summary section.]

Here is the resume text:

```
{resume_text}
```
Please generate the work experience summary based on the provided resume text, following the specified structure and instructions carefully."""



def get_resume_skills_prompt(resume_text):
    return f"""You are an AI assistant tasked with generate required information from given resume.
Your response should be structured as follows:

Skills:
[List of all proficient skills in 200 words, separated by commas. Do not repeat the skills.]

Here is the resume text:

```
{resume_text}
```

Please generate the work experience summary based on the provided resume text, following the specified structure and instructions carefully."""


def get_resume_information(resume_text):
    return f"""You are an AI assistant tasked with generate required information from given resume.
Your response should be structured as follows:
Years of Professional Experience: [Total number of years working in any professional capacity in numbers only. Exclude any personal projects or training experiences for students or freshers.]
Most Recent Work Location: [City, State/Country]
Candidate Name: [Candidate's name]

Here is the resume text:

```
{resume_text}
"""