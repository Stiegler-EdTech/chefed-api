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
4. Run the application: `python app.py`

## Deployment

This application is configured for deployment on Vercel.

