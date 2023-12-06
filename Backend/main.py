from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
import uvicorn
import jsonify
from bson.json_util import dumps
from fastapi.middleware.cors import CORSMiddleware
from bson import ObjectId
import bcrypt
from model import UserCredentials,UserCreate,Leg,Strategy,Signal,password,strategyData,Roles,Instrument,Profile,forget,resetDetail,emailformat
import jwt
from typing import Optional 
from datetime import datetime, timedelta
import binascii
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import secrets
import datetime
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from jinja2 import Template 
from typing import List  # Import List from typing module
from constant import SENDER_EMAIL,SENDER_PASSWORD,SECRET_KEY,ALGORITHM,encryptionKey,encryptionKey1,encryptionKey2,encryptionKey3,iv,iv1,iv2,iv3


app = FastAPI()

templates = Jinja2Templates(directory="templates")

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


origins = [
    "http://localhost",
    "http://localhost:3000",
    "https://example.com",
    "http://localhost:3000/login",
    "http://localhost:3000/signup",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
client = MongoClient("mongodb://localhost:27017/")
db = client["online_shopping"]
users_collection = db["users"]


token_storage = {}


def generate_token():
    return secrets.token_urlsafe(32)

# Function to create an access token
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.datetime.utcnow() + expires_delta
    else:
        expire = datetime.datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# api for login page
@app.post("/login")
async def login(user_credentials: UserCredentials):
    username = user_credentials.username
    password = user_credentials.password

    # Query the database for the user
    user = users_collection.find_one({"username": username})
    checked=bcrypt.checkpw(user_credentials.password.encode('utf-8'), user['password'].encode('utf-8'))

    # Check if user exists and verify the password
    if user and checked:
        access_token = create_access_token(data={"sub": username})
        user['token']=access_token
        user['clientId']=decrypt_data(user['clientId'],encryptionKey3,iv3)
        return dumps(user)
    else:
        raise HTTPException(status_code=401, detail="Invalid username or password")

# api for register
@app.post("/register")
async def register(user: UserCreate):
    # Check if the username is already taken
    existing_user = users_collection.find_one({"username": user.username})
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), salt)    # Create a new user document
    new_user = {
        "email": user.email,
        "password": hashed_password.decode('utf-8'),
        "date_of_birth": user.date_of_birth,
        "full_name": user.full_name,
        "address":user.address,
        "username":user.username,
        "roles":"user"
    }
    sender_email=SENDER_EMAIL
    sender_password=SENDER_PASSWORD
    # sender_email = "codeway.skill@gmail.com"  # Replace with your own email address
    # sender_password = "msqgjgltgorjrqlm"  # Replace with your email password
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = user.email
    message["Subject"] = " Welcome to Fprognos.com - Your Journey with Damyant Fintech Begins Here!"
    
    with open("templates/welcome.html") as file:
        template = Template(file.read())

    html_content = template.render(username=user.username)
   
    message.attach(MIMEText(html_content, "html"))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        default_role = roles_collection.find_one({"name": "user"})
        if not default_role:
            raise HTTPException(status_code=500, detail="Default role not found.")
        new_user["roles"][0]=str(default_role["_id"])
        print(new_user,new_user['roles'])
        users_collection.insert_one(new_user)
        server.sendmail(sender_email, user.email, message.as_string())
        server.quit()
      
        return {"message": "user registered successfully!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"message": "User registered successfully"}


#api for get instrument
@app.get('/roles')
async def get_roles():
    data = list(roles_collection.find({}))
    return dumps(data)


# api for fetch particular detail of any user id
@app.get("/users/{id}")
async def get_detail_id(id: str):
    data = users_collection.find({"_id": ObjectId(id)})
    return dumps(data)


#api for update the password
@app.patch("/update_password/{id}")
async def update_password(id: str, password:password):
    # Query the database for the user
    result = users_collection.update_one({"_id": ObjectId(id)}, {"$set": {"password":password.password}})
    # Check if the update was successful
    if result.modified_count > 0:
        return {"message": "Profile Password Update Successful"}
    else:
        raise HTTPException(status_code=404, detail="User not found")

#api for update the profile
@app.patch("/update_profile/{id}")
async def update_profile(id: str, profile: Profile):
    detail = {
        "email": profile.email,
        "full_name": profile.full_name,
        "dob": profile.dob,
        "secret_key":encrypt_data(profile.secret_key,encryptionKey1,iv1),
        "api_key": encrypt_data(profile.api_key,encryptionKey3,iv3),
        "broker_name": profile.broker_name,
        "totp":encrypt_data(profile.totp,encryptionKey,iv),
        "acc_password":encrypt_data(profile.acc_password,encryptionKey2,iv2),
        "clientId":encrypt_data(profile.clientId,encryptionKey3,iv3),
    }
    user_detail=users_collection.find_one({"_id": ObjectId(id)})
    # if user_detail['profileCompleted'] is not True:
    #     print("download session is running now")
    #     url = f"http://0.0.0.0:9090/zw/api/download_session/{id}"
    #     response = axios.get(url)
    # Query the database for the user
    result = users_collection.update_one({"_id": ObjectId(id)}, {"$set": detail})
    # Check if the update was successful
    if result.modified_count > 0:
        return {"message": "Profile Update Successfully"}
    else:
        raise HTTPException(status_code=404, detail="User not found")




#api for handle rest password
@app.post("/reset_password/{username}/{token}")
async def reset_password(password:password):
    # Create a new user document
    users_collection.update({"username":username},{"$set": {"password":password.password}})
    # Insert the new user document into the MongoDB collection

    # Check if the update was successful
    if result.modified_count > 0:
        return {"message": "Profile Password Update Successful"}
    else:
        raise HTTPException(status_code=404, detail="User not found")


@app.post("/forget_password")
async def request_password_reset(emailformat:emailformat):
    email=emailformat.email
    username=emailformat.username
    # Check if the email exists in your user database (you should implement this logic)
    # If the email doesn't exist, return an appropriate response or raise an HTTPException.
    # Generate and store a new token for the user
    token = generate_token()
    expiration_time = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    token_storage[email] = {"token": token, "expires_at": expiration_time}

    sender_email=SENDER_EMAIL
    sender_password=SENDER_PASSWORD
    # sender_email = "codeway.skill@gmail.com"  # Replace with your own email address
    # sender_password = "msqgjgltgorjrqlm"  # Replace with your email password

    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = email
    message["Subject"] = "Password Reset Link - Action Required"
    # HTML content for the email
    with open("templates/resetPassword.html") as file:
        template = Template(file.read())

    html_content = template.render(token=token, email=email, username=username)
 
    message.attach(MIMEText(html_content, "html"))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, email, message.as_string())
        server.quit()
        return {"message": "Password reset email sent successfully!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/reset_password")
async def reset_password(resetDetail:resetDetail):
    # Check if the email exists in your user database (you should implement this logic)
    # If the email doesn't exist, return an appropriate response or raise an HTTPException.

    email:resetDetail.email
    token:resetDetail.token
    password:resetDetail.password

    # Check if the token is valid and not expired
    if email in token_storage and token_storage[email]["token"] == token:
        if datetime.datetime.utcnow() < token_storage[email]["expires_at"]:
            # Reset the user's password (you should implement this logic)
            # For example, update the user's password in the database with the new_password.
            result = users_collection.update_one({"email": email}, {"$set": {"password":password}})
            # Remove the token from the storage after it's used for security purposes
            del token_storage[email]
            return {"message": "Password reset successful!"}
        else:
            raise HTTPException(status_code=400, detail="Token has expired.")
    else:
        raise HTTPException(status_code=400, detail="Invalid email or token.")


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=5000, reload=True)