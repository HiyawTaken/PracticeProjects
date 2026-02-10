from sqlalchemy.orm import Session, session
from sqlalchemy import func
import models, schemas

def get_contacts(db: Session):
    return db.query(models.Contact).all()

def get_contact_by_id(db: Session, contact_id: int):
    return db.query(models.Contact).filter(models.Contact.id == contact_id).first()

def get_contact_by_phone(db: Session, phone: str):
    return db.query(models.Contact).filter(models.Contact.phone == phone).first()

def find_contact_by_phone(db: Session, phone: str):
    return db.query(models.Contact).filter(models.Contact.phone.like(f"%{phone}%")).all()

def get_contact_by_name(db: Session, name: str):
    return db.query(models.Contact).filter(func.lower(models.Contact.name).like(f"%{name.lower()}%")).all()

def create_contact(db: Session, contact: schemas.UserBase):
    db_contact = models.Contact(name=contact.name, phone=contact.phone, email=contact.email)
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)

    return db_contact

def delete_contact(db: Session, contact: schemas.UserResponse):
    db.delete(contact)
    db.commit()

def update_contact(db: Session, contact: schemas.UserResponse, updated_contact: schemas.UserBase):
    contact.name = updated_contact.name
    contact.phone = updated_contact.phone
    contact.email = updated_contact.email
    db.commit()
    db.refresh(contact)
    return contact
