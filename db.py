import os
import psycopg2
from dotenv import load_dotenv
import util

# Load environment variables
load_dotenv()

def get_db_connection():
    """Create a connection to the Neon PostgreSQL database"""
    conn = psycopg2.connect(
        host=os.getenv('PGHOST'),
        database=os.getenv('PGDATABASE'),
        user=os.getenv('PGUSER'),
        password=os.getenv('PGPASSWORD')
    )
    return conn

def save_skills_list(skills_list):
   try:
           # Store skills in database
      skills_data = []
      for skill_name in skills_list:
         job_id=-1
         # Check if skill already exists
         conn = get_db_connection()
         cursor = conn.cursor()
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
      util.log(util.LogLevel.Error, str(e))
      raise e


def save_outline(outline):
    return
