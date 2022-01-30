from sqlalchemy.sql.coercions import InElementImpl
from typing import List, Optional
from datetime import date, datetime, time, timedelta
from enum import Enum
from pydantic import BaseModel
import warnings

#local
# from . import API
from sql.models import Board, Book, Chapter, Standard, Subject
from sql.database import Base

#docker
# from app.sql.models import API
# from app.sql.models import Board, Book, Chapter, Standard, Subject
# from app.sql.database import Base


# from sql.models import API

class Client(BaseModel):

    client_id : int
    name :str
    num_of_students : int
    is_active :bool
    phone_number :int
    email_address : str
    # apis : List[API] = []
    class Config:
        orm_mode = True
        arbitrary_types_allowed = True

class Student(BaseModel):
    name: str
    gender: str
    dob: str
    # school_name : Optional[str] = None
    # batch_name : Optional[str] = None
    # favorite_teacher_name : Optional[str] = None
    # is_active : bool
    email_address : str
    phone_number : str
    who_pays_for_course :str
    english_proficiency :str
    preferred_language :str

class StudentCreate(Student):
    student_id :int
    """
    school_name : str
    batch_id : int
    batch_name : str
    school_id : int
    school_name : str
    authorized_client_id : int
    client_name : str
    favorite_teacher_id : int
    favorite_teacher_name : str
    """
    class Config:
        orm_mode = True
        # arbitrary_types_allowed = True

class Teacher(BaseModel):

    name: str
    address: str
    school_id : int
    authorized_client_id : int
    course_id : int
    is_active : int
    email : str
    phone_number : str


class TeacherCreate(Teacher):
    teacher_id:int
    class Config:
        orm_mode = True
        arbitrary_types_allowed = True

class Business_Signup(BaseModel):
    name: str
    email : str
    no_of_students : int


class Business_Signup_base(Business_Signup):
    business_id :int
    class Config:
        orm_mode = True
        arbitrary_types_allowed = True

# class TeacherAvatar(BaseModel):
#     image_name : str
#     image_url : str
#     is_cartoon : Optional[bool]
#     class Config:
#         orm_mode = True
#         arbitrary_types_allowed = True

class School(BaseModel):
    school_id : int
    name : str
    address :str
    is_active : bool
    class Config:
        orm_mode = True
        arbitrary_types_allowed = True


class Courses(BaseModel):
    course_id : int
    name : int
    is_active : int
    authorized_client_id : int

class StatusEnum(str, Enum):
    DEFINING ='DEFINING'
    DOWNLOADING = 'DOWNLOADING'
    INPROGRESS = 'INPROGRESS'
    COMPLETED = 'COMPLETED'
    REMOVED = 'REMOVED'

class AssessmentTypeEnum(str, Enum):
    MCQ = 'MCQ'
    MOCK_INTERVIEW= 'MOCK_INTERVIEW'
    LONGFORM_QA= 'LONGFORM_QA'
    CONVERSATION_FOR_IMPROVING_ENGLISH='CONVERSATION_FOR_IMPROVING_ENGLISH'
    REVISION='REVISION'

class QuestionTypeEnum(str, Enum):
    MCQ = 'MCQ'
    OBJECTIVE = 'OBJECTIVE'

class ConvBotNameEnum(str, Enum):
    GPT3 = 'GPT3'
    RASA= 'RASA'
    BLENDER= 'BLENDER'
    ALBERT='ALBERT'

class LogRequest(BaseModel):
    logmessage: str
    logfile: str

class SearchResponse(BaseModel):
    response_id: int
    log_message: str
    log_file_path: str
    search_result: Optional[str]
    request_id: int
    updated_time: datetime
    matched_file: Optional[str]
    time_taken: int

class Response(SearchResponse):
    class Config:
       orm_mode = True

class SearchRequest(BaseModel):
    request_id: int
    macaddress: str
    starttime: datetime
    endtime: datetime
    status: StatusEnum
    user_nt_id: str
    updated_time: datetime
    time_taken: int
    logParam: List[Response] = []

class Request(SearchRequest):
    class Config:
       orm_mode = True

# user schemas
class UserInfoBase(BaseModel):
    username: str
    fullname: str

class UserCreate(UserInfoBase):
    password: str

class UserInfo(UserInfoBase):
    id: int
    class Config:
        orm_mode = True

# student schemas
class StudentInfoBase(BaseModel):
    name: str
    gender:str
    age:int
    email_address:str
    phone_number:str
    who_pays_for_course:str
    english_proficiency:str
    preferred_language:str
    batch_name: Optional[str]
    school_name: Optional[str]
    client_name: str

