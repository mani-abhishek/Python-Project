from typing import Optional
from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from typing import List
from fastapi import Depends, FastAPI, HTTPException, Request, Response
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from datetime import datetime
from fastapi.openapi.utils import get_openapi
from sqlalchemy import DDL
from starlette.routing import request_response
# from sql.models import API

#Docker
# from app.sql import crud, models, schemas, otp
# from app.sql.database import SessionLocal, engine

#Local
from sql import crud, models, schemas,otp
from sql.database import SessionLocal, engine


DATABASE_URL = "mysql://stbitdbuser:9cAxIccp+p*vPJsA@localhost:3306/sudharsan"
# database = database.Database(DATABASE_URL)

models.Base.metadata.create_all(bind=engine)

tags_metadata = [
    {
        "name": "Ping",
        "description": "Get Hevovle-db-app status.",
    },
    {
        "name": "Students",
        "description": "CRUD Ops with Students..",
    },
    {
        "name": "Clients",
        "description": "CRUD Ops with Clients",
        # "externalDocs": {
        #     "description": "Items external docs",
        #     "url": "https://fastapi.tiangolo.com/",
        # },
    },
    {
        "name": "APIs",
        "description": "CRUD Ops with Assessment, Interview, Conversational, Revision APIs ",
    },
    {
        "name": "Schools",
        "descrition": "Crud ops with Schools"
    },
    {
        "name": "Batches",
        "descrition": "Crud ops with Batches"
    },
    {
        "name": "Users",
        "descrition": "Crud ops with Users"
    }
]
controller = FastAPI(
    title="Hevolve-db-app",
    description="This is Hevolve-db-app with auto docs for the API and everything",
    version="1.0",
    openapi_tags=tags_metadata,
)

