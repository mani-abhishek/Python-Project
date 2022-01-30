from datetime import datetime
from re import I, T
from sqlalchemy import Boolean, Column,Table, ForeignKey,Text, Integer, String, DateTime, Enum, Float
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.dialects.mysql.types import TINYINT
from sqlalchemy.orm import relationship
from sqlalchemy.sql.coercions import InElementImpl
from sqlalchemy.sql.expression import false, null
from sqlalchemy.sql.operators import is_commutative
from sqlalchemy.sql.schema import ForeignKeyConstraint
from sqlalchemy.sql.sqltypes import BIGINT

from .database import Base


# User is the main table
class User(Base):
    __tablename__ = "user"
    __table_args__ = {'extend_existing': True}

    user_id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String(100), nullable=False, unique=True)
    client_id = Column(String(100), nullable=False)
    client_secret = Column(String(100), nullable=False)
    email_address = Column(String(100), nullable=False, unique=True)
    role = Column(String(100), nullable=False)
    # current_grade = Column(String(100), nullable=True)
    # image_url = Column(String(255), nullable=True)
    latitude = Column(String(255), nullable=True)
    longitude = Column(String(255), nullable=True)
    varified = Column(Boolean, default=False)
    creationDate = Column(DateTime, default=datetime.now())
    is_active = Column(Boolean, default=True)
    # apis = relationship(lambda: API)

# TeacherAvatar store images which will be used in generating video an profile pic
class TeacherAvatar(Base):
    __tablename__ = "teacher_avatar"
    __table_args__ = {'extend_existing': True}
    teacher_avatar_id = Column(Integer, primary_key=True, index=True)
    image_name = Column(String(255), nullable=True)
    image_url = Column(Text,nullable=True)
    user_id = Column(Integer, ForeignKey(User.user_id))
    in_use = Column(Boolean, default=True)
    is_cartoon = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    upload_date = Column(DateTime, default=datetime.now())

# VoiceSample store voice sample of user
class VoiceSample(Base):
    __tablename__ = "voice_sample"
    voice_id = Column(Integer, primary_key=True, index=True)
    voice_sample_name = Column(String(300), nullable=True)
    voice_sample_url = Column(String(300), nullable=False)
    user_id = Column(Integer, ForeignKey(User.user_id))
    is_active = Column(Boolean, default=True)
    in_use = Column(Boolean, default=True)
    upload_date = Column(DateTime, default=datetime.now())

class Client(Base):
    __tablename__ = "client"
    __table_args__ = {'extend_existing': True}

    client_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    num_of_students = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=True)
    phone_number = Column(String(100), default=True)
    email_address = Column(String(100), default=True)
    # apis = relationship(lambda: API)
    # courses_offered = relationship(lambda: Course)
    # batches_registered = relationship(lambda: Batch)
    # students_registered = relationship(lambda: Student)


class Board(Base):
    __tablename__ = "board"
    __table_args__ = {'extend_existing': True}

    board_id = Column(Integer, primary_key=True, index=True)
    board_name = Column(String(30), nullable=False)



class Course(Base):
    __tablename__  = "course"
    __table_args__ = {'extend_existing': True}

    course_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), index=True)
    is_active = Column(Boolean, default=True)
    authorized_client_id = Column(Integer, ForeignKey(Client.client_id) )

class Standard(Base):
    __tablename__ = "standard"
    __table_args__ = {'extend_existing': True}

    standard_id = Column(Integer, primary_key=True, index=True)
    standard = Column(String(25), nullable=False)

# School table is used to store school detail
class School(Base):
    __tablename__ = "school"
    __table_args__ = {'extend_existing': True}

    school_id = Column(Integer, primary_key=True, index=True)
    school_name = Column(String(100), nullable=False)
    school_address = Column(String(100), nullable=True)
    # is_active = Column(Boolean, default=True)
    board_id = Column(Integer, ForeignKey(Board.board_id))
    affiliation_code = Column(String(100), nullable=True)
    user_id = Column(Integer, ForeignKey(User.user_id))
    creationDate = Column(DateTime, default=datetime.now())

    # students_registered = relationship(lambda: Student)


class Batch(Base):
    __tablename__  = "batch"
    __table_args__ = {'extend_existing': True}

    batch_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), index=True)
    year = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True)
    standard_id = Column(Integer, ForeignKey(Standard.standard_id))
    school_id = Column(Integer, ForeignKey(School.school_id))
    authorized_client_id = Column(Integer, ForeignKey(Client.client_id), )
    # students_registered = relationship(lambda: Student)