# student schemas
class UpdateFavouriteTeacher(BaseModel):
    student_id: int
    favourite_teacher_id:int

# Batch pydantic working fine!
class BatchBase(BaseModel):
    name: str
    is_active:bool
    year : int
    client_name:str
    school_name:str
    standard : int

class BatchCreate(BatchBase):
    batch_id: int
    class Config:
        orm_mode = True

class TeacherAvatar(BaseModel):
    image_name : str
    image_url : str
    user_id : int
    is_cartoon : Optional[bool] = False
    in_use : Optional[bool] = True

class TeacherAvatarResponse(BaseModel):
    image_url : str
    class Config:
        orm_mode = True

class VoiceSample(BaseModel):
    voice_sample_name : str
    voice_sample_url : str
    user_id : int
    in_use : Optional[bool] = True

class VoiceSampleResponse(BaseModel):
    voice_sample_url : str
    class Config:
        orm_mode = True

# school pydantic working fine!
class SchoolBase(BaseModel):
    school_name: str
    school_address:str
    board_id : int
    affiliation_code : str
    phone_number : str
    email_address : str

class SchoolCreate(SchoolBase):
    school_id: int

    class Config:
        orm_mode = True

class School(BaseModel):
    school_id:int
    board_id : int
    name:str
    address:str
    is_active:bool
    class Config:
        orm_mode = True
        arbitrary_types_allowed = True
# class School(SchoolBase):
#     class Config:
#         orm_mode = True
#         arbitrary_types_allowed = True


# TODO get batch, school, and client info as well..
# TODO - Dont use it
class BasicStudentInfo(BaseModel):
    name: str
    gender:str
    age:int
    email_address:str
    phone_number:str
    who_pays_for_course:str
    english_proficiency:str
    preferred_language:str
    favourite_teacher_id:Optional[int]
    favourite_teacher_name: Optional[str]
    favourite_teacher_avatar_url: Optional[str]
    # batch_name: Batch
    class Config:
        orm_mode=True


# class StudentCreate(StudentInfoBase):
#    password: str

#TODO - Dont use it
class StudentInfo(BasicStudentInfo):
    student_id: int
    school: str
    batch: str
    client: str
    class Config:
        orm_mode = True

class LimitedStudentInfo(BaseModel):
    name: str
    phone_number: str
    email_address: str
    gender : str
    dob : str
    class Config:
        orm_mode = True

# API
class APIBase(BaseModel):
    name: str
    # end_point: str
    is_active:bool
    end_point:str

class APICreate(APIBase):
    api_id:int
    class Config:
        orm_mode = True
        arbitrary_types_allowed = True

class API(BaseModel):
    name:str
    is_active:bool
    class Config:
        orm_mode = True
        arbitrary_types_allowed = True

# Course
class CourseBase(BaseModel):
    name: str
    is_active:bool

class CourseCreate(CourseBase):
    pass

class Course(CourseBase):
    #id:int

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True

# batch
# class BatchBase(BaseModel):
#     name: str
#     is_active:bool

# class BatchCreate(BatchBase):
#     pass

class Batch(BaseModel):
    batch_id:int
    name: str
    is_active: bool

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True

class CourseBatchBook(BaseModel):
    course_name:str
    batch_name:str
    book_name:str
    is_active:bool

class UserBase(BaseModel):
    name: str
    email_address:str
    phone_number:str
    current_grade: str
    image_url : str
    latitude : str
    longitude : str
    apis: List[API] = []

class Conversation(BaseModel):
    user_id: int
    request: str
    response: str
    conv_bot_name: ConvBotNameEnum
    class Config:
        orm_mode = True

# Client schemas
class ClientInfoBase(BaseModel):
    name: str
    num_of_students: int
    phone_number:str
    email_address:str
    apis: List[API] = []
    # courses_offered: List[Course] = []
    # batches_registered: List[Batch] = []
    courseBatchBooks_offered: List[CourseBatchBook] = []


class ClientInfo(ClientInfoBase):
    client_id: int
    is_active: bool
    class Config:
        orm_mode = True

class Client(BaseModel):
    client_id: int
    is_active: bool
    name: str
    class Config:
        orm_mode = True

# Teacher pydantic working fine!
class TeacherBase(BaseModel):
    name: str
    address : str
    email_address: str
    phone_number: str

"""
class TeacherCreate(TeacherBase):
    class Config:
        orm_mode = True

class Teacher(BaseModel):
    teacher_id:int
    name: str
    is_active: bool
    class Config:
        orm_mode = True
        arbitrary_types_allowed = True
"""
# Teacher pydantic working fine!
class GoalBase(BaseModel):
    student_name: str
    goals: str
    email_address : str

class GoalCreate(GoalBase):
    class Config:
        orm_mode = True

