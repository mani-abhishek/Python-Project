# INSERT THIS IN models.py

class Book_Upload(Base):
    __tablename__ = "book"

    name = Column(String(50), nullable=False)
    email = Column(String(35), nullable=False)
    no_of_students =Column(Integer, nullable=False)

# INSERT THIS IN schemas.py

class Book_Upload(BaseModel):
    name: str
    email : str
    no_of_students : int
    class Config:
        orm_mode = True
        arbitrary_types_allowed = True

# INSERT THIS IN main.py

@controller.post("/create_business_signup", tags=["business_Signup"], response_model=schemas.Business_Signup)
def CreateBusinessSignup(business: schemas.Business_Signup, db: Session = Depends(get_db)):
    db_user = crud.get_business(db, name=business.name)
    if db_user:
        raise HTTPException(status_code=400, detail="Business ID already registered")
    return crud.create_business_signup(db=db, business= business)

# INSERT THIS IN crud.py

def create_business_signup(db: Session, business_signup: schemas.Business_Signup):
    
    db_business_signup = models.Business_Signup(
                                name = business_signup.name,
                                email = business_signup.email,
                                no_of_students = business_signup.preferred_language

                                )
    db.add(db_business_signup)
    db.commit()
    db.refresh(db_business_signup)
    return db_business_signup

