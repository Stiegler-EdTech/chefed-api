import os
from dotenv import load_dotenv
from openai import OpenAI
import json
import db
import util
import uuid
import os
import json

# Load environment variables
load_dotenv()

outline_result=None
# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def flight_check():
   return {"message":{"1":"Ready to go!"}}

def parse_job(desc_or_url):
   desc_or_url="https://www.indeed.com/viewjob?jk=8b7c696f002362d0&from=shareddesktop_copy"
    # Extract job posting content
   #https://www.indeed.com/viewjob?jk=8b7c696f002362d0&from=shareddesktop_copy
   #https://tysonfoods.wd5.myworkdayjobs.com/en-US/TSN/details/Continuous-Improvement-Manager_R0361223-1?jobFamilyGroup=4506c4a2b82c017025ec5e6da234cd2f&jobFamilyGroup=4506c4a2b82c0165ff9e9b6da234e72f

        
   # Use OpenAI to extract skills from the job description
   sys_prompt = f"""
   You are a specialized analyst designed to extract and categorize specific skills and experience from job descriptions. When given a job description or a URL pointing to one, you must:
   Systematically Identify Skills and Experience: Extract every listed skill and type of experience at a very granular level.
   Categorize Skills: Group extracted skills into higher-level categories. For example, "SQL Server Database Performance Tuning" should be categorized as a granular skill under the coarse category "SQL Server Database Skills."
   Differentiate Skill Types: Classify each skill as either a hard skill (technical, measurable abilities) or a soft skill (interpersonal, communication, and behavioral traits).
   Ensure Clarity and Structure: Provide clear, concise, and structured output that highlights the key competencies for the role.
   Provide Explanations: Offer brief explanations or examples of each skill upon request.
   Preserve Exact Wording: Capture and include specific skills as they are explicitly mentioned in the job descriptions (e.g., "LEAN 5S") without altering their wording.
   Follow these guidelines to deliver an accurate and user-friendly analysis of job descriptions.
   Return as a strict json object following the example below:
   {{'skills': [{{'skill': 'SQL Server Database Performance Tuning',
      'category': 'SQL Server Database',
      'soft_hard': 'hard',
      'explanation': 'Experience using advanced SQL Server performance tuning tools and techniques.'}},
   {{'skill': 'Agile Software Development Practices',
      'category': 'Software Engineering',
      'soft_hard': 'soft',
      'explanation': 'Ability to use Agile practices, such as Scrum, to effect efficiency and productivity.'}}]
   }}
  
   """
        
   # response = client.chat.completions.create(
   #    model="o3-mini",
   #    messages=[
   #          {"role": "system", "content": sys_prompt},
   #          {"role": "user", "content": desc_or_url}
   #    ],
   #    response_format={"type": "json_object"}
   # )

   response = client.responses.create(
   model="o3-mini",
   input=[
      {"role": "system", "content": sys_prompt},
      {"role": "user", "content": desc_or_url}
   ])

 
   
   #skills_json = json.loads(response.choices[0].message.content)
   skills_json = json.loads(response.output_text)   
                          
   skills_list = skills_json.get('skills', [])
   for skill in skills_list:
    skill['id'] = str(uuid.uuid4())

   util.log_verbose(skills_list)
   
   db.save_skills_list(skills_list)
   return {"skills": skills_list}

