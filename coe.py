import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def parse_job_posting(url, body):
   
    # Extract job posting content
    try:
        
        # Use OpenAI to extract skills from the job description
        prompt = f"""
        Extract a list of technical skills from the following job description. 
        Return only the list of skills as a JSON array of strings.
        
        Job Title: {title}
        
        Job Description:
        {body}
        """
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that extracts technical skills from job descriptions."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        skills_json = json.loads(response.choices[0].message.content)
        skills_list = skills_json.get('skills', [])
        
        # Store skills in database
        skills_data = []
        for skill_name in skills_list:
            # Check if skill already exists
            cursor.execute("SELECT id FROM skills WHERE name = %s", (skill_name,))
            result = cursor.fetchone()
            
            if result:
                skill_id = result[0]
            else:
                cursor.execute(
                    "INSERT INTO skills (name) VALUES (%s) RETURNING id",
                    (skill_name,)
                )
                skill_id = cursor.fetchone()[0]
            
            # Link skill to job posting
            cursor.execute(
                "INSERT INTO job_skills (job_id, skill_id) VALUES (%s, %s) ON CONFLICT DO NOTHING",
                (job_id, skill_id)
            )
            skills_data.append({"id": skill_id, "name": skill_name})
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {"skills": skills_data}
    
    except Exception as e:
        print(f"Error processing job posting: {str(e)}")
        abort(500, message=f"Error processing job posting: {str(e)}")