controller.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    #allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# @controller.post("/register_student", tags=["Student"], response_model=schemas.StudentCreate)
@controller.post("/register_student", tags=["Student"])
def CreateStudent(student: schemas.Student, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_phone_number(db, phone_number=student.phone_number)
    if db_user:
        raise HTTPException(status_code=400, detail="phone number already registered. Please login")

    db_user = crud.get_user_by_email_address(db, email_address=student.email_address)
    if db_user:
        raise HTTPException(status_code=400, detail="Email id is already registered. Please login")

    return crud.register_student(db=db, student= student)


# @controller.post("/register_teacher", tags=["Teacher"], response_model=schemas.TeacherCreate)
@controller.post("/register_teacher", tags=["Teacher"])
def RegisterTeacher(teacher: schemas.TeacherBase, db: Session = Depends(get_db)):
    # db_user = crud.get_teacher_by_name(db, name=teacher.name)
    # if db_user:
    #     raise HTTPException(status_code=400, detail="Teacher already registered")

    db_user = crud.get_user_by_phone_number(db, phone_number=teacher.phone_number)
    if db_user:
        raise HTTPException(status_code=400, detail="phone number already registered. Please login")

    db_user = crud.get_user_by_email_address(db, email_address=teacher.email_address)
    if db_user:
        raise HTTPException(status_code=400, detail="Email id is already registered. Please login")
    return crud.register_teacher(db=db, teacher= teacher)

@controller.post("/createclient", tags=["Clients"], response_model=schemas.ClientInfo)
def create_client(client: schemas.ClientInfoBase, db: Session = Depends(get_db)):
    db_user = crud.get_client_by_name(db, name=client.name)
    if db_user:
        raise HTTPException(status_code=400, detail="Client already registered")
    return crud.create_client(db=db, client=client)


# @controller.post("/registerschool", tags=["Schools"],response_model=schemas.SchoolCreate)
@controller.post("/registerschool", tags=["Schools"])
def register_school(school: schemas.SchoolBase, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_phone_number(db, phone_number=school.phone_number)
    if db_user:
        raise HTTPException(status_code=400, detail="phone number already registered. Please login")

    db_user = crud.get_user_by_email_address(db, email_address=school.email_address)
    if db_user:
        raise HTTPException(status_code=400, detail="Email id is already registered. Please login")
    return crud.register_school(db=db, school=school)

@controller.post("/createbatch", tags=["Batches"],response_model=schemas.BatchCreate)
def create_batch(batch: schemas.BatchBase, db: Session = Depends(get_db)):
    db_user = crud.get_batch_by_name(db, name=batch.name)
    if db_user:
        raise HTTPException(status_code=400, detail="Batch already registered")
    return crud.create_batch(db=db, batch=batch)

@controller.post("/create_business_signup", tags=["business_Signup"], response_model=schemas.Business_Signup_base)
def CreateBusinessSignup(business: schemas.Business_Signup, db: Session = Depends(get_db)):
    db_user = crud.get_business(db, name=business.name)
    if db_user:
        raise HTTPException(status_code=400, detail="Business ID already registered")
    return crud.create_business_signup(db=db, business_signup= business)


@controller.post("/fetch_paragraph_topic_name_and_studentid", tags=["Fetch_Paragraph"], response_model=schemas.Fetch_Paragraph)
def Fetch_Paragraph_by_topic_name_student_id(layout: schemas.Fetch_Paragraph, db: Session = Depends(get_db)):
    # Find student by email or phone number
    db_user = crud.fetch_paragraph_topic_name_and_studentid(db, topic_name = layout.topic_name, student_id=layout.student_id)
    if db_user == None:
        raise HTTPException(status_code=400, detail="No student found")
    return db_user

@controller.post("/fetch_topic_student_id_chapter_name", tags=["Fetch_Topics"], response_model=schemas.Fetch_Topic_name)
def Fetch_topic_by_student_id_chapter_name(layout: schemas.Fetch_Topic_name, db: Session = Depends(get_db)):
    # Find student by email or phone number
    db_user = crud.fetch_topics_student_id_chapter_name(db, chapter_name = layout.chapter_name, student_id=layout.student_id)
    if db_user == None:
        raise HTTPException(status_code=400, detail="No student found")
    return db_user

@controller.post("/fetch_chapter_bookname_studentid", tags=["Fetch_Chapter"], response_model=schemas.Fetch_Chapter)
def Fetch_chapter_bookname_studentid(layout: schemas.Fetch_Chapter, db: Session = Depends(get_db)):
    # Find student by email or phone number
    db_user = crud.fetch_chapter_bookname_studentid(db, book_id = layout.book_id, student_id=layout.student_id)
    if db_user == None:
        raise HTTPException(status_code=400, detail="No student found")
    return db_user

@controller.post("/fetch_subjects", tags=["Fetch_subjects"], response_model=schemas.fetch_subjects)
def Fetch_subjects_studentid(subject: schemas.fetch_subjects, db: Session = Depends(get_db)):
    # Find student by email or phone number
    db_user = crud.fetch_subjects(db, student_id=subject.student_id)
    if db_user == None:
        raise HTTPException(status_code=400, detail="No student found")
    return db_user

@controller.post("/fetch_subjects_teacher_id", tags=["Fetch_subjects_teacher_id"], response_model=schemas.Fetch_Subjects_Teacher)
def Fetch_subjects_teacher_id(subject: schemas.Fetch_Subjects_Teacher, db: Session = Depends(get_db)):
    # Find student by email or phone number
    db_user = crud.fetch_subjects_teacher_id(db, teacher_id =subject.teacher_id)
    if db_user == None:
        raise HTTPException(status_code=400, detail="No student found")
    return db_user

@controller.post("/fetch_book_name_student_id_subject", tags=["fetch_book_name_student_id_subject"], response_model=schemas.FetchBookName)
def Fetch_book_name_student_id_subject(book: schemas.FetchBookName, db: Session = Depends(get_db)):
    # Find student by email or phone number
    db_user = crud.fetch_book_name_student_id_subject(db, student_id = book.student_id , subject_id = book.subject_id)
    if db_user == None:
        raise HTTPException(status_code=400, detail="No student found")
    return db_user

@controller.post("/virtual_teachers_student_id", tags=["virtual_teachers_student_id"], response_model=schemas.FetchVirtualTeachers)
def Fetch_virtual_teachers_student_id(virtual_avatar: schemas.FetchVirtualTeachers, db: Session = Depends(get_db)):
    # Find student by email or phone number
    db_user = crud.virtual_teachers_student_id(db, student_id = virtual_avatar.student_id , virtual_avatar_id = virtual_avatar.virtual_avatar_id)
    if db_user == None:
        raise HTTPException(status_code=400, detail="No student found")
    return db_user

@controller.post("/real_teachers_student_id", tags=["real_teachers_student_id"], response_model=schemas.FetchRealTeachers)
def Fetch_Real_teachers_student_id(Student_Teacher: schemas.FetchRealTeachers, db: Session = Depends(get_db)):
    # Find student by email or phone number
    db_user = crud.real_teachers_student_id(db, student_id = Student_Teacher.student_id , teacher_id = Student_Teacher.teacher_id)
    if db_user == None:
        raise HTTPException(status_code=400, detail="No student found")
    return db_user

@controller.get("/", tags=['Ping'])
def PingAPI():
    return "Hevolve-db-app is listening !"

@controller.post("/update_fav_teacher_avatar", tags=["Students"])
def update_student_fav_teacher_avatar(request: schemas.UpdateFavouriteTeacher, db: Session = Depends(get_db)):
    # !! NO NEED TO RESTRICT STUDENT JUST BY NAME, WE ARE DOING WITH (EMAIL + PHONEnUM)
    # db_user = crud.get_student_by_studentname(db, studentname=student.name)
    # if db_user:
    #     raise HTTPException(status_code=400, detail="Student already registered")
    return crud.update_student_fav_teacher_avatar(db=db, student_id=request.student_id, favourite_teacher_id=request.favourite_teacher_id)

@controller.post("/getstudent_by_email_or_phone_num", tags=["Students"], response_model=schemas.BasicStudentInfo)
def getstudent_by_email_or_phone_num(student: schemas.GetStudent, db: Session = Depends(get_db)):
    # Find student by email or phone number
    db_user = crud.get_student_by_email_or_phone_num(db, email_address=student.email_address, phone_number=student.phone_number)
    if db_user == None:
        raise HTTPException(status_code=400, detail="No student found")
    return db_user

@controller.post("/getstudent_by_id", tags=["Students"], response_model=schemas.BasicStudentInfo)
def getstudent_by_id(student: schemas.GetStudentByID, db: Session = Depends(get_db)):
    # Find student by email or phone number
    db_user = crud.get_student_by_id(db, student_id=student.student_id)
    if db_user == None:
        raise HTTPException(status_code=400, detail="No student found with id : " + str(student.student_id))
    return db_user

@controller.get("/allstudents", tags=["Students"],response_model=List[schemas.LimitedStudentInfo])
def get_all_students(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    requests = crud.get_all_students(db, skip=skip, limit=limit)
    return requests

@controller.get("/all_teacher_avatars", tags=["Students"])
def get_all_teacher_avatars(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    requests = crud.get_all_teacher_avatars(db, skip=skip, limit=limit)
    return requests

@controller.post("/createapi", tags=["APIs"],response_model=schemas.APICreate)
def create_api(api: schemas.APIBase, db: Session = Depends(get_db)):
    db_user = crud.get_api_by_name(db, name=api.name)
    if db_user:
        raise HTTPException(status_code=400, detail="API already registered")
    return crud.create_api(db=db, api=api)

@controller.get("/allAPIs", tags=["APIs"])
def get_all_apis(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    requests = crud.get_all_apis(db, skip=skip, limit=limit)
    return requests

# @controller.get("/allclients", response_model=List[schemas.ClientInfo])
# def get_all_clients(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
#     requests = crud.get_all_clients(db, skip=skip, limit=limit)
#     print("Crossed get_all_clients() method!")
#     return requests

@controller.get("/allclients", tags=["Clients"],response_model=List[schemas.Client])
def get_all_clients(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    requests = crud.get_all_clients(db, skip=skip, limit=limit)
    return requests

@controller.get("/allschools", tags=["Schools"],response_model=List[schemas.School])
def get_all_schools(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    requests = crud.get_all_schools(db, skip=skip, limit=limit)
    print("THe schools are fetched in main file -> ", requests)
    return requests

@controller.get("/allbatches", tags=["Batches"],response_model=List[schemas.Batch])
def get_all_batches(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    requests = crud.get_all_batches(db, skip=skip, limit=limit)
    print("The batches are fetched in main file -> ", requests)
    return requests

@controller.get("/allteachers", tags=["Teachers"],response_model=List[schemas.Teacher])
def get_all_batches(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    requests = crud.get_all_teachers(db, skip=skip, limit=limit)
    print("The Teachers are fetched in main file -> ", requests)
    return requests

@controller.post("/creategoal", tags=["Goals"],response_model=schemas.GoalCreate)
def create_goal(goal: schemas.GoalBase, db: Session = Depends(get_db)):
    db_goal = crud.get_goals_by_student_id(db, student_name=goal.student_name, email_address=goal.email_address)
    if db_goal:
        raise HTTPException(status_code=400, detail="Goal is already set for " + goal.student_name + "with email_address " + goal.email_address)
    return crud.create_goal(db=db, goal=goal)

@controller.get("/allgoals", tags=["Goals"],response_model=List[schemas.Goal])
def get_all_goals(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    requests = crud.get_all_goals(db, skip=skip, limit=limit)
    print("Goals are fetched in main file -> ", requests)
    return requests

@controller.post("/createassessment", tags=["Assessments"],response_model=schemas.AssessmentCreate)
def create_assessment(assessment: schemas.AssessmentBase, db: Session = Depends(get_db)):
    db_assessment = crud.get_assessments_by_name(db, name=assessment.name)
    if db_assessment:
        raise HTTPException(status_code=400, detail="assessment is already created with name " + assessment.name)
    return crud.create_assessment(db=db, assessment=assessment)

@controller.get("/allassessments", tags=["Assessments"],response_model=List[schemas.Assessment])
def get_all_assessments(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    requests = crud.get_all_assessments(db, skip=skip, limit=limit)
    print("Assessments are fetched in main file -> ", requests)
    return requests

@controller.post("/create_assessment_result", tags=["Assessment Results"],response_model=schemas.AssessmentResultCreate)
def create_assessment_result(assessment_result: schemas.AssessmentResultBase, db: Session = Depends(get_db)):
    db_assessment_result = crud.get_assessmentResults_by_student_name_and_assessment_name(db, assessment_result=assessment_result)
    if db_assessment_result:
        raise HTTPException(status_code=400, detail="assessment result is already created with student '" + assessment_result.student_name + "' and assessment '"+ assessment_result.assessment_name +"'")
    return crud.create_assessment_result(db=db, assessment_result=assessment_result)

@controller.get("/all_assessment_results", tags=["Assessment Results"],response_model=List[schemas.AssessmentResult])
def get_all_assessment_results(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    requests = crud.get_all_assessment_results(db, skip=skip, limit=limit)
    print("Assessment Results fetched in main file -> ", requests)
    return requests

# @controller.post("/create_question_answers", tags=["Question and Answers"],response_model=schemas.QuestionAndAnswerCreate)
@controller.post("/create_question_answers", tags=["Question and Answers"])
def create_assessment_result(question_answer: schemas.QuestionAndAnswerBase, db: Session = Depends(get_db)):
    # db_assessment_result = crud.get_question_answers_by_assessment_name(db, assessment_name=question_answer.assessment_name)
    # if db_assessment_result:
    #     raise HTTPException(status_code=400, detail="Question and Answers are already created for assessment '"+ question_answer.assessment_name +"'")
    return crud.create_question_answers(db=db, question_answer=question_answer)

@controller.post("/create_paragraph_tracker", tags=["Question and Answers"],response_model=schemas.ParagraphTracker)
def create_paragraph_tracker(paragraph_tracker: schemas.ParagraphTrackerBase, db: Session = Depends(get_db)):
    # par_id = crud.get_paragraph_by_para_id(db,paragraph_tracker = paragraph_tracker)
    # if par_id:
    #     raise HTTPException(status_code=400, detail="para_id already allocated , try with new one")
    return crud.create_paragraphs_tracker(db=db, paragraph_tracker=paragraph_tracker)

@controller.get("/all_paragraphs", tags=["Question and Answers"],response_model=List[schemas.ParagraphTracker])
def get_all_paragraph(db: Session = Depends(get_db)):
    print("entered get all paragraphs")
    requests = crud.get_all_paragraphs(db)
    # print("Assessment Results fetched in main file -> ", requests)
    return requests

@controller.get("/all_question_answers", tags=["Question and Answers"])
def get_all_question_answers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    requests = crud.get_all_question_answers(db, skip=skip, limit=limit)
    print("All question_answers fetched in main file -> ", requests)
    return requests

# @controller.get("/all_question_answers_by_assessmentid/{id}", tags=["Question and Answers"],response_model=List[schemas.QuestionAndAnswer])
# def get_all_question_answers_by_assessment(question_answer: schemas.QuestionAndAnswerByAssessmentID,db: Session = Depends(get_db)):
#     requests = crud.get_question_answers_by_assessment_id(db,question_answer=question_answer)
#     print("All question_answers fetched in main file -> ", requests)
#     return requests

@controller.get("/all_question_answers_by_assessmentid/{id}", tags=["Question and Answers"],response_model=List[schemas.QuestionAndAnswer])
def get_all_question_answers_by_assessment(id : int,db: Session = Depends(get_db)):
    requests = crud.get_question_answers_by_assessment_id(db, id = id)
    print("All question_answers fetched in main file -> ", requests)
    return requests

# @controller.post("/get_all_QAs_by_assessment_name", tags=["Question and Answers"],response_model=List[schemas.QuestionAndAnswer])
@controller.get("/get_all_QAs_by_assessment_name/{assesment_name}", tags=["Question and Answers"])
def get_all_QAs_by_assessment_name(assessment_name:str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    db_assessment = crud.get_assessments_by_name(db, name=assessment_name)
    if db_assessment == None:
        raise HTTPException(status_code=400, detail="assessment name is not valid, or not created yet")
    # duplicate method get_question_answers_by_assessment_id
    requests = crud.get_all_question_answers_by_assessment_id(db, assessment_id=db_assessment.assessment_id, skip=skip, limit=limit)
    print("All question_answers fetched in main file  -> ", requests)
    if len(requests) == 0:
        #raise HTTPException(status_code=204, detail="No questions created for '" + assessment_name + "'")
        return Response(status_code=204)
    return requests

@controller.post("/put_students_response", tags=["Assessment Results"],response_model=schemas.StudentsResponse)
def put_student_response(student_response: schemas.StudentsResponseCreate, db: Session = Depends(get_db)):
    # db_assessment_result = crud.get_assessmentResults_by_student_name_and_assessment_name(db, assessment_result=assessment_result)
    # if db_assessment_result:
    #     raise HTTPException(status_code=400, detail="assessment result is already created with student '" + assessment_result.student_name + "' and assessment '"+ assessment_result.assessment_name +"'")
    return crud.put_student_answer(db=db, student_response=student_response)

@controller.get("/get_students_answer_by_assessmentid_and_studentid", tags=["Assessment Results"],response_model=List[schemas.StudentsResponse])
def get_students_answer(student_response: schemas.StudentsResponseGet,db: Session = Depends(get_db)):
    requests = crud.get_students_answer_by_assessmentid_and_studentid(student_response,db)
    # print("Assessment Results fetched in main file -> ", requests)
    return requests

@controller.post("/updateQA/{qid}", tags=["Question and Answers"], response_model=schemas.QuestionAndAnswer2)
def update_QA(qid: int, question_answer:schemas.QuestionAndAnswerCreate2, db: Session = Depends(get_db)):
    db_updated_qa = crud.update_question_answers(db=db, qid=qid, question_answer=question_answer)
    return db_updated_qa

## below 2 endpoints will be used at teacher/student signin
@controller.post("/verifyTeacher", tags=["Teachers"])
def verify_teacher(teacher: schemas.verifyTeacher, db: Session = Depends(get_db)):
    db_user = crud.verify_teacher(db, email_address=teacher.email_address, phone_number=teacher.phone_number)
    if db_user:
        return True
    else:
        return False

@controller.post("/verifyStudent", tags=["Students"])
def verify_student(student: schemas.verifyStudent, db: Session = Depends(get_db)):
    db_user = crud.verify_student(db, email_address=student.email_address, phone_number=student.phone_number)
    if db_user:
        return True
    else:
        return False

@controller.post("/createuser", tags=["Users"])
def create_user(user: schemas.UserBase, db: Session = Depends(get_db)):
    return crud.create_user(db=db, user=user)

@controller.get("/allusers", tags=["Users"])
def get_all_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    requests = crud.get_all_users(db, skip=skip, limit=limit)
    return requests

@controller.post("/conversation", tags=["Users"])
def save_conversation(conv: schemas.Conversation, db: Session = Depends(get_db)):
    return crud.save_conversation(db=db, conv=conv)

@controller.get("/allconversations", tags=["Users"])
def get_all_conversations(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    requests = crud.get_all_conversations(db, skip=skip, limit=limit)
    return requests

@controller.get("/recentconversations/{mins}", tags=["Users"])
def get_recentconversations(mins, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    print("mins", mins)
    requests = crud.get_recentconversations(db, mins, skip=skip, limit=limit)
    return requests

@controller.post("/createboard", tags=["board"], response_model=schemas.CreateBoard)
def create_board(board: schemas.CreateBoard, db: Session = Depends(get_db)):
    # db_user = crud.get_board_by_name(db, name=board.board_name)
    # if db_user:
    #     raise HTTPException(status_code=400, detail="School already registered")
    return crud.create_board(db=db, board=board)

@controller.post("/create_standard", tags=["standard"])
def create_standard(create_standard: schemas.CreateStandard, db: Session = Depends(get_db)):

    return crud.create_standard(db=db, create_standard = create_standard)


@controller.post("/upload_teacher_avatar", tags=["Teacher Avatar"],response_model=schemas.TeacherAvatarResponse)
def upload_teacher_avatar(TeacherAvatar: schemas.TeacherAvatar, db: Session = Depends(get_db)):
    return crud.upload_teacher_avatar(db=db, teacher_avatar=TeacherAvatar)

@controller.post("/upload_voice_sample", tags=["Voice Sample"],response_model=schemas.VoiceSampleResponse)
def upload_voice_sample(voice: schemas.VoiceSample, db: Session = Depends(get_db)):
    return crud.upload_voice_sample(db=db, voice=voice)


@controller.post("/create_virtual_avatar", tags=["Teacher Virtual Avatar"],response_model=schemas.VirtualAvatarBase)
def create_virtual_avatar(VirtualAvatar: schemas.VirtualAvatar, db: Session = Depends(get_db)):
    # db_user = crud.get_batch_by_name(db, name=batch.name)
    # if db_user:
    #     raise HTTPException(status_code=400, detail="Batch already registered")
    return crud.create_virtual_avatar(db=db, virtual_avatar= VirtualAvatar)

@controller.post("/create_course", tags=["Course"])
def create_course(course: schemas.CreateCourse, db: Session = Depends(get_db)):
    # db_user = crud.get_batch_by_name(db, name=batch.name)
    # if db_user:
    #     raise HTTPException(status_code=400, detail="Batch already registered")
    return crud.create_course(db=db, course=course)

@controller.post("/create_post", tags=["Users"],response_model=schemas.CreatePostBase)
def create_post(post: schemas.CreatePost, db: Session = Depends(get_db)):
    # db_user = crud.get_batch_by_name(db, name=batch.name)
    # if db_user:
    #     raise HTTPException(status_code=400, detail="Batch already registered")
    return crud.create_post(db=db, post= post)

@controller.post("/create_stories", tags=["Users"],response_model=schemas.CreateStoriesBase)
def create_stories(stories: schemas.CreateStories, db: Session = Depends(get_db)):
    # db_user = crud.get_batch_by_name(db, name=batch.name)
    # if db_user:
    #     raise HTTPException(status_code=400, detail="Batch already registered")
    return crud.create_stories(db=db, stories= stories)

@controller.post("/create_activity", tags=["Users"],response_model=schemas.CreateActivityBase)
def create_activity(activity: schemas.CreateActivity, db: Session = Depends(get_db)):
    # db_user = crud.get_batch_by_name(db, name=batch.name)
    # if db_user:
    #     raise HTTPException(status_code=400, detail="Batch already registered")
    return crud.create_activity(db=db, activity= activity)


@controller.post("/Like", tags=["Users"],response_model=schemas.LikeBase)
def like(like: schemas.Like, db: Session = Depends(get_db)):
    # db_user = crud.get_batch_by_name(db, name=batch.name)
    # if db_user:
    #     raise HTTPException(status_code=400, detail="Batch already registered")
    return crud.like(db=db, like= like)

@controller.post("/Share", tags=["Users"],response_model=schemas.ShareBase)
def share(share: schemas.Share, db: Session = Depends(get_db)):
    # db_user = crud.get_batch_by_name(db, name=batch.name)
    # if db_user:
    #     raise HTTPException(status_code=400, detail="Batch already registered")
    return crud.share(db=db, share= share)

@controller.post("/View", tags=["Users"],response_model=schemas.ViewBase)
def view(view: schemas.View, db: Session = Depends(get_db)):
    # db_user = crud.get_batch_by_name(db, name=batch.name)
    # if db_user:
    #     raise HTTPException(status_code=400, detail="Batch already registered")
    return crud.view(db=db, view = view)

@controller.post("/Comment", tags=["Users"],response_model=schemas.CommandBase)
def Comment(commands: schemas.Command, db: Session = Depends(get_db)):
    # db_user = crud.get_batch_by_name(db, name=batch.name)
    # if db_user:
    # raise HTTPException(status_code=400, detail="Batch already registered")
    return crud.comment(db=db, command= commands)

@controller.post("/create_subject", tags=["Subject"],response_model=schemas.CreateSubject)
def create_subject(subject: schemas.Subject, db: Session = Depends(get_db)):
    # db_user = crud.get_batch_by_name(db, name=batch.name)
    # if db_user:
    # raise HTTPException(status_code=400, detail="Batch already registered")
    return crud.create_subject(db=db, subjects= subject)

@controller.post("/create_reqres", tags=["Request Response"],response_model=schemas.CreateRequestResponse)
def create_subject(reqres : schemas.RequestResponse, db: Session = Depends(get_db)):
    # db_user = crud.get_batch_by_name(db, name=batch.name)
    # if db_user:
    # raise HTTPException(status_code=400, detail="Batch already registered")
    return crud.OCR_request_response(db=db, reqres= reqres)


@controller.post("/create_layout", tags=["Layouts"],response_model=schemas.CreateLayout)
def create_layout(layout : schemas.Layout , db: Session = Depends(get_db)):
    # db_user = crud.get_batch_by_name(db, name=batch.name)
    # if db_user:
    # raise HTTPException(status_code=400, detail="Batch already registered")
    return crud.create_layout(db=db, layout= layout)


@controller.post("/create_book", tags=["Book"],response_model=schemas.CreateBook)
def create_book(book : schemas.Book , db: Session = Depends(get_db)):
    # db_user = crud.get_batch_by_name(db, name=batch.name)
    # if db_user:
    # raise HTTPException(status_code=400, detail="Batch already registered")
    return crud.create_book(db=db, book= book)


@controller.post("/varify_otp", tags=["OTP"])
def varify_otp(req: schemas.otp, db: Session = Depends(get_db)):
    return otp.varify_otp(db=db, phone_number = req.phone_number, otp = req.otp )


@controller.post("/login", tags=["login"])
def login(phone_number: str, db: Session = Depends(get_db)):
    return otp.login(db=db, phone_number = phone_number)








@controller.post("/cartoonimages", tags=["Cartoon Images"])
async def create_cartoonimages(cartoonimages : schemas.CartoonImages , db: Session = Depends(get_db)):
    return crud.create_cartoonimages(db=db, cartoonimages=cartoonimages)
    

@controller.get("/cartoonimages/{image_name}",tags=["Cartoon Images"], response_model=List[schemas.CartoonImages])
async def get_all_cartoonimages_by_imagename(image_name : str,db: Session = Depends(get_db)):
    requests = crud.get_all_cartoonimages_by_imagename(db, image_name = image_name)
    return requests

@controller.get("/allcartoonimage",tags=["Cartoon Images"], response_model=List[schemas.CartoonImages])
async def get_all_cartoonimages(user_id: int, is_active: bool = True, db: Session = Depends(get_db)):
    requests = crud.get_all_cartoonimages(db,user_id=user_id, is_active=is_active)
    return requests

@controller.get("/cartoonimage/{cartoon_id}",tags=["Cartoon Images"])
async def get_all_cartoonimages_by_cartoonid(cartoon_id : int,db: Session = Depends(get_db)):
    requests = crud.get_all_cartoonimages_by_cartoonid(db, cartoon_id = cartoon_id)
    return requests

@controller.get("/alluserimage", tags=["Students1"],response_model=List[schemas.UserImages])
def get_all_userimage(user_id: int, is_active: bool = True, db: Session = Depends(get_db)):
    requests = crud.get_all_userimage(db, user_id=user_id, is_active=is_active)
    return requests