# Student table used to store student detail
class Student(Base):
    __tablename__ = "student"
    __table_args__ = {'extend_existing': True}

    student_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    gender = Column(String(15), nullable=False)
    dob = Column(String(20), nullable=False)
    school_id = Column(Integer, ForeignKey(School.school_id))
    batch_id = Column(Integer, ForeignKey(Batch.batch_id))
    user_id = Column(Integer, ForeignKey(User.user_id))
    favorite_teacher_id = Column(Integer, ForeignKey(TeacherAvatar.teacher_avatar_id))
    # is_active = Column(Boolean, default=True)
    # email_address = Column(String(35), nullable=False, unique=True)
    # phone_number = Column(String(13), nullable=False, unique=True)
    who_pays_for_course = Column(String(50), nullable=True)
    english_proficiency = Column(String(50), nullable=False)
    preferred_language = Column(String(25), nullable=False)
    created_date = Column(DateTime, default=datetime.now())

# Teacher table used to store teacher detail
class Teacher(Base):
    __tablename__ = "teacher"
    __table_args__ = {'extend_existing': True}

    teacher_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(25), nullable=False)
    address = Column(String(100), nullable=False)
    school_id = Column(Integer, ForeignKey(School.school_id))
    # authorized_client_id = Column(Integer, ForeignKey(Client.client_id))
    course_id = Column(Integer, ForeignKey(Course.course_id))
    # is_active = Column(Integer, default=True)
    # email_address = Column(String(35), unique=True)
    # phone_number = Column(String(15), unique=True)
    user_id = Column(Integer, ForeignKey(User.user_id))
    created_date = Column(DateTime, default=datetime.now())

class Business_Signup(Base):
    __tablename__ = "business"
    __table_args__ = {'extend_existing': True}

    business_id = Column(Integer, nullable=False, primary_key=True)
    name = Column(String(50), nullable=False)
    email = Column(String(35), nullable=False)
    no_of_students =Column(Integer, nullable=False)

class API(Base):
    __tablename__  = "api"
    __table_args__ = {'extend_existing': True}

    api_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), index=True)
    end_point = Column(String(512), nullable = True )
    is_active = Column(Boolean, default=True)
    authorized_client_id = Column(Integer, ForeignKey(Client.client_id), )
    authorized_user_id = Column(Integer, ForeignKey(User.user_id), )



class BatchCourseNormalization(Base):
    __tablename__ = "batch_course_normalization"
    __table_args__ = {'extend_existing': True}

    batch_course_id =  Column(Integer, primary_key=True, index=True)
    batch_id = Column(Integer, ForeignKey(Batch.batch_id))
    course_id = Column(Integer, ForeignKey(Course.course_id))



class HertzOcrRequestResponse(Base):
    __tablename__ = "hertz_ocr_req_res_table"
    __table_args__ = {'extend_existing': True}

    FileID = Column(Integer, primary_key=True, autoincrement = True)
    StartTime = Column(DateTime, nullable=False)
    EndTime = Column(DateTime, nullable=True)
    Directory = Column(String(30), nullable=False)
    FileName = Column(String(50), nullable=False)
    TextResponse = Column(LONGTEXT, nullable=True)

class Subject(Base):
    __tablename__ = "subject"
    __table_args__ = {'extend_existing': True}

    # add FK book

    subject_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(25), nullable=False)
    # book_id = Column(Integer, ForeignKey(Book.book_id))
    batch_id = Column(Integer, ForeignKey(Batch.batch_id))
    student_id = Column(Integer, ForeignKey(Student.student_id))
    teacher_id = Column(Integer, ForeignKey(Teacher.teacher_id))


class Book(Base):
    __tablename__ = "book"
    __table_args__ = {'extend_existing': True}

    book_id =  Column(Integer, primary_key=True, index=True)
    subject_id = Column(Integer, ForeignKey(Subject.subject_id))
    student_id = Column(Integer, ForeignKey(Student.student_id))
    name = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True)
    file_id = Column(Integer, ForeignKey(HertzOcrRequestResponse.FileID))



