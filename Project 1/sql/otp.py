import random as r
from . import models
from sqlalchemy.orm import Session
import requests
from fastapi import Depends, FastAPI, HTTPException
from datetime import datetime
import json

provision_key = "vOZH33SBIna33g1mk5bAlHeNO0yjKeHB"

def get_access_token(url, client_id, client_secret):
    response = requests.post(
        url,
        data={"grant_type": "client_credentials"},
        auth=(client_id, client_secret),
    )
    return response.json()

# function for otp generation
def generate_otp():
    otp=""
    for i in range(4):
        otp+=str(r.randint(1,9))
    return otp

# function for saving otp in database
def save_otp(db: Session, phone_number, otp, user_id):
	push_otp = models.Otp(phone_number = phone_number, otp = otp, user_id = user_id)

	db.add(push_otp)
	db.commit()
	db.refresh(push_otp)

	return push_otp

def varify_otp(db: Session, phone_number:str, otp:str):
	res = db.query(models.Otp).filter(models.Otp.phone_number == phone_number).order_by(models.Otp.id.desc()).first()
	if res is None:
		raise HTTPException(status_code=404, detail="Phone number is wrong")

	elif res.otp == otp:
		time_delta = (datetime.now() - res.created_date)
		total_seconds = time_delta.total_seconds()
		minutes = int(total_seconds/60)
		if minutes > 10:
			raise HTTPException(status_code=400, detail="OTP Expired")
		user_data = db.query(models.User).filter(models.User.phone_number == phone_number).first()
		access_token = get_access_token("https://service.mcgroce.com/hertzai/oauth2/token", user_data.client_id, user_data.client_secret)
		access_token["user_id"] = res.user_id



		user_data = db.query(models.User).filter(models.User.phone_number == phone_number).first()
		data=models.User
		if not user_data.varified:
			db.query(data).filter(models.User.phone_number == phone_number).update({data.varified:True})

			db.commit()


		return access_token
	else:
		raise HTTPException(status_code=404, detail="Wrong OTP")
		# generate refresh token


def send_email(subject, message, email):
	headers = {'Content-Type': 'application/json'}
	email = email.strip()
	data = {
	"subject" : subject,
	"message" : message,
	"emailList" : [email]
	}
	requests.post("https://email.hertzai.com/sendEmail", data=json.dumps(data), headers=headers)
	print(email, " --------------------   success")
	return "SUCCESS"


def login(db: Session, phone_number:str):
	user =  db.query(models.User).filter(models.User.phone_number.ilike("%" + phone_number.strip() +  "%")).first()
	if user == None:
		raise HTTPException(status_code=400, detail="{} is not registered".format(phone_number))

	generated_otp = generate_otp()
	print(" *************************  generated otp : ", generated_otp)

	save = save_otp(db=db, phone_number=phone_number, otp = generated_otp, user_id = user.user_id)
	show_email = user.email_address.split("@")
	show_email1 = show_email[0][0:3] + "****@" + show_email[1]

	subject = "Security verification"
	email = user.email_address
	message = "Log In Security Verification: {} \n  For security reasons, this code will expire in 10 minutes. Please don't tell others.".format(generated_otp)
	email = send_email(subject=subject, message=message, email=email)

	return {"detail": "OTP sent to your email address {}".format(show_email1)}