class Goal(BaseModel):
    goal_id:int
    student_id:int
    goals: str
    achieved: bool
    class Config:
        orm_mode = True


# Assessment pydantic working fine!
class AssessmentBase(BaseModel):
    name: str
    course_name: str
    number_of_questions: int
    assessment_type: AssessmentTypeEnum
    is_active:bool

class AssessmentCreate(AssessmentBase):
    class Config:
        orm_mode = True

class Assessment(BaseModel):
    assessment_id:int
    name: str
    course_id: str
    number_of_questions: int
    assessment_type: AssessmentTypeEnum
    is_active:bool
    class Config:
        orm_mode = True
        arbitrary_types_allowed = True


# Assessment pydantic working fine!
class AssessmentResultBase(BaseModel):
    student_name : str
    assessment_name : str
    percent : float
    improvement_areas : str
    is_active : bool

class AssessmentResultCreate(AssessmentResultBase):
    class Config:
        orm_mode = True

class AssessmentResult(BaseModel):
    assessment_result_id:int
    student_id: str
    assessment_id: str
    percent : float
    improvement_areas : str
    is_active : bool
    class Config:
        orm_mode = True
        arbitrary_types_allowed = True

class StudentsResponseCreate(BaseModel):
    question_id : int
    student_id : int
    student_answer : str
    assessment_id : int
    f1score : float
    recall : float
    emb_score : float
    is_active : bool
    class Config:
        orm_mode = True
        # arbitrary_types_allowed = True

class StudentsResponseGet(BaseModel):
    assessment_id : int
    student_id : int
    class Config:
        orm_mode = True
        arbitrary_types_allowed = True

class StudentsResponse(BaseModel):
    id : int
    question_id : int
    student_id : int
    student_answer : str
    assessment_id : int
    f1score : float
    recall : float
    emb_score : float
    is_active : bool
    class Config:
        orm_mode = True
        arbitrary_types_allowed = True

class ParagraphTrackerBase(BaseModel):
    paragraph : str
    is_active : bool

class ParagraphTrackerCreate(ParagraphTrackerBase):
    class Config:
        orm_mode = True

class ParagraphTracker(BaseModel):
    layout_id : int
    passage : str
    # is_active : bool
    class Config:
        orm_mode = True
        arbitrary_types_allowed = True


# QuestionAndAnswer pydantic working fine!
class QuestionAndAnswerBase(BaseModel):
    question : str
    question_type : QuestionTypeEnum
    answer : str
    layout_id : int
    options : str
    assessment_name : str
    is_active : bool

class QuestionAndAnswerBase2(BaseModel):
    question : str
    question_type : QuestionTypeEnum
    answer : str
    assessment_name : str
    is_active : bool

class QuestionAndAnswerCreate2(QuestionAndAnswerBase2):
    class Config:
        orm_mode = True

class QuestionAndAnswer2(BaseModel):
    id:int
    question : str
    question_type : QuestionTypeEnum
    answer : str
    assessment_id : str
    is_active : bool
    class Config:
        orm_mode = True
        arbitrary_types_allowed = True

class QuestionAndAnswerByAssessmentID(BaseModel):
    assessment_id : int

class QuestionAndAnswerByAssessmentName(BaseModel):
    assessment_name:str

class QuestionAndAnswerCreate(QuestionAndAnswerBase):
    class Config:
        orm_mode = True

class QuestionAndAnswer(BaseModel):
    id:int
    question : str
    question_type : QuestionTypeEnum
    answer : str
    layout_id : str
    options : str
    assessment_id : str
    is_active : bool
    class Config:
        orm_mode = True
        arbitrary_types_allowed = True

class verifyTeacher(BaseModel):
    email_address: str
    phone_number: str

class verifyStudent(BaseModel):
    email_address: str
    phone_number: str

class GetStudent(BaseModel):
    email_address: str
    phone_number: str

class GetStudentByID(BaseModel):
    student_id: int

class Fetch_Paragraph(BaseModel):
    student_id : int
    topic_name : str
    # passage : str

class Fetch_Topic_name(BaseModel):
    topic_name : str
    chapter_name : str
    student_id : int

class Fetch_Chapter(BaseModel):
    book_id : int
    book_name : str
    student_id : int
    chapter_name : str

class fetch_subjects(BaseModel):
    student_id : int

class Fetch_Subjects_Teacher(BaseModel):
    teacher_id : int

class StudentVirtualAvatar(BaseModel):

    student_id : int
    virtual_avatar_id : int

class TeacherVirtualAvatar(BaseModel):

    teacher_id : int
    virtual_avatar_id : int