class Layout(Base):
    __tablename__ = "layout"
    __table_args__ = {'extend_existing': True}

    file_id = Column(Integer, ForeignKey(HertzOcrRequestResponse.FileID))
    student_id = Column(Integer, ForeignKey(Student.student_id))
    publey_flag = Column(TINYINT, nullable=False)
    publey_processing_time = Column(BIGINT, nullable=True)
    Page_number = Column(Integer, nullable = False)
    Layout_number = Column(Integer, nullable=True)
    num_of_bboxes_per_page = Column(Integer, nullable=True)
    passage = Column(LONGTEXT, nullable=True)
    layout_id = Column(Integer, primary_key=True, index=True)
    # LayoutPrimaryId = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    topic_name = Column(String(50), nullable=False)
    chapter_name = Column(String(50), nullable=False)
    book_id = Column(Integer, ForeignKey(Book.book_id))

class Assessment(Base):
    __tablename__ = "assessment"
    __table_args__ = {'extend_existing': True}

    assessment_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True)
    course_id = Column(Integer, ForeignKey(Course.course_id))
    number_of_questions = Column(Integer, nullable=False)
    assessment_type = Column(Enum('MCQ', 'MOCK_INTERVIEW', 'LONGFORM_QA', 'CONVERSATION_FOR_IMPROVING_ENGLISH', 'REVISION'), nullable=False)
    is_active = Column(Boolean, default=True)
    layout_id = Column(Integer, ForeignKey(Layout.layout_id))

class AssessmentResult(Base):
    __tablename__ = "assessment_result"
    __table_args__ = {'extend_existing': True}

    assessment_result_id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey(Student.student_id))
    assessment_id = Column(Integer, ForeignKey(Assessment.assessment_id))
    percent = Column(Float, nullable=False, default=0.0)
    improvement_areas = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True)

class QuestionAndAnswer(Base):
    __tablename__ = "question_and_answer"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    layout_id = Column(Integer, ForeignKey(Layout.layout_id))
    question = Column(String(1000), nullable=False)
    question_type = Column(Enum('MCQ', 'OBJECTIVE'), nullable=False)
    # para_id = Column(Integer,ForeignKey(Paragraphs.id),nullable=False)
    options = Column(String(1000),default="[]")
    answer = Column(String(1000))
    is_active = Column(Boolean, default=True)
    assessment_id = Column(Integer, ForeignKey(Assessment.assessment_id), default=6)
    # LayoutPrimaryId = Column(Integer, ForeignKey(Layout.LayoutPrimaryId))


class BookCourseNormalized(Base):
    __tablename__ = "book_course_normalized"
    __table_args__ = {'extend_existing': True}

    book_course_id =  Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey(Book.book_id))
    course_id = Column(Integer, ForeignKey(Course.course_id))

class ClientTeacherCourse(Base):
    __tablename__ = "client_teacher_course_normalized"
    __table_args__ = {'extend_existing': True}

    client_teacher_course_id =  Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey(Client.client_id))
    teacher_id = Column(Integer, ForeignKey(Teacher.teacher_id))
    course_id = Column(Integer, ForeignKey(Course.course_id))


class Conversation(Base):
    __tablename__ = "conversation"
    __table_args__ = {'extend_existing': True}

    conv_id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    timestamp = Column(DateTime, nullable=False)
    user_id = Column(Integer, ForeignKey(User.user_id), )
    request = Column(LONGTEXT, nullable = True)
    response = Column(LONGTEXT, nullable = True)
    conv_bot_name = Column(Enum('GPT3', 'RASA', 'BLENDER', 'ALBERT'), )

class Goal(Base):
    __tablename__ = "goal"
    __table_args__ = {'extend_existing': True}

    goal_id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey(Student.student_id))
    goals = Column(String(500),nullable=False)
    achieved = Column(Float, nullable=False, default=0.0)

class NLPresults(Base):
    __tablename__ = "nlp_results_table"
    __table_args__ = {'extend_existing': True}

    req_id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(Text,nullable=True)
    req_module = Column(String(255), nullable=True)
    startTime = Column(DateTime, nullable=False)
    endTime = Column(DateTime, nullable=True)
    refresh_flag = Column(TINYINT, nullable=False)
    enable_flag = Column(TINYINT, nullable=False)
    disable_flag = Column(TINYINT, nullable=False)
    folder_path = Column(String(50), nullable=False)
    response_text = Column(LONGTEXT, nullable=True)

