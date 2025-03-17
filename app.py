from apiflask import APIFlask, Schema, HTTPTokenAuth, abort
from apiflask.fields import String, Integer, List, Nested, Float
from apiflask.validators import Length, Range
from flask import request, g
import os
from dotenv import load_dotenv
from datetime import datetime
import json
import re
import requests
from bs4 import BeautifulSoup
from openai import OpenAI
from db import get_db_connection

# Load environment variables
load_dotenv()

# Initialize app
app = APIFlask(__name__, title='Learning API', version='1.0.0')
auth = HTTPTokenAuth(scheme='Bearer')

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Simple user authentication (for demo purposes)
USERS = {
    'test_token': {'id': 1, 'username': 'test_user'}
}

@auth.verify_token
def verify_token(token):
    if token in USERS:
        g.current_user = USERS[token]
        return True
    return False

# Schema definitions
class JobPostingSchema(Schema):
    url = String(required=True, validate=Length(min=1))

class SkillSchema(Schema):
    id = Integer()
    name = String()

class SkillListSchema(Schema):
    skills = List(Nested(SkillSchema))

class SkillSelectionSchema(Schema):
    skill_id = Integer(required=True)

class CourseTopicSchema(Schema):
    id = Integer()
    title = String()
    description = String()
    sequence_number = Integer()

class CourseOutlineSchema(Schema):
    id = Integer()
    skill_id = Integer()
    title = String()
    description = String()
    topics = List(Nested(CourseTopicSchema))

class SkillAssessmentSchema(Schema):
    topic_id = Integer(required=True)
    proficiency_level = Integer(required=True, validate=Range(min=1, max=5))

class SkillAssessmentListSchema(Schema):
    assessments = List(Nested(SkillAssessmentSchema))

class CourseProgressSchema(Schema):
    course_outline_id = Integer(required=True)

class TopicProgressSchema(Schema):
    topic_id = Integer(required=True)

class ProgressReportSchema(Schema):
    course_outline_id = Integer()
    completion_percentage = Float()
    current_topic_id = Integer()
    next_topic_id = Integer()

class TopicContentSchema(Schema):
    topic_id = Integer()
    content = String()

