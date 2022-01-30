import re
from sqlalchemy.orm import Session
from fastapi import Depends, FastAPI, HTTPException, Request, Response
from pytz import timezone
from datetime import datetime, time
from sqlalchemy.sql import schema
from sqlalchemy.sql.functions import user
import requests
from sqlalchemy.sql.selectable import Select
from starlette.responses import HTMLResponse
from . import models, schemas, otp
from sqlalchemy import text
import json

UTC = timezone('UTC')

def flush_db(db: Session):
    db.flush()


# def get_access_token(url, client_id, client_secret):
#     response = requests.post(
#         url,
#         data={"grant_type": "client_credentials"},
#         auth=(client_id, client_secret),
#     )
#     return response.json()

def register_student(db: Session, student: schemas.Student):

    # Verify student is not registered before
    # print("checking email address is not registered before..!")
    # #if (db.query(models.Student).filter(str(student.email_address).strip().upper()).first()) or (db.query(models.Student).filter(str(student.email_address).strip().lower()).first()) or (db.query(models.Student).filter(student.email_address).first()):
    # if (db.query(models.Student).filter(models.Student.email_address.ilike("%" + student.email_address.strip().lower() +  "%")).first()):
    #     print("Seems student is already registered by ", student.email_address)
    #     raise HTTPException(status_code=400, detail="{} already registered".format(student.email_address))

    # if (db.query(models.Student).filter(models.Student.phone_number.ilike("%" + student.phone_number.strip().lower() +  "%")).first()):
    #     print("Seems student is already registered by ", student.phone_number)
    #     raise HTTPException(status_code=400, detail="{} already registered".format(student.phone_number))

    """
    # Fetch client_id, school_id, and batch_ids from the names given in student's info
    client_obj = db.query(models.Client).filter(models.Client.client_id ==  student.authorized_client_id).first()
    # print("student.school :: ", student.school_name)
    # print("student.school :: ", student.batch_name)
    if student.school_id != None:
        school_obj = db.query(models.School).filter(models.School.school_id ==  student.school_id).first()
        school_id = school_obj.school_id if school_obj != None else 1
    else:
        school_id = 1
    if student.batch_id != None:
        batch_obj = db.query(models.Batch).filter(models.Batch.batch_id ==  student.batch_id).first()
        batch_id = batch_obj.batch_id if batch_obj != None else 1
    else:
        batch_id = 1

    #school_obj =db.query(models.School).filter(models.School.name ==  student.school_name).first()
    #batch_obj =db.query(models.Batch).filter(models.Batch.name ==  student.batch_name).first()

    # verify the client, batch, school objs are present, else tag them to others/default
    authorized_client_id =client_obj.client_id if client_obj != None else 1
    # mapping to default client
    #client_id = 1
    #school_id = 1
    #batch_id = 1

    print("The client_id found from student -> ", authorized_client_id)
    print("The batch_id found from student -> ", batch_id)
    print("The school_id found from student -> ", school_id)
    """

    # school_id = db.query(models.School).filter(models.School.name == student.school_name).first()
    # if school_id == None:
    #     pass
    #     # raise HTTPException(status_code=400, detail="Invalid Client name, please register the Client first")
    # else:
    #     school_id = school_id.school_id

    # verify the client is valid
    # authorized_client_id = db.query(models.Client).filter(models.Client.name == student.client_name).first()
    # if authorized_client_id == None:
    #     raise HTTPException(status_code=400, detail="Invalid Client name, please register the Client first")
    # else:
    #     authorized_client_id = authorized_client_id.client_id

    # batch_id = db.query(models.Batch).filter(models.Batch.name == student.batch_name).first()
    # if batch_id == None:
    #     pass
    #     # raise HTTPException(status_code=400, detail="Invalid Client name, please register the Client first")
    # else:
    #     batch_id = batch_id.batch_id

    # favorite_teacher_id = db.query(models.VirtualAvatar).filter(models.VirtualAvatar.name == student.favorite_teacher_name).first()
    # if favorite_teacher_id == None:
    #     pass
    #     # raise HTTPException(status_code=400, detail="Invalid Client name, please register the Client first")
    # else:
    #     favorite_teacher_id = favorite_teacher_id.virtual_avatar_id


    headers = {'Content-Type': 'application/json'}
    data = {
        "username" : student.email_address,
        "custom_id" : student.phone_number
    }
    kong = requests.post("https://service.mcgroce.com/register/consumers/", data=json.dumps(data), headers=headers)
    kong = requests.post(f"https://service.mcgroce.com/register/consumers/{student.email_address}/oauth2", data=json.dumps({"name":student.name}), headers=headers)
    kong = kong.json()
    print(kong)
    user_data = models.User(phone_number=student.phone_number, client_id=kong['client_id'],
        client_secret=kong['client_secret'], email_address=student.email_address, role="Student", latitude="0",longitude="0", varified=False)

    db.add(user_data)
    db.commit()
    db.refresh(user_data)

    db_user = models.Student(name=student.name,gender=student.gender,dob=student.dob,
      batch_id=None, school_id=None, favorite_teacher_id= None,
      who_pays_for_course=student.who_pays_for_course, english_proficiency=student.english_proficiency,
      preferred_language=student.preferred_language, user_id = user_data.user_id
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    access_token = otp.get_access_token("https://service.mcgroce.com/hertzai/oauth2/token", user_data.client_id, user_data.client_secret)

    print(access_token)

    generated_otp = otp.generate_otp()
    print(" *************************  generated otp : ", generated_otp)

    save = otp.save_otp(db=db, phone_number=student.phone_number, otp = generated_otp, user_id = user_data.user_id)

    subject = "Registration successful"
    email = user_data.email_address
    message = "Please varify your email address, OTP: {} \n  For security reasons, this code will expire in 10 minutes. Please don't tell others.".format(generated_otp)
    email = otp.send_email(subject=subject, message=message, email=email)
    access_token["user_id"] = user_data.user_id

    # Once student's info is store in db, now fetch the school, batch, and client information from database!!
    # db_user.school=(db.query(models.School).filter(db_user.school_id == models.School.school_id).first()).name
    # db_user.client=(db.query(models.Client).filter(db_user.authorized_client_id == models.Client.client_id).first()).name
    # db_user.batch=(db.query(models.Batch).filter(db_user.batch_id == models.Batch.batch_id).first()).name
    return access_token


def register_teacher(db: Session, teacher: schemas.TeacherBase):

    # school_id = db.query(models.School).filter(models.School.name == teacher.school_name).first()
    # if school_id == None:
    #     raise HTTPException(status_code=400, detail="Invalid Client name, please register the Client first")
    # else:
    #     school_id = school_id.school_id

    # # verify the client is valid
    # client_id = db.query(models.Client).filter(models.Client.name == teacher.client_name).first()
    # if client_id == None:
    #     raise HTTPException(status_code=400, detail="Invalid Client name, please register the Client first")
    # else:
    #     client_id = client_id.client_id

    # course_id = db.query(models.Course).filter(models.Course.name == teacher.course_name).first()
    # if course_id == None:
    #     raise HTTPException(status_code=400, detail="Invalid Client name, please register the Course first")
    # else:
    #     course_id = course_id.course_id


    # Verify teacher is not registered before
    # print("checking email address is not registered before..!")
    # if (db.query(models.Teacher).filter(models.Teacher.email_address.ilike("%" + teacher.email_address.strip().lower() +  "%")).first()):
    #     print("Seems teacher is already registered by ", teacher.email_address)
    #     raise HTTPException(status_code=400, detail="{} already registered".format(teacher.email_address))

    # if (db.query(models.Teacher).filter(models.Teacher.phone_number.ilike("%" + teacher.phone_number.strip().lower() +  "%")).first()):
    #     print("Seems teacher is already registered by ", teacher.phone_number)
    #     raise HTTPException(status_code=400, detail="{} already registered".format(teacher.phone_number))

    headers = {'Content-Type': 'application/json'}
    data = {
        "username" : teacher.email_address,
        "custom_id" : teacher.phone_number
    }
    kong = requests.post("https://service.mcgroce.com/register/consumers/", data=json.dumps(data), headers=headers)
    kong = requests.post(f"https://service.mcgroce.com/register/consumers/{teacher.email_address}/oauth2", data=json.dumps({"name":teacher.name}), headers=headers)
    kong = kong.json()
    print(kong)
    user_data = models.User(phone_number=teacher.phone_number, client_id=kong['client_id'],
        client_secret=kong['client_secret'], email_address=teacher.email_address, role="Teacher", latitude="0",longitude="0", varified=False)

    db.add(user_data)
    db.commit()
    db.refresh(user_data)

    db_teacher = models.Teacher(name=teacher.name,
    address = teacher.address,
    school_id = None,
    course_id = None,
    user_id = user_data.user_id)
    db.add(db_teacher)
    db.commit()
    db.refresh(db_teacher)

    print("Successfully inserted the teacher record with id -> ",db_teacher.teacher_id)

    access_token = otp.get_access_token("https://service.mcgroce.com/hertzai/oauth2/token", user_data.client_id, user_data.client_secret)

    print(access_token)

    generated_otp = otp.generate_otp()
    print(" *************************  generated otp : ", generated_otp)

    save = otp.save_otp(db=db, phone_number=teacher.phone_number, otp = generated_otp, user_id = user_data.user_id)

    subject = "Registration successful"
    email = user_data.email_address
    message = "Please varify your email address, OTP: {} \n  For security reasons, this code will expire in 10 minutes. Please don't tell others.".format(generated_otp)
    email = otp.send_email(subject=subject, message=message, email=email)
    access_token["user_id"] = user_data.user_id

    #Now make entries in client-teacher-course table

    """
    db_client_teacher_course = models.ClientTeacherCourse(client_id=client_id,
    course_id=course_id,
    teacher_id=db_teacher.teacher_id,
    school_id=db_teacher.school_id)

    db.add(db_client_teacher_course)
    db.commit()
    db.refresh(db_client_teacher_course)
    # db_teacher.client_name=teacher.client_name
    # db_teacher.course_name=teacher.course_name
    # db_teacher.school_name=teacher.school_name

    """
    return access_token

# @DeprecationWarning
def get_teacher_by_name(db: Session, name: str):
    return db.query(models.Teacher).filter(models.Teacher.name == name).first()

def create_client(db: Session, client: schemas.ClientInfo):
    # fake_hashed_password = student..password + "not really hashed!!"
    db_user = models.Client(name=client.name, num_of_students=client.num_of_students,
        phone_number=client.phone_number, email_address=client.email_address)
    #apis = client.apis)
    #db_user = models.Client(name=client.name)
    #db_user = student
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    print("saved the client with request id -> ",db_user.client_id)
    CourseBatchBookOuputList = []
    CourseBatchBookOuput = {}
    if db_user.client_id > 0:
        for x in range(len(client.apis)):
            db_response = models.API(name = client.apis[x].name, is_active=client.apis[x].is_active,authorized_client_id=db_user.client_id)
            db.add(db_response)
            db.commit()
            db.refresh(db_response)
            print("saved the api from client with api id -> ",db_response.api_id)
        for x in range(len(client.courseBatchBooks_offered)):
            CourseBatchBookOuput = {}
            course_response = models.Course(name = client.courseBatchBooks_offered[x].course_name, is_active=client.courseBatchBooks_offered[x].is_active,authorized_client_id=db_user.client_id)
            db.add(course_response)
            db.commit()
            print("saved the Course from client with course_id -> ",course_response.course_id)
            CourseBatchBookOuput['course_name'] = client.courseBatchBooks_offered[x].course_name
            batch_response = models.Batch(name = client.courseBatchBooks_offered[x].batch_name, is_active=client.courseBatchBooks_offered[x].is_active,authorized_client_id=db_user.client_id)
            db.add(batch_response)
            db.commit()
            db.refresh(batch_response)
            print("saved the Batch from client with batch_id -> ",batch_response.batch_id)
            CourseBatchBookOuput['batch_name'] = client.courseBatchBooks_offered[x].batch_name
            book_response = models.Book(name = client.courseBatchBooks_offered[x].book_name, is_active=client.courseBatchBooks_offered[x].is_active)
            db.add(book_response)
            db.commit()
            print("saved the Book from client with book_id -> ",book_response.book_id)
            CourseBatchBookOuput['book_name'] = client.courseBatchBooks_offered[x].book_name
            CourseBatchBookOuput['is_active'] = client.courseBatchBooks_offered[x].is_active
            CourseBatchBookOuputList.append(CourseBatchBookOuput)
            book_course_response = models.BookCourseNormalized(book_id = book_response.book_id, course_id=course_response.course_id)
            db.add(book_course_response)
            db.commit()
            print("saved the BookCourse ids from client with book_course_id -> ",book_course_response.book_course_id)
            db.refresh(course_response)
            db.refresh(book_response)
            db.refresh(book_course_response)
    print("CourseBatchBookOuputList")
    print(CourseBatchBookOuputList)
    db_user.courseBatchBooks_offered = CourseBatchBookOuputList
    return db_user

def create_batch(db: Session, batch: schemas.BatchBase):
    #fake_hashed_password = student..password + "not really hashed!!"

    print("batch.client_name -> " + batch.client_name)
    print("batch.scool_name -> " + batch.school_name)
    # verify the client is valid
    client_id = db.query(models.Client).filter(models.Client.name == batch.client_name).first()
    if client_id == None:
        raise HTTPException(status_code=400, detail="Invalid Client name, please register the Client first")
    else:
        client_id = client_id.client_id

    # verify the school is valid
    school_id = db.query(models.School).filter(models.School.name == batch.school_name).first()
    if school_id == None:
        raise HTTPException(status_code=400, detail="Invalid School name, please register the School first")
    else:
        school_id = school_id.school_id

    standard_id = db.query(models.Standard).filter(models.Standard.standard == batch.standard).first()
    if standard_id == None:
        raise HTTPException(status_code=400, detail="Invalid Standard , please register the Standard first")
    else:
        standard_id = standard_id.standard_id

    # Get the school_id from school name

    db_batch = models.Batch(name=batch.name,
                            is_active=batch.is_active,
                            year = batch.year,
                            authorized_client_id=client_id,
                            school_id=school_id,
                            standard_id = standard_id
                            )
    #db_user = student
    db.add(db_batch)
    db.commit()
    db.refresh(db_batch)
    print("The batch details saved in database!!")
    print(db_batch.batch_id)
    print(db_batch.name)
    print(db_batch.is_active)
    db_batch.client_name=batch.client_name
    db_batch.school_name=batch.school_name
    return db_batch

def register_school(db: Session, school: schemas.SchoolBase):
    affiliation_code = db.query(models.School).filter(models.School.affiliation_code == school.affiliation_code).first()
    if affiliation_code:
        raise HTTPException(status_code=400, detail="School already register with this Affiliation Code")

    # board_id = db.query(models.Board).filter(models.Board.board_id == school.board_id).first()
    # if board_id == None:
    #     raise HTTPException(status_code=400, detail="Invalid School name, please register the School first")
    # else:
    #     board_id = board_id.board_id

    headers = {'Content-Type': 'application/json'}
    data = {
        "username" : school.email_address,
        "custom_id" : school.phone_number
    }
    kong = requests.post("https://service.mcgroce.com/register/consumers/", data=json.dumps(data), headers=headers)
    kong = requests.post(f"https://service.mcgroce.com/register/consumers/{school.email_address}/oauth2", data=json.dumps({"name":school.school_name}), headers=headers)
    kong = kong.json()
    print(kong)
    user_data = models.User(phone_number=school.phone_number, client_id=kong['client_id'],
        client_secret=kong['client_secret'], email_address=school.email_address, role="School", latitude="0",longitude="0", varified=False)

    db.add(user_data)
    db.commit()
    db.refresh(user_data)

    db_school = models.School(school_name=school.school_name, school_address=school.school_address, board_id=school.board_id,
        affiliation_code = school.affiliation_code, user_id = user_data.user_id
    )

    db.add(db_school)
    db.commit()
    db.refresh(db_school)
    print("The school details saved in database!!")

    access_token = otp.get_access_token("https://service.mcgroce.com/hertzai/oauth2/token", user_data.client_id, user_data.client_secret)

    print(access_token)

    generated_otp = otp.generate_otp()
    print(" *************************  generated otp : ", generated_otp)

    save = otp.save_otp(db=db, phone_number=school.phone_number, otp = generated_otp, user_id = user_data.user_id)

    subject = "Registration successful"
    email = user_data.email_address
    message = "Please varify your email address, OTP: {} \n  For security reasons, this code will expire in 10 minutes. Please don't tell others.".format(generated_otp)
    email = otp.send_email(subject=subject, message=message, email=email)
    access_token["user_id"] = user_data.user_id
    return access_token

def create_business_signup(db: Session, business_signup: schemas.Business_Signup):

    db_business_signup = models.Business_Signup(
                                name = business_signup.name,
                                email = business_signup.email,
                                no_of_students = business_signup.no_of_students

                                )
    db.add(db_business_signup)
    db.commit()
    db.refresh(db_business_signup)
    # db_assessment_result.assessment_name=assessment_result.assessment_name
    # db_assessment_result.student_name=assessment_result.student_name
    return db_business_signup


def fetch_paragraph_topic_name_and_studentid(db : Session, fetch_paragraph : schemas.Fetch_Paragraph):

    student_id = db.query(models.Student).filter(models.Student.student_id == fetch_paragraph.student_id)
    if student_id == None:
        raise HTTPException(status_code=400, detail="Invalid Student ID")
    else:
        student_id = student_id.student_id

    return db.query(models.Layout).filter(models.Layout.topic_name and models.Layout.student_id).all()


def fetch_topics_student_id_chapter_name(db: Session, fetch_topic_name : schemas.Fetch_Topic_name):

    student_id = db.query(models.Student).filter(models.Student.student_id == fetch_topic_name.student_id)
    if student_id == None:
        raise HTTPException(status_code=400, detail="Invalid Student ID")
    else:
        student_id = student_id.student_id

    return db.query(models.Layout).filter(models.Layout.chapter_name and models.Layout.student_id).all()


def fetch_chapter_bookname_studentid(db : Session, fetch_chapter : schemas.Fetch_Chapter):

    student_id = db.query(models.Student).filter(models.Student.student_id == fetch_chapter.student_id)
    if student_id == None:
        raise HTTPException(status_code=400, detail="Invalid Student ID")
    else:
        student_id = student_id.student_id

    book_name = db.query(models.Layout).join(models.Layout.book_id == models.Book.name)
    if book_name == None:
        raise HTTPException(status_code=400, detail="Invalid Student ID")
    else:
        book_name = book_name.book_name


    return db.query(models.Layout).filter(models.Layout.student_id and book_name)


def fetch_subjects(db: Session, fetch_subjects : schemas):

    student_id = db.query(models.Student).filter(models.Student.student_id == fetch_subjects.student_id).first()
    if student_id == None:
        raise HTTPException(status_code=400, detail="Invalid Student ID")
    else:
        student_id = student_id.student_id

    return db.query(models.Subject).filter(models.Subject.student_id == student_id).all()


def fetch_subjects_teacher_id(db : Session, fetch_subjects_teacher_id : schemas.Fetch_Subjects_Teacher):

    teacher_id = db.query(models.Teacher).filter(models.Teacher.teacher_id == fetch_subjects_teacher_id.teacher_id).first()
    if teacher_id == None:
        raise HTTPException(status_code=400, detail="Invalid Teacher ID")
    else:
        teacher_id = teacher_id.teacher_id

    return db.query(models.Subject).filter(models.Subject.teacher_id == teacher_id).all()


def fetch_book_name_student_id_subject(db : Session, fetch_book_name : schemas.FetchBookName):

    student_id = db.query(models.Student).filter(models.Student.student_id == fetch_book_name.student_id)
    if student_id == None:
        raise HTTPException(status_code=400, detail="Invalid Student ID")
    else:
        student_id = student_id.student_id

    subject_id = db.query(models.Subject).filter(models.Subject.subject_id == fetch_book_name.subject_id)
    if subject_id == None:
        raise HTTPException(status_code=400, detail="Invalid Subject ID")
    else:
        subject_id = subject_id.subject_id


    return db.query(models.Book).filter(models.Book.subject_id and models.Book.student_id)


def virtual_teachers_student_id(db : Session, fetch_virtual_teachers : schemas.FetchVirtualTeachers):

    student_id = db.query(models.Student).filter(models.Student.student_id == fetch_virtual_teachers.student_id)
    if student_id == None:
        raise HTTPException(status_code=400, detail="Invalid Student ID")
    else:
        student_id = student_id.student_id

    virtual_avatar_id = db.query(models.VirtualAvatar).filter(models.VirtualAvatar.virtual_avatar_id == fetch_virtual_teachers.virtual_avatar_id)
    if virtual_avatar_id == None:
        raise HTTPException(status_code=400, detail="Invalid Virtual Teacher ID")
    else:
        virtual_avatar_id = virtual_avatar_id.virtual_avatar_id


    return db.query(models.StudentVirtualAvatar).filter(models.StudentVirtualAvatar.student_id and models.StudentVirtualAvatar.virtual_avatar_id)


def real_teachers_student_id(db : Session, fetch_real_teachers : schemas.FetchRealTeachers):

    teacher_id = db.query(models.Teacher).filter(models.Teacher.teacher_id == fetch_real_teachers.teacher_id)
    if teacher_id == None:
        raise HTTPException(status_code=400, detail="Invalid Teacher ID")
    else:
        teacher_id = teacher_id.teacher_id

    student_id = db.query(models.Student).filter(models.Student.student_id == fetch_real_teachers.student_id)
    if student_id == None:
        raise HTTPException(status_code=400, detail="Invalid Student ID")
    else:
        student_id = student_id.student_id

    return db.query(models.TeacherStudentNorm).filter(models.TeacherStudentNorm.student_id and models.TeacherStudentNorm.teacher_id)


def get_allrequest(db: Session, skip: int = 0, limit: int = 100):
    print("get_allrequest")
    new = db.query(models.search_request).offset(skip).limit(limit).all()
    for x in range(len(new)):
        print(new[x].macaddress)
    return new


def get_allrequestAndResponse(db: Session, skip: int = 0, limit: int = 100):
    print("get_allrequest")
    new = db.query(models.search_request).join(models.search_response).offset(skip).limit(limit).all()
    for x in range(len(new)):
        print(new[x].logParam)
        for y in range(len(new[x].logParam)):
            print( new[x].logParam[y].response_id)
    return new


def update_searchRequestStatus(db: Session, request_id: int, status:str):
    print("update_searchRequestStatus ")
    db_request = db.query(models.search_request).filter(models.search_request.request_id == request_id).first()
    db_request.status = status
    db.commit()
    db.refresh(db_request)


def get_searchRequestBasedOnStatus(db: Session, status:str):
    print("get_searchRequestBasedOnStatus")
    new = db.query(models.search_request).join(models.search_response).filter(models.search_request.status == status).all()
    # for x in range(len(new)):
        # print(new[x].logParam)
        # for y in range(len(new[x].logParam)):
            # print( new[x].logParam[y].response_id)
    return new


def get_responseforrequestid(db: Session, request_id: int):
    return db.query(models.search_response).filter(models.search_response.request_id == request_id).all()

def updateSearch_result(db: Session, response_id:int, result:str, time_taken:int, matched_file:str, log_file:str):
    print('Updated search result '+str(response_id))
    db_response = db.query(models.search_response).filter(models.search_response.response_id == response_id).first()
    print(db_response)
    db_response.matched_file = matched_file
    db_response.search_result = result
    db_response.time_taken = time_taken
    db_response.log_file_path = log_file
    db.commit()

def create_request(db: Session, request: schemas.SearchRequest):
    print("creating request")
    db_request = models.search_request(macaddress = request.macaddress, starttime = request.starttime, endtime = request.endtime, status = request.status, user_nt_id = request.user_nt_id ,updated_time = request.updated_time , time_taken = 0)
    print(db_request.macaddress)
    db.add(db_request)
    db.commit()
    db.refresh(db_request)
    if db_request.request_id > 0 :
        for x in range(len(request.logParam)):
            db_response = models.search_response(log_message = request.logParam[x].log_message, log_file_path = request.logParam[x].log_file_path, request_id = db_request.request_id, updated_time =  request.logParam[x].updated_time, time_taken = 0 )
            db.add(db_response)
            db.commit()
            db.refresh(db_response)
    return db_request



def get_user_by_username(db: Session, username: str):
    return db.query(models.UserInfo).filter(models.UserInfo.username == username).first()

# def create_user(db: Session, user: schemas.UserCreate):
#     fake_hashed_password = user.password + "not really hashed!!"
#     db_user = models.UserInfo(username=user.username, password=fake_hashed_password, fullname=user.fullname)
#     db.add(db_user)
#     db.commit()
#     db.refresh(db_user)
#     return db_user


def get_allUsers(db: Session, skip: int = 0, limit: int = 100):
    print("Entered get_allUsers")
    new = db.query(models.UserInfo).offset(skip).limit(limit).all()
    for x in range(len(new)):
        print(new[x].username)
    return new


def get_user_by_phone_number(db: Session, phone_number: str):
    return db.query(models.User).filter(models.User.phone_number == phone_number).first()


def get_user_by_email_address(db: Session, email_address: str):
    return db.query(models.User).filter(models.User.email_address == email_address).first()


def get_allStudents(db: Session, skip: int = 0, limit: int = 100):
    print("Entered get_allUsers")
    new = db.query(models.Student).offset(skip).limit(limit).all()
    for x in range(len(new)):
        print(new[x].name)
    return new

def create_user(db: Session, user: schemas.UserBase):
    print("Entered create_user()")
    # Verify user is not registered before
    print("checking email address is not registered before..!")
    #if (db.query(models.user).filter(str(user.email_address).strip().upper()).first()) or (db.query(models.user).filter(str(user.email_address).strip().lower()).first()) or (db.query(models.user).filter(user.email_address).first()):
    # if (db.query(models.User).filter(models.User.email_address.ilike("%" + user.email_address.strip().lower() +  "%")).first()):
    #     print("Seems user is already registered by ", user.email_address)
    #     raise HTTPException(status_code=400, detail="user already registered")

    # if (db.query(models.User).filter(models.User.phone_number.ilike("%" + user.phone_number.strip().lower() +  "%")).first()):
    #     print("Seems user is already registered by ", user.email_address)
    #     raise HTTPException(status_code=400, detail="user already registered")
    print("user.email_address -> ", user.email_address)
    print("user.phone_number -> ", user.phone_number)
    user_id = db.query(models.User).filter(models.User.email_address == user.email_address
                    ,models.User.phone_number == user.phone_number).first()
    print("userID -> ", user_id)
    if user_id != None:
        print("User already registered..!!")
        raise HTTPException(status_code=400, detail="user already registered")

    db_user = models.User(name=user.name,email_address=user.email_address,phone_number=user.phone_number,
     current_grade = user.current_grade, image_url = user.image_url, latitude = user.latitude, longitude = user.longitude,
     creationDate = datetime.now())
    #db_user = student
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    if db_user.user_id > 0:
        for x in range(len(user.apis)):
            db_response = models.API(name = user.apis[x].name, is_active=user.apis[x].is_active,authorized_user_id=db_user.user_id)
            db.add(db_response)
            db.commit()
            db.refresh(db_response)
            print("saved the api from user with api id -> ",db_response.api_id)

    # Once student's info is store in db, now fetch the school, batch, and client information from database!!
    #db_user.apis=db.query(models.API).filter(db_user.user_id == models.API.authorized_user_id)
    return db_user



def save_conversation(db: Session, conv: schemas.Conversation):
    print("Entered save_converstation()")

    #validate user id
    user_obj = db.query(models.User).filter(models.User.user_id == conv.user_id).first()
    if user_obj == None:
        print("Seems user not found with id :", conv.user_id)
        raise HTTPException(status_code=400, detail="User Not Found with ID : " + str(conv.user_id))
    print("Valid user found  : ", user_obj.name)

    db_conv = models.Conversation(timestamp = datetime.now(UTC),
                                    user_id = conv.user_id,
                                    request = conv.request,
                                    response = conv.response,
                                    conv_bot_name = conv.conv_bot_name)
    db.add(db_conv)
    db.commit()
    db.refresh(db_conv)

    if db_conv.conv_id > 0:
        print("saved the converstation to database with id : ", db_conv.conv_id)

    return db_conv

def get_all_students(db: Session, skip: int = 0, limit: int = 100):
    print("Entered get_all_students")
    studentList = db.query(models.Student).offset(skip).limit(limit).all()
    print("queried successfully..!!")
    for x in range(len(studentList)):
        print("Student name -> ", studentList[x].name)
        # Once student's info is store in db, now fetch the school, batch, and client information from database!!
        studentList[x].school=(db.query(models.School).filter(studentList[x].school_id == models.School.school_id).first()).name
        studentList[x].client=(db.query(models.Client).filter(studentList[x].authorized_client_id == models.Client.client_id).first()).name
        studentList[x].batch=(db.query(models.Batch).filter(studentList[x].batch_id == models.Batch.batch_id).first()).name
    print("logged all student names!!")

    return studentList

def get_all_users(db: Session, skip: int = 0, limit: int = 100):
    print("Entered get_all_users")
    userList = db.query(models.User).offset(skip).limit(limit).all()
    print("queried successfully..!!")
    for x in range(len(userList)):
        print("Student name -> ", userList[x].name)
        # Once student's info is store in db, now fetch the school, batch, and client information from database!!
        userList[x].features=db.query(models.API).filter(userList[x].user_id == models.API.authorized_user_id).all()
    print("logged all usernames!!")

    return userList


def get_all_conversations(db: Session, skip: int = 0, limit: int = 100):
    print("Entered get_all_users")
    convList = db.query(models.Conversation).offset(skip).limit(limit).all()
    print("queried successfully..!!")
    return convList

def get_recentconversations(db: Session, mins: int=10, skip: int = 0, limit: int = 100):

    try:
        mins = int(mins)
        print("mins parsed :" , mins)
    except ValueError:
        # Handle the exception
        raise HTTPException(status_code=400, detail="minutes are invalid, please check mins value")

    print("Entered get_all_users")
    ten_mins_ago = text('UTC_TIMESTAMP() - INTERVAL ' + str(mins) + ' MINUTE')
    print("ten_mins_ago : ", ten_mins_ago)
    convList = db.query(models.Conversation).filter(models.Conversation.timestamp > ten_mins_ago).offset(skip).limit(limit).all()
    print("queried successfully..!!")
    return convList

def get_client_by_name(db: Session, name: str):
    return db.query(models.Client).filter(models.Client.name == name).first()

def get_api_by_name(db: Session, name: str):
    return db.query(models.API).filter(models.API.name == name).first()

def get_business(db: Session, name: str):
    return db.query(models.Business_Signup).filter(models.Business_Signup.name == name).first()

def get_school_by_name(db: Session, name: str):
    return db.query(models.School).filter(models.School.name == name).first()

def get_batch_by_name(db: Session, name: str):
    return db.query(models.Batch).filter(models.Batch.name == name).first()

@DeprecationWarning
def get_teacher_by_name(db: Session, name: str):
    return db.query(models.Teacher).filter(models.Teacher.name == name).first()

def get_teacher_by_email_phone(db: Session, teacher: str):
    return db.query(models.Teacher).filter(models.Teacher.email_address == teacher.email_address
     or models.Teacher.phone_number == teacher.phone_number).first()


def get_assessments_by_name(db: Session, name: str):
    return db.query(models.Assessment).filter(models.Assessment.name == name).first()

def get_assessmentResults_by_student_name_and_assessment_name(db:Session, assessment_result: schemas.AssessmentResultBase):
    # verify the student is valid
    assessment_id = db.query(models.Assessment).filter(models.Assessment.name == assessment_result.assessment_name).first()
    if assessment_id == None:
        raise HTTPException(status_code=400, detail="Invalid assessment_name, please create the assessment first")
    else:
        assessment_id = assessment_id.assessment_id

    student_id = db.query(models.Student).filter(models.Student.name == assessment_result.student_name).first()
    if student_id == None:
        raise HTTPException(status_code=400, detail="Invalid student_name, please register the student first")
    else:
        student_id = student_id.student_id

    assessment_results = db.query(models.AssessmentResult).filter(models.AssessmentResult.assessment_id == assessment_id and models.AssessmentResult.student_id == student_id).first()
    return assessment_results

# def get_question_answers_by_assessment_id(db:Session, question_answer: schemas.QuestionAndAnswerByAssessmentID):
#     # verify the student is valid
#     assessment_id = db.query(models.Assessment).filter(models.Assessment.assessment_id == question_answer.assessment_id).first()
#     if assessment_id == None:
#         raise HTTPException(status_code=400, detail="Invalid assessment_id, please create the assessment first")
#     else:
#         assessment_id = question_answer.assessment_id

#     question_answers = db.query(models.QuestionAndAnswer).filter(models.QuestionAndAnswer.assessment_id == assessment_id).all()
#     return question_answers

def get_question_answers_by_assessment_id(db:Session, id : int):
    question_answers = db.query(models.QuestionAndAnswer).filter(models.QuestionAndAnswer.assessment_id == id).all()
    return question_answers


def get_goals_by_student_id(db: Session, student_name:str, email_address:str):
    student_id = db.query(models.Student).filter(models.Student.name == student_name and models.Student.email_address == email_address ).first()
    if student_id == None:
        raise HTTPException(status_code=400, detail="Invalid Student name / email_address, please register first")
    else:
        student_id = student_id.student_id
        print("Found the student id -> ", student_id)
    # Now verify that no goals are setup for this student id
    db_goals = db.query(models.Goal).filter(models.Goal.student_id == student_id).first()
    return db_goals

def get_all_schools(db: Session, skip: int = 0, limit: int = 100):
    print("Entered get_all_schools")
    #new = db.query(models.School).offset(skip).limit(limit).all()
    new = db.query(models.School).all()
    print("queried successfully..!!")
    for x in range(len(new)):
        print("School name -> ", new[x].school_name)
    print("logged all School names!!")
    return new

def get_all_batches(db: Session, skip: int = 0, limit: int = 100):
    print("Entered get_all_batches")
    #new = db.query(models.School).offset(skip).limit(limit).all()
    new = db.query(models.Batch).all()
    print("queried successfully..!!")
    for x in range(len(new)):
        print("Batch name -> ", new[x].name)
    print("logged all batch names!!")
    return new

def get_all_teachers(db: Session, skip: int = 0, limit: int = 100):
    print("Entered get_all_teachers")
    #new = db.query(models.School).offset(skip).limit(limit).all()
    new = db.query(models.Teacher).all()
    print("queried successfully..!!")
    for x in range(len(new)):
        print("Teacher name -> ", new[x].name)
    print("logged all teacher names!!")
    return new

def get_all_goals(db: Session, skip: int = 0, limit: int = 100):
    print("Entered get_all_goals")
    #new = db.query(models.School).offset(skip).limit(limit).all()
    #new = db.query(models.Goal).all()
    new = db.query(models.Goal).offset(skip).limit(limit).all()
    print("queried successfully..!!")
    return new

def get_all_assessments(db: Session, skip: int = 0, limit: int = 100):
    print("Entered get_all_assessments")
    new = db.query(models.Assessment).offset(skip).limit(limit).all()
    return new

# def last_para_id(db:Session):
#     return db.query(models.Paragraphs).order_by(models.Paragraphs.para_id.desc()).first()

def get_all_assessment_results(db: Session, skip: int = 0, limit: int = 100):
    print("Entered get_all_assessment_results")
    new = db.query(models.AssessmentResult).offset(skip).limit(limit).all()
    return new

def get_all_question_answers(db: Session, skip: int = 0, limit: int = 100):
    print("Entered get_all_question_answers")
    new = db.query(models.QuestionAndAnswer).offset(skip).limit(limit).all()
    return new

# def get_all_question_answers_by_assessment_id(db: Session):
#     print("Entered get_all_question_answers")
#     new = db.query(models.QuestionAndAnswer).filter(models.QuestionAndAnswer).all()
#     return new

# correct the method name
def get_all_question_answers_by_assessment_id(db: Session, assessment_id: int, skip: int = 0, limit: int = 100):
    #new = db.query(models.QuestionAndAnswer).offset(skip).limit(limit).all()
    all_QA = db.query(models.QuestionAndAnswer).filter(models.QuestionAndAnswer.assessment_id == assessment_id).all()
    return all_QA

def get_all_clients(db: Session, skip: int = 0, limit: int = 100):
    print("Entered get_all_clients")
    new = db.query(models.Client).offset(skip).limit(limit).all()
    print("queried successfully..!!")
    for x in range(len(new)):
        print("client name -> ", new[x].name)
        print("client active -> ", new[x].is_active)
    print("logged all client names!!")
    # TODO include course batch book in return statement..
    return new

# API
def create_api(db: Session, api: schemas.APICreate):
    #fake_hashed_password = student..password + "not really hashed!!"
    db_user = models.API(name=api.name,end_point=api.end_point, is_active=api.is_active)
    #db_user = models.Client(name=client.name)
    #db_user = student
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_all_apis(db: Session, skip: int = 0, limit: int = 100):
    print("Entered get_all_apis")
    apiList = db.query(models.API).offset(skip).limit(limit).all()
    print("queried successfully..!!")
    for x in range(len(apiList)):
        print("API name -> ", apiList[x].name)
    print("logged all api names!!")

    return apiList

def create_goal(db: Session, goal: schemas.GoalCreate):
    # verify the student is valid
    student_id = db.query(models.Student).filter(models.Student.name == goal.student_name and models.Student.email_address == goal.email_address ).first()
    student_id = student_id.student_id
    db_goal = models.Goal(student_id=student_id, goals=goal.goals)
    db.add(db_goal)
    db.commit()
    db.refresh(db_goal)
    db_goal.student_name=(db.query(models.Student).filter(models.Student.student_id == student_id).first()).name
    db_goal.email_address=(db.query(models.Student).filter(models.Student.student_id == student_id).first()).email_address
    return db_goal

def create_assessment(db: Session, assessment: schemas.AssessmentCreate):
    # verify the student is valid
    course_id = db.query(models.Course).filter(models.Course.name == assessment.course_name).first()
    if course_id == None:
        raise HTTPException(status_code=400, detail="Invalid Course name, please create the course first")
    else:
        course_id = course_id.course_id
    db_assessment = models.Assessment(name=assessment.name,
                                course_id=course_id,
                                number_of_questions=assessment.number_of_questions,
                                assessment_type=assessment.assessment_type,
                                is_active=assessment.is_active)
    db.add(db_assessment)
    db.commit()
    db.refresh(db_assessment)
    db_assessment.course_name=assessment.course_name
    return db_assessment

def create_assessment_result(db: Session, assessment_result: schemas.AssessmentResultCreate):
    # verify the student is valid
    assessment_id = db.query(models.Assessment).filter(models.Assessment.name == assessment_result.assessment_name).first()
    if assessment_id == None:
        raise HTTPException(status_code=400, detail="Invalid assessment_name, please create the assessment first")
    else:
        assessment_id = assessment_id.assessment_id

    student_id = db.query(models.Student).filter(models.Student.name == assessment_result.student_name).first()
    if student_id == None:
        raise HTTPException(status_code=400, detail="Invalid student_name, please register the student first")
    else:
        student_id = student_id.student_id

    db_assessment_result = models.AssessmentResult(
                                student_id=student_id,
                                assessment_id=assessment_id,
                                percent=assessment_result.percent,
                                improvement_areas=assessment_result.improvement_areas,
                                is_active=assessment_result.is_active,
                                )
    db.add(db_assessment_result)
    db.commit()
    db.refresh(db_assessment_result)
    db_assessment_result.assessment_name=assessment_result.assessment_name
    db_assessment_result.student_name=assessment_result.student_name
    return db_assessment_result

def create_paragraphs_tracker(db:Session, paragraph_tracker: schemas.ParagraphTracker):
    ## to track paragraphs
    # para_id = db.query(models.Paragraphs).filter(models.Paragraphs.para_id == paragraph_tracker.para_id).first()
    # if para_id == None:
    #     para_id = paragraph_tracker.para_id
    # else:
    #     raise HTTPException(status_code=400, detail="Invalid para_id, please try with another para_id")

    db_para_tracker = models.Paragraphs(
        # para_id = paragraph_tracker.para_id,
        paragraph = paragraph_tracker.paragraph,
        is_active = True
    )
    db.add(db_para_tracker)
    db.commit()
    db.refresh(db_para_tracker)
    # db_para_tracker.
    return db_para_tracker

def put_student_answer(db:Session,student_response:schemas.StudentsResponseCreate):
    db_put_student_answer = models.StudentsAnswer(
        question_id = student_response.question_id,
        student_id = student_response.student_id,
        student_answer = student_response.student_answer,
        assessment_id = student_response.assessment_id,
        f1score = student_response.f1score,
        recall = student_response.recall,
        emb_score = student_response.emb_score,
        is_active = student_response.is_active
    )
    db.add(db_put_student_answer)
    db.commit()

    db.refresh(db_put_student_answer)

    return db_put_student_answer

def get_students_answer_by_assessmentid_and_studentid(db:Session,student_response:schemas.StudentsResponseGet):
    assessment_id = db.query(models.StudentsAnswer).filter(models.StudentsAnswer.assessment_id == student_response.assessemnt_id).first()
    if assessment_id==None:
        raise HTTPException(status_code=400, detail="Invalid assessment_id, please try with another assessmentid")

    student_id = db.query(models.StudentsAnswer).filter(models.StudentsAnswer.student_id == student_response.student_id).first()
    if assessment_id==None:
        raise HTTPException(status_code=400, detail="Invalid student_id , please provide the registered student id or student haven't taken assessment yet")

    return db.query(models.StudentsAnswer).filter(models.StudentsAnswer.student_id == student_response.student_id and models.StudentsAnswer.assessment_id == student_response.assessment_id).all()

def get_all_paragraphs(db:Session):
    paras = db.query(models.Layout).all()
    return paras

def get_paragraph_by_para_id(db:Session, paragraph_tracker: schemas.ParagraphTracker):
    para_id = db.query(models.Paragraphs).filter(models.Paragraphs.id == paragraph_tracker.para_id).first()
    if para_id != None:
        raise HTTPException(status_code=400, detail="Invalid para_id, please try with another para_id")
    else:
        para_id = paragraph_tracker.para_id

    return db.query(models.Paragraphs).filter(models.Paragraphs.id == paragraph_tracker.para_id).first()

def create_question_answers(db: Session, question_answer: schemas.QuestionAndAnswerCreate):
    # verify the assessment is valid
    # assessment_id = db.query(models.Assessment).filter(models.Assessment.name == question_answer.assessment_name).first()
    # if assessment_id == None:
    #     raise HTTPException(status_code=400, detail="Invalid assessment_name, please create the assessment first")
    # else:
    #     assessment_id = assessment_id.assessment_id

    # QA_id = db.query(models.QuestionAndAnswer).filter(models.QuestionAndAnswer.assessment_id == assessment_id).first()

    # if QA_id != None:
    #     raise HTTPException(status_code=400, detail="Already created QA for the assessment :: " + question_answer.assessment_name)

    # db_question_answer = models.QuestionAndAnswer(
    #                             assessment_id=assessment_id,
    #                             question=question_answer.question,
    #                             question_type=question_answer.question_type,
    #                             layout_id = question_answer.layout_id,
    #                             options = question_answer.options,
    #                             answer=question_answer.answer,
    #                             is_active=question_answer.is_active,
    #                             )

    db_question_answer = models.QuestionAndAnswer(
                                question=question_answer.question,
                                question_type=question_answer.question_type,
                                layout_id = question_answer.layout_id,
                                options = question_answer.options,
                                answer=question_answer.answer,
                                is_active=question_answer.is_active,
                                assessment_id=6
                                )

    db.add(db_question_answer)
    db.commit()
    db.refresh(db_question_answer)
    db_question_answer.assessment_name=question_answer.assessment_name
    return db_question_answer

def update_question_answers(db: Session, qid:int, question_answer: schemas.QuestionAndAnswerBase2):
    # verify the assessment is valid
    assessment_id = db.query(models.Assessment).filter(models.Assessment.name == question_answer.assessment_name).first()
    if assessment_id == None:
        raise HTTPException(status_code=400, detail="Invalid assessment_id, please create the assessment first")
    else:
        assessment_id = assessment_id.assessment_id
    db_question_answer = db.query(models.QuestionAndAnswer).filter(models.QuestionAndAnswer.id == qid).first()
    db_question_answer.question = question_answer.question
    db_question_answer.question_type = question_answer.question_type
    db_question_answer.answer = question_answer.answer
    db_question_answer.is_active = question_answer.is_active
    db_question_answer.assessment_id = assessment_id
    db.commit()
    return db_question_answer

def verify_teacher(db:Session, email_address, phone_number):
    teacher_id = db.query(models.Teacher).filter(models.Teacher.email_address == email_address
                    ,   models.Teacher.phone_number == phone_number).first()
    if teacher_id != None:
        teacher_id = teacher_id.teacher_id
    else:
        return None
    print("teacher_id -> ", teacher_id)
    return db.query(models.ClientTeacherCourse).filter(
        models.ClientTeacherCourse.teacher_id == teacher_id)

def verify_student(db:Session, email_address, phone_number):
    student_id = db.query(models.Student).filter(models.Student.email_address == email_address
                    ,models.Student.phone_number == phone_number).first()
    if student_id != None:
        student_id = student_id.student_id
    else:
        return None
    print("student_id -> ", student_id)
    return student_id

def get_student_by_email_or_phone_num(db:Session, email_address, phone_number):
    # student_id = db.query(models.Student).filter(models.Student.email_address == email_address
    #                 ,models.Student.phone_number == phone_number).first()

    student = db.query(models.Student).filter(models.Student.email_address == email_address).first()

    if student == None:
        print("checking with phone number, since no entries found with email_address")
        student = db.query(models.Student).filter(models.Student.phone_number == phone_number).first()
        if student != None and student.favourite_teacher_id != None:
            print("Appending the fav teacher info")
            teacher_avt_obj = db.query(models.TeacherAvatar).filter(models.TeacherAvatar.teacher_avatar_id == student.favourite_teacher_id).first()
            student.favourite_teacher_name = teacher_avt_obj.name
            student.favourite_teacher_avatar_url = teacher_avt_obj.url
    else:
        if student != None and student.favourite_teacher_id != None:
            print("Appending the fav teacher info")
            teacher_avt_obj = db.query(models.TeacherAvatar).filter(models.TeacherAvatar.teacher_avatar_id == student.favourite_teacher_id).first()
            student.favourite_teacher_name = teacher_avt_obj.name
            student.favourite_teacher_avatar_url = teacher_avt_obj.url
    return student

def get_student_by_id(db:Session, student_id):
    student = db.query(models.Student).filter(models.Student.student_id == student_id).first()
    if student != None and student.favourite_teacher_id != None:
        print("Appending the fav teacher info")
        teacher_avt_obj = db.query(models.TeacherAvatar).filter(models.TeacherAvatar.teacher_avatar_id == student.favourite_teacher_id).first()
        student.favourite_teacher_name = teacher_avt_obj.name
        student.favourite_teacher_avatar_url = teacher_avt_obj.url
    return student

def update_student_fav_teacher_avatar(db: Session, student_id, favourite_teacher_id):
    db_request = db.query(models.Student).filter(models.Student.student_id == student_id).first()
    db_request.favourite_teacher_id = favourite_teacher_id
    db.commit()
    db.refresh(db_request)
    print("The updated student obj -> ", db_request)
    return db_request

def get_all_teacher_avatars(db: Session, skip: int = 0, limit: int = 100):
    teacherAvaList = db.query(models.VirtualAvatar).offset(skip).limit(limit).all()
    return teacherAvaList

def create_board(db: Session, board : schemas.CreateBoard):
    db_board = models.Board(board_id = board.board_id , board_name = board.board_name)
    #db_user = student
    db.add(db_board)
    db.commit()
    db.refresh(db_board)
    # print("The school details saved in database!!")
    return db_board


def create_standard(db: Session, create_standard : schemas.CreateStandard):

    standard = create_standard.age - 6
    # level = level.lower()
    if str(create_standard.level).lower() == 'basic':
            standard-=1
            # return standard
    elif str(create_standard.level).lower() == 'intermediate':
            pass
            # return standard
    elif str(create_standard.level).lower() == 'advanced':
            standard+=1
    else:
        print("Please Enter correct level")

    schemas.StandardResponse.standard = standard

    db_standard = models.Standard(standard_id = create_standard.standard_id, standard= schemas.StandardResponse.standard)
    db.add(db_standard)
    db.commit()
    db.refresh(db_standard)
    return db_standard

def upload_teacher_avatar(db : Session, teacher_avatar : schemas.TeacherAvatar):
    # user_data = db.query(models.TeacherAvatar).filter(models.TeacherAvatar.user_id == teacher_avatar.user_id).all()
    # for i in user_data:
    #     i.in_use=False
    user_data = db.query(models.TeacherAvatar).filter(models.TeacherAvatar.user_id == teacher_avatar.user_id,models.TeacherAvatar.in_use==1).first()
    user_data.in_use=False

    db.commit()

    db_teacher_avatar = models.TeacherAvatar(image_name= teacher_avatar.image_name,
        image_url = teacher_avatar.image_url, user_id = teacher_avatar.user_id, is_cartoon = teacher_avatar.is_cartoon,
        in_use = teacher_avatar.in_use
    )
    db.add(db_teacher_avatar)
    db.commit()
    db.refresh(db_teacher_avatar)
    return db_teacher_avatar

def upload_voice_sample(db : Session, voice: schemas.VoiceSample):
    # user_data = db.query(models.VoiceSample).filter(models.VoiceSample.user_id == voice.user_id).all()
    # for i in user_data:
    #     i.in_use=False
    user_data = db.query(models.VoiceSample).filter(models.VoiceSample.user_id == voice.user_id,models.VoiceSample.in_use==True).first()
    user_data.in_use=False

    db.commit()
    voice_sample = models.VoiceSample(voice_sample_name= voice.voice_sample_name,
        voice_sample_url = voice.voice_sample_url, user_id = voice.user_id, in_use = voice.in_use
    )
    db.add(voice_sample)
    db.commit()
    db.refresh(voice_sample)
    return voice_sample

def create_virtual_avatar(db : Session, virtual_avatar : schemas.VirtualAvatar):

    db_virtual_avatar = models.VirtualAvatar(name= virtual_avatar.name,
                                             profile_pic_link = virtual_avatar.profile_pic_link,
                                             audio_link = virtual_avatar.audio_link,
                                             description = virtual_avatar.description,
                                             is_active = virtual_avatar.is_active

                            )
    #db_user = student
    db.add(db_virtual_avatar)
    db.commit()
    db.refresh(db_virtual_avatar)
    return db_virtual_avatar


def create_course(db : Session, course : schemas.CreateCourse):

    authorized_client_id = db.query(models.Client).filter(models.Client.name == course.client_name).first()

    if authorized_client_id == None:
        raise HTTPException(status_code=400, detail="Invalid client_id, please create the client first")
    else:
        authorized_client_id = authorized_client_id.client_id

    course_id = db.query(models.Course).filter(models.Course.name == course.name).first()

    if course_id != None:
        raise HTTPException(status_code=400, detail="Course already created")

    db_course = models.Course(

        name = course.name,
        is_active = course.is_active,
        authorized_client_id = authorized_client_id
    )

    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    return db_course

def create_post(db : Session, post : schemas.CreatePost):

    user_id = db.query(models.User).filter(models.User.name == post.user_name).first()

    if user_id == None:
        raise HTTPException(status_code=400, detail="Invalid user_id, please create the user first")
    else:
        user_id = user_id.user_id

    db_post = models.Post(

        user_id = user_id,
        resource_url = post.resource_url,
        content_type = post.resource_url,
        caption = post.caption,
        creationDate = datetime.now(),
        like_count = post.like_count,
        comment_count = post.comment_count,
        share_count = post.share_count,
        view_count = post.view_count

    )

    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post

def create_stories(db : Session, stories : schemas.CreateStories):

    teacher_id = db.query(models.Teacher).filter(models.Teacher.name == stories.name).first()
    if teacher_id == None:
        raise HTTPException(status_code=400, detail="Invalid Teacher ID")
    else:
        teacher_id = teacher_id.teacher_id

    db_story = models.Stories(

        title = stories.title,
        description = stories.description,
        teacher_id = teacher_id,
        source_url = stories.source_url,
        creationDate = datetime.now()
    )

    db.add(db_story)
    db.commit()
    db.refresh(db_story)
    return db_story


def create_activity(db : Session, activity : schemas.CreateActivity):

    post_id = db.query(models.Post).filter(models.Post.post_id == activity.post_id).first()
    if post_id == None:
        raise HTTPException(status_code=400, detail="Invalid post ID")
    else:
        post_id = post_id.post_id

    db_activity = models.Activity(

        post_id = post_id,
        type = activity.type,
        creationDate = datetime.now()

    )

    db.add(db_activity)
    db.commit()
    db.refresh(db_activity)
    return db_activity


def like(db : Session, like : schemas.Like):

    activity_id = db.query(models.Activity).filter(models.Activity.activity_id == like.activity_id).first()
    if activity_id == None:
        raise HTTPException(status_code=400, detail="Invalid Activity ID")
    else:
        activity_id = activity_id.activity_id

    user_id = db.query(models.User).filter(models.User.name == like.user_name).first()
    if user_id == None:
        raise HTTPException(status_code=400, detail="Invalid USER ID")
    else:
        user_id = user_id.user_id

    db_like = models.Like(

        activity_id = activity_id,
        user_id = user_id,
        creationDate = datetime.now()

    )

    db.add(db_like)
    db.commit()
    db.refresh(db_like)
    return db_like

def share(db : Session, share : schemas.Share):

    activity_id = db.query(models.Activity).filter(models.Activity.activity_id == share.activity_id).first()
    if activity_id == None:
        raise HTTPException(status_code=400, detail="Invalid Activity ID")
    else:
        activity_id = activity_id.activity_id

    user_id = db.query(models.User).filter(models.User.name == share.user_name).first()
    if user_id == None:
        raise HTTPException(status_code=400, detail="Invalid USER ID")
    else:
        user_id = user_id.user_id

    db_share = models.Share(

        activity_id = activity_id,
        user_id = user_id,
        creationDate = datetime.now()

    )

    db.add(db_share)
    db.commit()
    db.refresh(db_share)
    return db_share


def view(db : Session, view : schemas.View):

    activity_id = db.query(models.Activity).filter(models.Activity.activity_id == view.activity_id).first()
    if activity_id == None:
        raise HTTPException(status_code=400, detail="Invalid Activity ID")
    else:
        activity_id = activity_id.activity_id

    user_id = db.query(models.User).filter(models.User.name == view.user_name).first()
    if user_id == None:
        raise HTTPException(status_code=400, detail="Invalid USER ID")
    else:
        user_id = user_id.user_id

    db_view = models.View(

        activity_id = activity_id,
        user_id = user_id,
        creationDate = datetime.now()

    )

    db.add(db_view)
    db.commit()
    db.refresh(db_view)
    return db_view


def comment(db : Session, command : schemas.Command):

    post_id = db.query(models.Post).filter(models.Post.post_id == command.post_id).first()
    if post_id == None:
        raise HTTPException(status_code=400, detail="Invalid post ID")
    else:
        post_id = post_id.post_id

    user_id = db.query(models.User).filter(models.User.name == command.user_name).first()
    if user_id == None:
        raise HTTPException(status_code=400, detail="Invalid USER ID")
    else:
        user_id = user_id.user_id

    db_command = models.Comment(

        post_id = post_id,
        user_id = user_id,
        text = command.text,
        creationDate = datetime.now()
    )

    db.add(db_command)
    db.commit()
    db.refresh(db_command)
    return db_command

def OCR_request_response(db: Session, reqres : schemas.RequestResponse):

    db_request_response = models.HertzOcrRequestResponse(

        StartTime = reqres.StartTime,
        EndTime = reqres.EndTime,
        Directory = reqres.Directory,
        FileName = reqres.FileName,
        TextResponse = reqres.TextResponse

    )

    db.add(db_request_response)
    db.commit()
    db.refresh(db_request_response)
    return db_request_response

def create_subject(db: Session, subjects : schemas.Subject):

    batch_id = db.query(models.Batch).filter(models.Batch.name == subjects.batch_name).first()
    if batch_id == None:
        raise HTTPException(status_code=400, detail="Invalid Client name, please register the Client first")
    else:
        batch_id = batch_id.batch_id

    student_id = db.query(models.Student).filter(models.Student.name == subjects.student_name).first()
    if student_id == None:
        raise HTTPException(status_code=400, detail="Invalid Student ID")
    else:
        student_id = student_id.student_id

    teacher_id = db.query(models.Teacher).filter(models.Teacher.name == subjects.teacher_name).first()
    if teacher_id == None:
        raise HTTPException(status_code=400, detail="Invalid Teacher ID")
    else:
        teacher_id = teacher_id.teacher_id

    db_subject = models.Subject(

        name = subjects.subject_name,
        batch_id = batch_id,
        student_id = student_id,
        teacher_id = teacher_id

    )

    db.add(db_subject)
    db.commit()
    db.refresh(db_subject)
    return db_subject

def create_layout(db: Session, layout : schemas.Layout):

    file_id = db.query(models.HertzOcrRequestResponse).filter(models.HertzOcrRequestResponse.FileName == layout.file_name).first()
    if file_id == None:
        raise HTTPException(status_code=400, detail="Invalid Client name, please register the Client first")
    else:
        file_id = file_id.FileID

    student_id = db.query(models.Student).filter(models.Student.name == layout.student_name).first()
    if student_id == None:
        raise HTTPException(status_code=400, detail="Invalid Student ID")
    else:
        student_id = student_id.student_id

    book_id = db.query(models.Book).filter(models.Book.name == layout.book_name).first()
    if book_id == None:
        raise HTTPException(status_code=400, detail="Invalid Teacher ID")
    else:
        book_id = book_id.book_id

    db_layout = models.Layout(

        file_id = file_id,
        student_id = student_id,
        book_id = book_id,
        publey_flag = layout.publey_flag,
    publey_processing_time = layout.publey_processing_time,
    Page_number = layout.page_number,
    Layout_number = layout.layout_number,
    num_of_bboxes_per_page = layout.num_of_bboxes_per_page,
    passage = layout.passage,
    topic_name = layout.topic_name,
    chapter_name = layout.chapter_name,

    )

    db.add(db_layout)
    db.commit()
    db.refresh(db_layout)
    return db_layout



def create_book(db: Session, book : schemas.Book):

    file_id = db.query(models.HertzOcrRequestResponse).filter(models.HertzOcrRequestResponse.FileName == book.file_name).first()
    if file_id == None:
        raise HTTPException(status_code=400, detail="Invalid Client name, please register the Client first")
    else:
        file_id = file_id.FileID

    student_id = db.query(models.Student).filter(models.Student.name == book.student_name).first()
    if student_id == None:
        raise HTTPException(status_code=400, detail="Invalid Student ID")
    else:
        student_id = student_id.student_id

    subject_id = db.query(models.Subject).filter(models.Subject.name == book.subject_name).first()
    if subject_id == None:
        raise HTTPException(status_code=400, detail="Invalid Teacher ID")
    else:
        subject_id = subject_id.subject_id

    db_book = models.Book(

        file_id = file_id,
        student_id = student_id,
        subject_id = subject_id,
        name = book.book_name,
        is_active = book.is_active,

    )

    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book







def create_cartoonimages(db:Session, cartoonimages: schemas.CartoonImages):
    db_cartoon = models.CartoonImages(
        image_name = cartoonimages.image_name,             
        image_url = cartoonimages.image_url,             
        delauney_triangulation = cartoonimages.delauney_triangulation ,
        open_mouth             = cartoonimages.open_mouth ,            
        close_mouth            = cartoonimages.close_mouth ,           
        scale_shift            = cartoonimages.scale_shift ,           
        is_active              = cartoonimages.is_active,                  
        image_bg_url           = cartoonimages.image_bg_url,  
        user_id                = cartoonimages.user_id,
    )
    db.add(db_cartoon)
    db.commit()
    db.refresh(db_cartoon)
    return db_cartoon


def get_all_cartoonimages_by_imagename(db:Session, image_name : str):
    Cartoon_Images = db.query(models.CartoonImages).filter(models.CartoonImages.image_name == image_name).all()
    return Cartoon_Images 

def get_all_cartoonimages_by_cartoonid(db:Session, cartoon_id : int):
    Cartoon_Image = db.query(models.CartoonImages).filter(models.CartoonImages.cartoon_id == cartoon_id).first()
    return Cartoon_Image 

def get_all_cartoonimages(db: Session, user_id: int, is_active: bool = True):
    CartoonImageList = db.query(models.CartoonImages).filter(models.CartoonImages.user_id == user_id , models.CartoonImages.is_active==is_active).all()
    return CartoonImageList 

def get_all_userimage(db: Session, user_id: int, is_active: bool = True):
    ImageList = db.query(models.TeacherAvatar).filter(models.TeacherAvatar.user_id == user_id , models.TeacherAvatar.is_active==is_active).all()
    return ImageList