class ObjDeResults(Base):
    __tablename__ = "obj_det_results"
    __table_args__ = {'extend_existing': True}

    file_id = Column(Integer, primary_key=True, autoincrement=True)
    img_path = Column(String(255), nullable=True)
    mask_image_path = Column(String(255), nullable=True)
    crop_image_path = Column(String(255), nullable=True)
    car_color = Column(String(255), nullable=True)
    reg_num_color = Column(String(255), nullable=True)
    response = Column(LONGTEXT, nullable=True)

class PubleyPixelCRNN(Base):
    __tablename__ = "publey_pixel_crnn_table"
    __table_args__ = {'extend_existing': True}

    publey_id = Column(Integer, primary_key=True, autoincrement=True)
    file_id = Column(Integer, ForeignKey(HertzOcrRequestResponse.FileID))
    publey_flag = Column(TINYINT, nullable=False)
    publey_processing_time = Column(Integer, nullable=True)
    pixel_processing_time = Column(Integer, nullable=True)
    crnn_processing_time = Column(Integer, nullable=True)
    Page_number = Column(Integer, nullable=False)
    Layout_number = Column(Integer, nullable=True)
    num_of_bboxes_per_page = Column(Integer, nullable=True)
    num_of_bboxes_per_layout = Column(Integer, nullable=True)
    car_color = Column(String(100), nullable=True)
    registration_no = Column(String(100), nullable=True)
    passage = Column(String(100), nullable=True)
    object_no = Column(Integer, nullable=True)
    object_name = Column(String(20), nullable=True)
    detectron = Column(Integer, nullable=True)

class Random(Base):
    __tablename__ = "random"
    __table_args__ = {'extend_existing': True}

    batch_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    name2 = Column(String(100), nullable=True)
    client_id = Column(Integer, nullable=False)
    client_id2 = Column(Integer, nullable=True)




class StudentsAnswer(Base):
    __tablename__= "students_answer"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key = True, index = True)
    question_id = Column(Integer,ForeignKey(QuestionAndAnswer.id))
    student_id = Column(Integer,ForeignKey(Student.student_id))
    student_answer = Column(String(1000))
    assessment_id = Column(Integer,ForeignKey(Assessment.assessment_id))
    f1score = Column(Float,nullable=False,default = 0.0)
    recall = Column(Float,nullable=False,default = 0.0)
    emb_score = Column(Float,nullable=False,default= 0.0)
    is_active = Column(Boolean,default = True)


class UserInfo(Base):
    __tablename__ = "user_info"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True)
    password = Column(String(50))
    fullname = Column(String(50), unique=True)

class Chapter(Base):
    __tablename__ = "chapter"
    __table_args__ = {'extend_existing': True}

    chapter_id = Column(Integer, primary_key=True, index=True)
    chapter_name = Column(String(25), nullable=False)
    school_id = Column(Integer, ForeignKey(School.school_id))



class Section(Base):
    __tablename__ = "section"
    __table_args__ = {'extend_existing': True}

    section_id = Column(Integer, primary_key=True, index=True)
    section_name = Column(String(25), nullable=False)
    batch_id = Column(Integer, ForeignKey(Batch.batch_id))

class VirtualAvatar(Base):
    __tablename__ = "virtual_avatar"
    __table_args__ = {'extend_existing': True}

    virtual_avatar_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    profile_pic_link = Column(String(255), nullable=False)
    audio_link = Column(String(255), nullable=False)
    description = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)

class StudentVirtualAvatar(Base):
    __tablename__ = "student_virtual_avatar"
    __table_args__ = {'extend_existing': True}

    student_virtual_avatar_id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey(Student.student_id))
    virtual_avatar_id = Column(Integer, ForeignKey(VirtualAvatar.virtual_avatar_id))


class TeacherVirtualAvatar(Base):
    __tablename__ = "teacher_virtual_avatar"
    __table_args__ = {'extend_existing': True}

    teacher_virtual_avatar_id = Column(Integer, primary_key=True)
    teacher_id = Column(Integer, ForeignKey(Teacher.teacher_id))
    virtual_avatar_id = Column(Integer, ForeignKey(VirtualAvatar.virtual_avatar_id))

class TeacherStudentNorm(Base):
    __tablename__ = "teacher_student_normalization"
    __table_args__ = {'extend_existing': True}

    teacher_student_id = Column(Integer, primary_key=True)
    teacher_id = Column(Integer, ForeignKey(Teacher.teacher_id))
    student_id = Column(Integer, ForeignKey(Student.student_id))

