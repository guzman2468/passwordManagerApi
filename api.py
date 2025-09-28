from pydantic import BaseModel
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
import os
# from dotenv import load_dotenv
# import certifi
import encryption_utils

# load_dotenv()
# #retrieves database connection string from Render environment variables
mongo_uri = os.environ.get("MONGO_URI")
#loads env to local machine

app = FastAPI()
client = MongoClient(mongo_uri)

db = client["password_manager"]
collection = db["details"]

class Website(BaseModel):
    site_name: str
    site_username: str = None
    site_password: str = None


class User(BaseModel):
    username: str
    password: str
    websites: Optional[List[Website]] = None

@app.get("/")
def root():
    return {"Hello" : "World"}


@app.post("/api/accountCreate")
def accountCreate(user: User):
    if user.username.strip() == "" or user.password.strip == "":
        raise HTTPException(status_code=400, detail="All fields must be filled")
    if len(user.username) < 4 or len(user.password) < 4:
        raise HTTPException(status_code=400, detail="Username and password must be at least 4 characters long")

    existing_user = collection.find_one({"initial_username" : user.username})

    if existing_user:
        raise HTTPException(status_code=400, detail="Username is already taken")

    document = ({
        "initial_username" : user.username,
        "initial_password" : encryption_utils.encrypt_password(user.password),
        "websites" : []
    })

    collection.insert_one(document)
    return {"message" : "Account created successfully"}

@app.post("/api/login")
def login(user: User):
    existing_user = collection.find_one({"initial_username": user.username})

    if not existing_user:
        raise HTTPException(status_code=400, detail="Username not found")

    encrypted_password = existing_user["initial_password"]
    decrypted_password = encryption_utils.decrypt_password(encrypted_password)

    if decrypted_password != user.password:
        raise HTTPException(status_code=400, detail="Incorrect password")
    return {"message" : "placeholder"}


@app.get("/api/searchSites")
def searchSites(user: User):
    '''
    This endpoint is called only after the user successfully logs in
    ensuring that data is protected and searching sites cannot occur before this
    :param user: User JSON object that has the username, password (both required), and site_name (optional)
    :return: JSON object showing the name, username, and password for the website given
    '''
    existing_user = collection.find_one({"initial_username": user.username},
                                        {"websites": 1})
    if not existing_user:
        raise HTTPException(status_code=400, detail="No user found with those credentials")
    if "websites" not in existing_user:
        raise HTTPException(status_code=400, detail="No websites found for user. Please add website.")

    for website in existing_user["websites"]:
        if user.websites[0].site_name == None:
            return {"message" : "site_name is missing"}
        if website["name"].lower() == user.websites[0].site_name.lower():
            decrypted_password = encryption_utils.decrypt_password(website["password"])
            return {
                "website_name" : website["name"],
                "website_username" : website["username"],
                "website_password" : decrypted_password
            }
    raise HTTPException(status_code=404, detail="Given site not found for this user.")
    return {"message" : "reached end of searchSites"}



@app.post("/api/addSite")
def addSite(user: User):
    '''
    This endpoint takes in the User JSON object and parses through the list user.websites
    to get the site_name, site_username, and site_password all while verifying the site does not
    exist yet in the database
    :param user: JSON object taken in to parse through for site details
    :return: response message indicating if the operation was success
    '''
    existing_user = collection.find_one(
        {"initial_username": user.username},
        {"websites": 1}
    )
    if not existing_user:
        raise HTTPException(status_code=400, detail="No user found with those credentials")

    if not user.websites or user.websites[0].site_name is None:
        raise HTTPException(status_code=400, detail="websites.site_name is missing")

    new_site_name = user.websites[0].site_name

    for website in existing_user.get("websites", []):
        if website["name"] == new_site_name:
            raise HTTPException(
                status_code=400,
                detail="Website already entered. Please choose a new site to add."
            )

    new_site = {
        "name": new_site_name,
        "username": user.websites[0].site_username,
        "password": encryption_utils.encrypt_password(user.websites[0].site_password),
    }

    collection.update_one(
        {"initial_username": user.username},
        {"$push": {"websites": new_site}}
    )

    return {"message": "Website added successfully"}