# Routes
@app.post('/api/job-posting')
@app.input(JobPostingSchema)
@app.output(SkillListSchema)
@auth.login_required
def submit_job_posting(data):
    """Submit a job posting URL to extract skills"""
    url = data['url']
    
    # Extract job posting content
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract job title and description (simplified)
        title = soup.title.string if soup.title else "Unknown Job Title"
        description = ' '.join([p.text for p in soup.find_all('p')])
        
        # Store job posting in database
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO job_postings (url, title, description) VALUES (%s, %s, %s) RETURNING id",
            (url, title, description)
        )
        job_id = cursor.fetchone()[0]
        
        # Use OpenAI to extract skills from the job description
        prompt = f"""
        Extract a list of technical skills from the following job description. 
        Return only the list of skills as a JSON array of strings.
        
        Job Title: {title}
        
        Job Description:
        {description}
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

@app.post('/api/select-skill')
@app.input(SkillSelectionSchema)
@app.output(CourseOutlineSchema)
@auth.login_required
def select_skill(data):
    """Generate a course outline based on the selected skill"""
    skill_id = data['skill_id']
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get skill name
        cursor.execute("SELECT name FROM skills WHERE id = %s", (skill_id,))
        result = cursor.fetchone()
        
        if not result:
            abort(404, message="Skill not found")
        
        skill_name = result[0]
        
        # Check if we already have a course outline for this skill
        cursor.execute(
            "SELECT id, title, description FROM course_outlines WHERE skill_id = %s",
            (skill_id,)
        )
        existing_outline = cursor.fetchone()
        
        if existing_outline:
            outline_id, title, description = existing_outline
            
            # Get existing topics
            cursor.execute(
                "SELECT id, title, description, sequence_number FROM course_topics WHERE course_outline_id = %s ORDER BY sequence_number",
                (outline_id,)
            )
            topics = [
                {
                    "id": row[0],
                    "title": row[1],
                    "description": row[2],
                    "sequence_number": row[3]
                }
                for row in cursor.fetchall()
            ]
            
            return {
                "id": outline_id,
                "skill_id": skill_id,
                "title": title,
                "description": description,
                "topics": topics
            }
        
        # Generate a course outline using OpenAI
        prompt = f"""
        Create a comprehensive course outline for learning {skill_name}. 
        The outline should include 5-10 topics that progress from beginner to advanced concepts.
        For each topic, provide a brief description.
        
        Return the result as a JSON object with the following structure:
        {{
            "title": "Course title",
            "description": "Overall course description",
            "topics": [
                {{
                    "title": "Topic 1 title",
                    "description": "Topic 1 description",
                    "sequence_number": 1
                }},
                ...
            ]
        }}
        """
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that creates learning outlines."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        outline_data = json.loads(response.choices[0].message.content)
        
        # Store course outline in database
        cursor.execute(
            "INSERT INTO course_outlines (skill_id, title, description) VALUES (%s, %s, %s) RETURNING id",
            (skill_id, outline_data['title'], outline_data['description'])
        )
        outline_id = cursor.fetchone()[0]
        
        # Store topics
        topics = []
        for topic in outline_data['topics']:
            cursor.execute(
                "INSERT INTO course_topics (course_outline_id, title, description, sequence_number) VALUES (%s, %s, %s, %s) RETURNING id",
                (outline_id, topic['title'], topic['description'], topic['sequence_number'])
            )
            topic_id = cursor.fetchone()[0]
            topic['id'] = topic_id
            topics.append(topic)
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            "id": outline_id,
            "skill_id": skill_id,
            "title": outline_data['title'],
            "description": outline_data['description'],
            "topics": topics
        }
    
    except Exception as e:
        print(f"Error generating course outline: {str(e)}")
        abort(500, message=f"Error generating course outline: {str(e)}")

@app.post('/api/assess-skills')
@app.input(SkillAssessmentListSchema)
@app.output({}, status_code=200)
@auth.login_required
def assess_skills(data):
    """Store user's self-assessment of skill levels"""
    user_id = g.current_user['id']
    assessments = data['assessments']
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        for assessment in assessments:
            topic_id = assessment['topic_id']
            proficiency_level = assessment['proficiency_level']
            
            # Get the skill_id for this topic
            cursor.execute(
                """
                SELECT s.id 
                FROM skills s
                JOIN course_outlines co ON s.id = co.skill_id
                JOIN course_topics ct ON co.id = ct.course_outline_id
                WHERE ct.id = %s
                """,
                (topic_id,)
            )
            result = cursor.fetchone()
            
            if not result:
                continue
                
            skill_id = result[0]
            
            # Store or update the assessment
            cursor.execute(
                """
                INSERT INTO user_skill_assessments (user_id, skill_id, proficiency_level)
                VALUES (%s, %s, %s)
                ON CONFLICT (user_id, skill_id) 
                DO UPDATE SET proficiency_level = %s, created_at = CURRENT_TIMESTAMP
                """,
                (user_id, skill_id, proficiency_level, proficiency_level)
            )
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {"message": "Skill assessments stored successfully"}
    
    except Exception as e:
        print(f"Error storing skill assessments: {str(e)}")
        abort(500, message=f"Error storing skill assessments: {str(e)}")