class PresynthesizedFillers(Base):
    __tablename__ = "pre_synthesized_fillers"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    link_to_presynthesized = Column(String(255), nullable=False)
    action = Column(String(255), nullable=False)
    virtual_avatar_id = Column(Integer, ForeignKey(VirtualAvatar.virtual_avatar_id))
    is_active = Column(Boolean, default=False)


class Post(Base):
    __tablename__ = "post"
    __table_args__ = {'extend_existing': True}

    post_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey(User.user_id))
    resource_url = Column(String(255), nullable=False)
    content_type = Column(String(50), nullable=False)
    caption = Column(String(50), nullable=False)
    creationDate = Column(DateTime, nullable=False)
    like_count = Column(Integer, nullable=False)
    comment_count = Column(Integer, nullable=False)
    share_count = Column(Integer, nullable=False)
    view_count = Column(Integer, nullable=False)


class Stories(Base):
    __tablename__ = "stories"
    __table_args__ = {'extend_existing': True}

    stories_id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    description = Column(String(255), nullable=False)
    teacher_id = Column(Integer, ForeignKey(Teacher.teacher_id))
    source_url = Column(String(255), nullable=False)
    creationDate = Column(DateTime, nullable=False)


class Activity(Base):
    __tablename__ = "activity"
    __table_args__ = {'extend_existing': True}

    post_id = Column(Integer, ForeignKey(Post.post_id))
    activity_id = Column(Integer, primary_key=True, index=True)
    type = Column(String(50), nullable=False)
    creationDate = Column(DateTime, nullable=False)

class Like(Base):
    __tablename__ = "like"
    __table_args__ = {'extend_existing': True}

    like_id = Column(Integer, primary_key=True, index=True)
    activity_id = Column(Integer, ForeignKey(Activity.activity_id))
    user_id = Column(Integer, ForeignKey(User.user_id))
    creationDate = Column(DateTime, nullable=False)

class Comment(Base):
    __tablename__ = "comment"
    __table_args__ = {'extend_existing': True}

    comment_id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey(Post.post_id))
    user_id = Column(Integer, ForeignKey(User.user_id))
    text = Column(String(255), nullable=False)
    creationDate = Column(DateTime, nullable=False)

class Share(Base):
    __tablename__ = "share"
    __table_args__ = {'extend_existing': True}

    share_id = Column(Integer, primary_key=True, index=True)
    activity_id = Column(Integer, ForeignKey(Activity.activity_id))
    user_id = Column(Integer, ForeignKey(User.user_id))
    creationDate = Column(DateTime, nullable=False)

class View(Base):
    __tablename__ = "view"
    __table_args__ = {'extend_existing': True}

    view_id = Column(Integer, primary_key=True, index=True)
    activity_id = Column(Integer, ForeignKey(Activity.activity_id))
    user_id = Column(Integer, ForeignKey(User.user_id))
    creationDate = Column(DateTime, nullable=False)


class Otp(Base):
    __tablename__ = "OTP"

    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String(13), nullable=False)
    otp = Column(String(4), nullable=False)
    user_id = Column(Integer, ForeignKey(User.user_id))
    created_date = Column(DateTime, default=datetime.now())


class AddUser(Base):
    __tablename__ = "AddUser"

    id = Column(Integer, primary_key=True, index=True)
    organisation_user_id = Column(Integer, ForeignKey(User.user_id))
    user_id = Column(Integer, ForeignKey(User.user_id))
    created_date = Column(DateTime, default=datetime.now())



#Catoon Images Database Model
class CartoonImages(Base):
    __tablename__= "CartoonImages"
    __table_args__ = {'extend_existing': True}

    cartoon_id                = Column(Integer,primary_key=True,index=True)
    image_name                = Column(String(255), nullable=False)
    image_url                 = Column(String(255), unique=True,nullable=False)
    delauney_triangulation    = Column(String(255), nullable=False)
    open_mouth                = Column(String(255), nullable=False)
    close_mouth               = Column(String(255), nullable=False)
    scale_shift               = Column(String(255),nullable=True)
    is_active                 = Column(Boolean,unique=False, default=True)
    uploaded_date             = Column(DateTime, default=datetime.now())
    image_bg_url              = Column(String(255), nullable=False)
    user_id                   = Column(Integer, ForeignKey(User.user_id))









