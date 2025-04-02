# Learning API

A web API built with APIFlask, Python, OpenAI, and Neon DB that helps users learn skills based on job postings.

## Features

- Parse job postings to extract skills
- Generate course outlines for skills using OpenAI
- Self-assess skill levels
- Generate course content
- Track learning progress

## API Endpoints

- `POST /api/job-posting`: Submit a job posting URL to extract skills
- `POST /api/select-skill`: Select a skill to generate a course outline
- `POST /api/assess-skills`: Self-assess skill levels
- `POST /api/begin-course`: Begin or resume a course
- `POST /api/advance-topic`: Advance to the next topic

## Setup

1. Clone this repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set up environment variables:
   - `OPENAI_API_KEY`: Your OpenAI API key
   - Database connection variables (provided by Neon DB)
4. Run the application: `python app.py` or `flask run --port 5001`. The second allows auto updates from saves. 

## Deployment

This application is configured for deployment on Vercel.

## Orchestration Design

1) given job desc, return structured list of skills
2) given skill, return course outline
3) given topic, return block of content with pagination
4) given topic, return assessment
5) given course and user, return progress report