@app.post('/api/begin-course')
@app.input(CourseProgressSchema)
@app.output(TopicContentSchema)
@auth.login_required
def begin_course(data):
    """Begin or resume a course and get content for the current topic"""
    user_id = g.current_user['id']
    course_outline_id = data['course_outline_id']
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if user already has progress for this course
        cursor.execute(
            "SELECT current_topic_id FROM user_course_progress WHERE user_id = %s AND course_outline_id = %s",
            (user_id, course_outline_id)
        )
        result = cursor.fetchone()
        
        if result and result[0]:
            # User has existing progress, get the current topic
            topic_id = result[0]
        else:
            # Get the first topic of the course
            cursor.execute(
                "SELECT id FROM course_topics WHERE course_outline_id = %s ORDER BY sequence_number ASC LIMIT 1",
                (course_outline_id,)
            )
            result = cursor.fetchone()
            
            if not result:
                abort(404, message="No topics found for this course")
                
            topic_id = result[0]
            
            # Create or update progress record
            cursor.execute(
                """
                INSERT INTO user_course_progress (user_id, course_outline_id, current_topic_id, completion_percentage)
                VALUES (%s, %s, %s, 0)
                ON CONFLICT (user_id, course_outline_id) 
                DO UPDATE SET current_topic_id = %s, last_accessed = CURRENT_TIMESTAMP
                """,
                (user_id, course_outline_id, topic_id, topic_id)
            )
            conn.commit()
        
        # Check if we already have content for this topic
        cursor.execute(
            "SELECT content FROM topic_content WHERE topic_id = %s",
            (topic_id,)
        )
        content_result = cursor.fetchone()
        
        if content_result:
            content = content_result[0]
        else:
            # Get topic details
            cursor.execute(
                """
                SELECT ct.title, ct.description, s.name
                FROM course_topics ct
                JOIN course_outlines co ON ct.course_outline_id = co.id
                JOIN skills s ON co.skill_id = s.id
                WHERE ct.id = %s
                """,
                (topic_id,)
            )
            topic_result = cursor.fetchone()
            
            if not topic_result:
                abort(404, message="Topic not found")
                
            topic_title, topic_description, skill_name = topic_result
            
            # Generate content using OpenAI
            prompt = f"""
            Create comprehensive learning content for a topic in a course about {skill_name}.
            
            Topic: {topic_title}
            Description: {topic_description}
            
            The content should include:
            1. An introduction to the topic
            2. Key concepts and explanations
            3. Examples or code snippets where applicable
            4. Best practices
            5. A summary
            
            Format the content with Markdown.
            """
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert educator creating learning content."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            content = response.choices[0].message.content
            
            # Store the generated content
            cursor.execute(
                "INSERT INTO topic_content (topic_id, content) VALUES (%s, %s)",
                (topic_id, content)
            )
            conn.commit()
        
        cursor.close()
        conn.close()
        
        return {
            "topic_id": topic_id,
            "content": content
        }
    
    except Exception as e:
        print(f"Error beginning course: {str(e)}")
        abort(500, message=f"Error beginning course: {str(e)}")

@app.post('/api/advance-topic')
@app.input(TopicProgressSchema)
@app.output(ProgressReportSchema)
@auth.login_required
def advance_topic(data):
    """Mark current topic as complete and advance to the next topic"""
    user_id = g.current_user['id']
    completed_topic_id = data['topic_id']
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get course outline id for this topic
        cursor.execute(
            "SELECT course_outline_id FROM course_topics WHERE id = %s",
            (completed_topic_id,)
        )
        result = cursor.fetchone()
        
        if not result:
            abort(404, message="Topic not found")
            
        course_outline_id = result[0]
        
        # Get total number of topics in the course
        cursor.execute(
            "SELECT COUNT(*) FROM course_topics WHERE course_outline_id = %s",
            (course_outline_id,)
        )
        total_topics = cursor.fetchone()[0]
        
        # Get the next topic
        cursor.execute(
            """
            SELECT id FROM course_topics 
            WHERE course_outline_id = %s AND sequence_number > (
                SELECT sequence_number FROM course_topics WHERE id = %s
            )
            ORDER BY sequence_number ASC LIMIT 1
            """,
            (course_outline_id, completed_topic_id)
        )
        next_topic_result = cursor.fetchone()
        
        if next_topic_result:
            next_topic_id = next_topic_result[0]
            # Calculate completion percentage
            cursor.execute(
                "SELECT sequence_number FROM course_topics WHERE id = %s",
                (next_topic_id,)
            )
            next_sequence = cursor.fetchone()[0]
            completion_percentage = (next_sequence - 1) / total_topics * 100
        else:
            # This was the last topic
            next_topic_id = None
            completion_percentage = 100
        
        # Update progress
        cursor.execute(
            """
            UPDATE user_course_progress 
            SET current_topic_id = %s, completion_percentage = %s, last_accessed = CURRENT_TIMESTAMP
            WHERE user_id = %s AND course_outline_id = %s
            RETURNING id
            """,
            (next_topic_id, completion_percentage, user_id, course_outline_id)
        )
        
        if cursor.rowcount == 0:
            # No existing progress record, create one
            cursor.execute(
                """
                INSERT INTO user_course_progress (user_id, course_outline_id, current_topic_id, completion_percentage)
                VALUES (%s, %s, %s, %s)
                """,
                (user_id, course_outline_id, next_topic_id, completion_percentage)
            )
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            "course_outline_id": course_outline_id,
            "completion_percentage": completion_percentage,
            "current_topic_id": completed_topic_id,
            "next_topic_id": next_topic_id
        }
    
    except Exception as e:
        print(f"Error advancing topic: {str(e)}")
        abort(500, message=f"Error advancing topic: {str(e)}")

if __name__ == '__main__':
    app.run(debug=True)

