import requests
import json

# Base URL (change this to your deployed API URL)
BASE_URL = "https://chefed-bruw86rex-stiegler-edtech.vercel.app"

# Test token (should match one in the app.py file)
TOKEN = "test_token"
HEADERS = {"Authorization": f"Bearer {TOKEN}"}

def test_job_posting():
    """Test submitting a job posting URL"""
    url = f"{BASE_URL}/api/job-posting"
    data = {
        "url": "https://www.example.com/job/software-engineer"
    }
    response = requests.post(url, json=data, headers=HEADERS)
    print("Job Posting Response:", response.status_code)
    print(json.dumps(response.json(), indent=2))
    return response.json()

def test_select_skill(skill_id):
    """Test selecting a skill"""
    url = f"{BASE_URL}/api/select-skill"
    data = {
        "skill_id": skill_id
    }
    response = requests.post(url, json=data, headers=HEADERS)
    print("Select Skill Response:", response.status_code)
    print(json.dumps(response.json(), indent=2))
    return response.json()

def test_assess_skills(topic_id):
    """Test skill assessment"""
    url = f"{BASE_URL}/api/assess-skills"
    data = {
        "assessments": [
            {
                "topic_id": topic_id,
                "proficiency_level": 3
            }
        ]
    }
    response = requests.post(url, json=data, headers=HEADERS)
    print("Assess Skills Response:", response.status_code)
    print(json.dumps(response.json(), indent=2))
    return response.json()

def test_begin_course(course_outline_id):
    """Test beginning a course"""
    url = f"{BASE_URL}/api/begin-course"
    data = {
        "course_outline_id": course_outline_id
    }
    response = requests.post(url, json=data, headers=HEADERS)
    print("Begin Course Response:", response.status_code)
    print(json.dumps(response.json(), indent=2))
    return response.json()

def test_advance_topic(topic_id):
    """Test advancing to the next topic"""
    url = f"{BASE_URL}/api/advance-topic"
    data = {
        "topic_id": topic_id
    }
    response = requests.post(url, json=data, headers=HEADERS)
    print("Advance Topic Response:", response.status_code)
    print(json.dumps(response.json(), indent=2))
    return response.json()

if __name__ == "__main__":
    # Run tests in sequence
    job_result = test_job_posting()
    if "skills" in job_result and len(job_result["skills"]) > 0:
        skill_id = job_result["skills"][0]["id"]
        
        outline_result = test_select_skill(skill_id)
        if "topics" in outline_result and len(outline_result["topics"]) > 0:
            topic_id = outline_result["topics"][0]["id"]
            course_outline_id = outline_result["id"]
            
            test_assess_skills(topic_id)
            begin_result = test_begin_course(course_outline_id)
            
            if "topic_id" in begin_result:
                test_advance_topic(begin_result["topic_id"])

