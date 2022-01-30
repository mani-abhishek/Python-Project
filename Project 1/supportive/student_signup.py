# INSERT THIS IN models.py

class Student_Signup(Base):
    __tablename__ = "student"

    student_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    gender = Column(String(15), nullable=False)
    age = Column(Integer, nullable=False)
    school_id = Column(Integer, ForeignKey(School.school_id))
    authorized_client_id = Column(Integer, ForeignKey(Client.client_id))
    batch_id = Column(Integer, ForeignKey(batch.school_id))
    favorite_teacher_id = Column(Integer, ForeignKey(teacher_avatar.teacher_avatar_id))
    is_active = Column(Integer, default=0)
    email = Column(String(35), nullable=False)
    phone_number = Column(String(15), nullable=False)
    who_pays_for_course = Column(String(50), nullable=False)
    english_proficiency = Column(String(50), nullable=False)
    preferred_language =Column(String(25), nullable=False)

# INSERT THIS IN schemas.py

class Student_Signup(BaseModel):
    student_id:int
    name: str
    gender:str
    age:int
    school_id : int
    authorized_client_id : int
    batch_id = int
    favorite_teacher_id = int
    is_active : int
    email : str
    phone_number : str
    who_pays_for_course :str
    english_proficiency :str
    preferred_language :str
    class Config:
        orm_mode = True
        arbitrary_types_allowed = True

# INSERT THIS IN main.py

@controller.post("/create_student", tags=["Student_Signup"], response_model=schemas.Student_Signup)
def CreateStudent(student: schemas.Student_Signup, db: Session = Depends(get_db)):
    db_user = crud.get_student_by_name(db, name=student.name)
    if db_user:
        raise HTTPException(status_code=400, detail="Student already registered")
    return crud.create_teacher(db=db, student= student)

# INSERT THIS IN crud.py

def create_student(db: Session, student_signup: schemas.Student_Signup):
    
    school_id = db.query(models.School).filter(models.School.school_id == student_signup.school_id).first()
    if school_id == None:
        raise HTTPException(status_code=400, detail="Invalid assessment_name, please create the assessment first")
    else:
        school_id = school_id.school_id

    batch_id = db.query(models.Batch).filter(models.Batch.batch_id == student_signup.courses).first()
    if courses == None:
        raise HTTPException(status_code=400, detail="Invalid student_name, please register the student first")
    else:
        batch_id = batch_id.batch_id

    authorized_client_id = db.query(models.Client).filter(models.Client.client_id == student_signup.authorized_client_id).first()
    if authorized_client_id == None:
        raise HTTPException(status_code=400, detail="Invalid student_name, please register the student first")
    else:
        authorized_client_id = authorized_client_id.authorized_client_id

    favorite_teacher_id = db.query(models.teacher_avatar).filter(models.teacher_avatar.teacher_avatar_id == student_signup.favorite_teacher_id).first()
    if favorite_teacher_id == None:
        raise HTTPException(status_code=400, detail="Invalid student_name, please register the student first")
    else:
        favorite_teacher_id = favorite_teacher_id.favorite_teacher_id
    

    db_student_signup = models.Student_Signup(
                                student_id= student_signup.teacher_id,
                                name = student_signup.name,
                                gender = student_signup.gender,
                                age = student_signup.age,
                                school_id = school_id,
                                client_id = authorized_client_id,
                                batch_id = batch_id,
                                favorite_teacher_id = favorite_teacher_id,
                                is_active=student_signup.is_active,
                                email = student_signup.email,
                                phone_number = student_signup.phone_number,
                                who_pays_for_course = student_signup.who_pays_for_course,
                                english_proficiency = student_signup.english_proficiency,
                                preferred_language = student_signup.preferred_language

                                )
    db.add(db_student_signup)
    db.commit()
    db.refresh(db_student_signup)
    # db_assessment_result.assessment_name=assessment_result.assessment_name
    # db_assessment_result.student_name=assessment_result.student_name
    return db_student_signup