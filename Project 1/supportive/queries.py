"""
1. fetch paragraphs by topic name and student id

2. topics based on chapter name and studentid

3. chapters based on student id and bookname

4. subjects based on studentid

5. book names based on subject and studentid

6. Virtual and real teachers based on student id

student_virtual - 3NF
contains students FK

teacher_virtual - 3NF
contains teacher FK

pre_synthesized_fillers
PK - AI
link to pre synthesized
action
virtual avatar id FK
isactive


*virtual_avatar*
primary_key
student_id FK
name
profile_pic_link
audio_link
description
enable or not

post and stories - gurunameh

uploading book - giri


7. subjects based on teacher ids.
"""


# No column named subject, virtual and real teachers
# should I create FK of student_id whereever i needed?
 
from sql import models

def fetch_paragraph(db: Session, student_id: int, topic_name: str):
    return db.query(models.Layout).filter(models.Layout.topic_name == topic_name and models.Layout.student_id == student_id).all()

def fetch_topics(db: Session, student_id: int, chapter_name: str):
    return db.query(models.Layout).filter(models.Layout.chapter_name == chapter_name and models.Layout.student_id == student_id).all()

def fetch_chapters(db: Session, student_id: int, book_name: str):
    return db.query(models.Layout).filter(models.Layout.book_name == book_name and models.Layout.student_id == student_id).all()

def fetch_subjects(db: Session, student_id: int):
    return db.query(models.Layout).filter(models.Layout.student_id == student_id).all()

def fetch_booknames(db: Session, student_id: int, topic_name: str):
    return db.query(models.Layout).filter(models.Layout.topic_name == topic_name and models.Layout.student_id == student_id).all()

def fetch_virtual_and_real_teacher(db: Session, student_id):
    return db.query(models.Layout).filter(models.Layout.topic_name == topic_name and models.Layout.student_id == student_id).all()

def fetch_subjects(db: Session, teacher_id: int):
    return db.query(models.Layout).filter(models.Layout.topic_name == topic_name and models.Layout.student_id == student_id).all()

