# INSERT THIS IN models.py

class Teacher_Signup(Base):
    __tablename__ = "teacher"

    teacher_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(25), nullable=False)
    address = Column(String(100), nullable=False)
    school_id = Column(Integer, ForeignKey(School.school_id))
    authorized_client_id = Column(Integer, ForeignKey(Client.client_id))
    courses = Column(Integer, ForeignKey(Course.course_id))
    is_active = Column(Integer, default=0)
    email = Column(String(35), nullable=False)
    phone_number = Column(String(15), nullable=False)

# INSERT THIS IN schemas.py

class Teacher_Signup(BaseModel):
    teacher_id:int
    name: str
    address: str
    school_id : int
    authorized_client_id : int
    courses : int
    is_active : int
    email : str
    phone_number : str
    class Config:
        orm_mode = True
        arbitrary_types_allowed = True

# INSERT THIS IN main.py

@controller.post("/create_teacher", tags=["Teacher_Signup"], response_model=schemas.Teacher_Signup)
def CreateTeacher(teacher: schemas.Teacher_Signup, db: Session = Depends(get_db)):
    db_user = crud.get_teacher_by_name(db, name=teacher.name)
    if db_user:
        raise HTTPException(status_code=400, detail="Client already registered")
    return crud.create_teacher(db=db, teacher= teacher)

# INSERT THIS IN crud.py

def create_teacher(db: Session, teacher_signup: schemas.Teacher_Signup):
    
    school_id = db.query(models.School).filter(models.School.school_id == teacher_signup.school_id).first()
    if school_id == None:
        raise HTTPException(status_code=400, detail="Invalid school id")
    else:
        school_id = school_id.school_id

    courses = db.query(models.Course).filter(models.Course.course_id == teacher_signup.courses).first()
    if courses == None:
        raise HTTPException(status_code=400, detail="Invalid course id")
    else:
        course_id = course_id.course_id

    client_id = db.query(models.Client).filter(models.Client.client_id == teacher_signup.authorized_client_id).first()
    if client_id == None:
        raise HTTPException(status_code=400, detail="Invalid client id")
    else:
        client_id = client_id.client_id

    db_teacher_signup = models.Teacher_Signup(
                                teacher_id= teacher_id,
                                name = assessment_result.name,
                                address = assessment_result.address,
                                school_id = school_id,
                                authorized_client_id = authorized_client_id,
                                courses = courses,
                                is_active=assessment_result.is_active,
                                email = assessment_result.email,
                                phone_number = assessment_result.phone_number,

                                )
    db.add(db_teacher_signup)
    db.commit()
    db.refresh(db_teacher_signup)
    # db_assessment_result.assessment_name=assessment_result.assessment_name
    # db_assessment_result.student_name=assessment_result.student_name
    return db_teacher_signup