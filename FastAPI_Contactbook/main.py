from typing import List

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from database import SessionLocal, get_db, engine
from sqlalchemy.orm import Session
import models, schemas, crud
import re

#create tables of the database if it doesn't exist
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Allows all origins for the backend to connect with our frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def normalize_phone(phone):
    return re.sub("[^0-9]", "", phone)

@app.get("/contacts/search", response_model=List[schemas.UserResponse])
def search_contact(
    phone: str | None = None,
    name: str | None = None,
    db: Session = Depends(get_db)
):
    if phone:
        return crud.find_contact_by_phone(db, normalize_phone(phone))
    if name:
        return crud.get_contact_by_name(db, name)
    raise HTTPException(status_code=400, detail="Provide phone or name")

@app.get("/contacts", response_model=List[schemas.UserResponse])
def get_contacts(db: Session = Depends(get_db)):
    return crud.get_contacts(db)

@app.get("/contacts/{user_id}", response_model=schemas.UserResponse)
def read_contact_by_id(user_id: int, db: Session = Depends(get_db)):
    db_contact = crud.get_contact_by_id(db, user_id)
    if db_contact:
        return db_contact
    else:
        raise HTTPException(status_code=404, detail="Contact not found")

@app.post("/contacts", response_model=schemas.UserResponse)
def create_contact(contact: schemas.UserBase, db: Session = Depends(get_db)):

    #check if contact already exists
    db_contact = crud.get_contact_by_phone(db, contact.phone)
    if db_contact:
        if contact.email == "":
            contact.email = None
        raise HTTPException(status_code=400, detail="Contact already exists")

    contact.phone = normalize_phone(contact.phone)

    return crud.create_contact(db, contact)

@app.put("/contacts/{user_id}", response_model=schemas.UserResponse)
def update_contact(user_id: int, updated_contact: schemas.UserBase, db: Session = Depends(get_db)):
    db_contact = crud.get_contact_by_id(db, user_id)
    if db_contact:
        db_contact.phone = normalize_phone(updated_contact.phone)
        if db_contact.email == "":
            db_contact.email = None
        if updated_contact.email == "":
            updated_contact.email = None
        updated_contact.phone = normalize_phone(updated_contact.phone)
        return crud.update_contact(db, db_contact, updated_contact)
    else:
        raise HTTPException(status_code=404, detail="Contact not found")

@app.delete("/contacts/{user_id}")
def delete_contact(user_id: int, db: Session = Depends(get_db)):
    db_contact = crud.get_contact_by_id(db, user_id)
    if db_contact:
        crud.delete_contact(db, db_contact)
        return {"detail": "Contact deleted"}
    else:
        raise HTTPException(status_code=404, detail="Contact not found")