class PreSynthesizedFillers(BaseModel):

    id : int
    link_to_presynthesized : str
    action : str
    virtual_avatar_id : int
    is_active : bool

class FetchBookName(BaseModel):
    student_id : int
    book_name : str
    subject_id : int

class FetchVirtualTeachers(BaseModel):
    student_id : int
    virtual_avatar_id : int

class TeacherStudentNorm(BaseModel):
    student_id : int
    teacher_id : int

class FetchRealTeachers(BaseModel):
    student_id : int
    teacher_id : int

class CreateBoardBase(BaseModel):
    board_name : str

class CreateBoard(CreateBoardBase):
    board_id : int
    board_name : str
    class Config:
        orm_mode = True


class CreateStandard(BaseModel):
    standard_id : int
    age : int
    level : str

class StandardResponse(BaseModel):
    standard : int

class CreateCourse(BaseModel):
    name : str
    is_active : bool
    client_name : str

class CreateCourseBase(CreateCourse):
    course_id : int
    class Config:
        orm_mode = True
        arbitrary_types_allowed = True

class CreatePost(BaseModel):
    user_name : str
    resource_url : str
    content_type : str
    caption : str
    like_count : int
    comment_count :int
    share_count : int
    view_count : int

class CreatePostBase(CreatePost):
    post_id : int
    class Config:
        orm_mode = True
        arbitrary_types_allowed = True

class CreateStories(BaseModel):
    title : str
    description : str
    name : str
    source_url : str

class CreateStoriesBase(CreateStories):
    stories_id : int
    class Config:
        orm_mode = True
        arbitrary_types_allowed = True

class CreateActivity(BaseModel):
    post_id : int
    type : str

class CreateActivityBase(CreateActivity):
    activity_id : int
    class Config:
        orm_mode = True
        arbitrary_types_allowed = True

class Like(BaseModel):
    activity_id : int
    user_name : str

class LikeBase(Like):
    like_id : int
    class Config:
        orm_mode = True
        arbitrary_types_allowed = True

class Share(BaseModel):
    activity_id : int
    user_name : str

class ShareBase(Share):
    share_id : int
    class Config:
        orm_mode = True
        arbitrary_types_allowed = True

class View(BaseModel):
    activity_id : int
    user_name : str

class ViewBase(View):
    view_id : int
    class Config:
        orm_mode = True
        arbitrary_types_allowed = True

class Command(BaseModel):
    post_id : int
    user_name : str
    text : str

class CommandBase(Command):
    comment_id : int
    class Config:
        orm_mode = True

class VirtualAvatar(BaseModel):
    name : str
    profile_pic_link : str
    audio_link : str
    description : str
    is_active : bool

class VirtualAvatarBase(VirtualAvatar):
    virtual_avatar_id : int
    class Config:
        orm_mode = True
        arbitrary_types_allowed = True


class RequestResponse(BaseModel):

    StartTime : str
    EndTime : str
    Directory : str
    FileName : str
    TextResponse : str


class CreateRequestResponse(RequestResponse):
    FileID : int
    class Config:
        orm_mode = True
        arbitrary_types_allowed = True

class Subject(BaseModel):

    subject_name : str
    batch_name : str
    student_name : str
    teacher_name : str

class CreateSubject(Subject):
    subject_id : int
    class Config:
        orm_mode = True
        arbitrary_types_allowed = True


class Layout(BaseModel):

    file_name : str
    student_name : str
    publey_flag : int
    publey_processing_time : int
    page_number : int
    layout_number : int
    num_of_bboxes_per_page : int
    passage : str
    topic_name : str
    chapter_name : str
    book_name : str

class CreateLayout(BaseModel):
    # layout_id : int
    passage : str
    class Config:
        orm_mode = True
        arbitrary_types_allowed = True

class Book(BaseModel):

    file_name : str
    student_name : str
    subject_name : str
    book_name : str
    is_active : bool

class CreateBook(Book):
    book_id : int
    class Config:
        orm_mode = True
        arbitrary_types_allowed = True

class otp(BaseModel):

    phone_number:str
    otp:str



#cartoon Images Base Model
class CartoonImages(BaseModel):
    # id:int
    image_name                         : str
    image_url                          : str
    delauney_triangulation             : str
    open_mouth                         : str
    close_mouth                        : str
    scale_shift                        : str
    is_active                          : bool
    image_bg_url                       : str
    user_id                            : int
    class Config:
        orm_mode = True
        arbitrary_types_allowed = True

class UserImages(BaseModel):
    teacher_avatar_id:int
    image_name:str
    image_url:str
    in_use:bool
    user_id:int
    upload_date:date
    class Config:
        orm_mode = True
        arbitrary_types_allowed = True