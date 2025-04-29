from apiflask import Schema
from apiflask.fields import String, Integer, List, Nested, Float, Field
from apiflask.validators import Length, Range

# Schema definitions
class BaseResponse(Schema):
    data = Field()  
    message = String()
    code = Integer()

class AnimalSchema(Schema):
    id = Integer()
    name = String()
    description = String()
    
class ZooSchema(Schema):
    id = Integer()
    name = String()
    featured_animals = List(Nested(AnimalSchema))


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

class LocationRequestSchema(Schema):
    place = String(default="1600 Amphitheatre Parkway, Mountain View, CA", required=True)

class LocationSchema(Schema):
    lattitude = Float()
    longitude = Float()
    formatted_address = String()