def generate_outline(skill):
        
   # Use OpenAI to extract skills from the job description
   sys_prompt = f"""
   You are an experienced education curriculum writer designed to generate a course outline for any given skill. The outline should cover all knowledge areas typically found in real-world professional settings. The outline should include sections for hands-on practice where possible.
   When given a skill, you must provide:
   Overview: Provide an introduction, context, and explanation of the skill. Articulate why the skill is valuable in real-world professional settings.
   Topics and Subtopics: List each major competency topic and its subtopics in a logical progression, ensuring comprehensive coverage of both theoretical concepts and practical applications.
   Learning Objectives: For each topic, clearly specify what learners should know or be able to do by the end of each topic.
   Hands-On Practice: For each major topic, include at least one hands-on activity, exercise, or project that allows learners to practice the skill in a realistic context.
   Additional Resources: Suggest case studies, industry examples, or supplemental materials such as articles, videos, open-source tools, or relevant communities, to deepen learners’ knowledge and support continued exploration.
   Output as Structured json: Provide all above elements following strictly the json example below.
   Return as a strict json object following the example below:
   {{
      "overview": "A concise introduction explaining the skill, its context, and why it is valuable in professional settings.",
      "topics": [
         {{
            "topic_name": "Main Topic Title",
            "subtopics": [
            "Subtopic 1",
            "Subtopic 2"
            ],
            "learning_objectives": [
            "Objective A: What learners should know/do by the end of this topic.",
            "Objective B: What learners should know/do by the end of this topic."
            ],
            "hands_on_practice": [
            {{
               "activity_title": "Practical Exercise or Project",
               "description": "A brief explanation of the hands-on activity that reinforces the topic’s concepts."
            }}
            ]
         }},
         {{
            "topic_name": "Another Main Topic Title",
            "subtopics": [
            "Subtopic 3",
            "Subtopic 4"
            ],
            "learning_objectives": [
            "Objective C: What learners should know/do by the end of this topic.",
            "Objective D: What learners should know/do by the end of this topic."
            ],
            "hands_on_practice": [
            {{
               "activity_title": "Second Practical Exercise",
               "description": "A brief explanation of another hands-on activity to deepen understanding."
            }}
            ]
         }}
      ],
      "additional_resources": [
         "Reference 1 (e.g., a link to a case study, article, or video)",
         "Reference 2 (e.g., open-source tools or relevant community resources)"
      ]
      }}
   """
   response = client.responses.create(
   model="o3-mini",
   input=[
      {"role": "system", "content": sys_prompt},
      {"role": "user", "content": skill}
   ])

   global outline_result
   outline_result = json.loads(response.output_text)  
   for topic in outline_result["topics"]:
      topic['id'] = str(uuid.uuid4())
   return outline_result


def generate_learning_block(topic, subtopic):
   user_prompt = f"""subtopic={subtopic} | topic={topic}"""
   print(user_prompt)  
   sys_prompt = f"""
   You are an experienced education curriculum writer designed to generate a paragraph or two for a given skill subtopic. 
   The content should briefly introduce the given subtopic, in context of the given topic. 
   When given a subtopic and its parent topic, you must provide:
   Sections of content about the subtopic in progression that covers the subtopic at high level and in total is between 2-3 paragraphs.
   Include a URL to a relevant image somewhere in the content.
   A section is either blocks of text or a link to a web-searched image that illustrates the content.
   """ 
  
   # Use OpenAI to extract skills from the job description
   sys_prompt = f"""
   You are an experienced education curriculum writer designed to generate a course learning content for any given skill subtopic for a given topic. 
   The content should cover the given subtopic, in context of the given topic, as would be found in real-world professional settings. 
   When given a subtopic and its parent topic, you must provide:
   Sections of educational content in progression that covers the subtopic in depth.
   A section is either blocks of text or a link to a web-searched image that illustrates the content.
   Try to include 1-2 images about every 5-15 paragraphs. 
   """

   structured_output_spec = """
   {
      "format": {
         "type": "json_schema",
         "name": "blocks_result",
         "schema": {
            "type": "object",
            "properties": {
               "topic": {
                  "type": "string"
               },
               "subtopic": {
                  "type": "string"
               },
               "blocks": {
                  "type": "array",
                  "items": {
                     "type": "object",
                     "properties": {
                        "block_type": {
                           "enum": ["image", "text"]
                        },
                        "content": {
                           "type": "string"
                        }
                     },
                     "required": ["block_type", "content"],
                     "additionalProperties": false
                  }
               }
            },
            "required": ["topic", "subtopic", "blocks"],
            "additionalProperties": false
         },
         "strict": true
      }
   }
   """
   response = client.responses.create(
      model="o3-mini-2025-01-31",
      input=[
         {"role": "system", "content": sys_prompt},
         {"role": "user", "content": user_prompt}
      ],  
      text=json.loads(structured_output_spec),
      reasoning={"effort": "high"},
   )

   block_result = json.loads(response.output_text)  
   for block in block_result["blocks"]:
      block['id'] = str(uuid.uuid4())
   return block_result



def get_last_outline():

   skills_file_path = os.path.join("samples", "outline-net_core2.json")
   # Read the skills_file as a string
   with open(skills_file_path, 'r') as file:
      skills_file_content = file.read()

   outline = json.loads(skills_file_content)
   return outline