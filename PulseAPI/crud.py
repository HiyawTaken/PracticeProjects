from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func
import schemas, models

class DuplicateTargetError(Exception):
    pass

class TargetNotFoundError(Exception):
    pass

def get_target_from_url(db: Session, url: str):
    return db.query(models.Targets).filter(models.Targets.url == url).first()

def get_targets(db: Session):
    return db.query(models.Targets).all()

def find_target_from_name(db: Session, name: str):
    return db.query(models.Targets).filter(func.lower(models.Targets.name).like(f"%{name.lower()}%")).all()

def get_target_from_id(db: Session, id: int):
    return db.query(models.Targets).filter(models.Targets.id == id).first()

def create_target(db: Session, target: schemas.TargetBase):

    if get_target_from_url(db, target.url) is not None:
        raise DuplicateTargetError("Target already exists")

    db_target = models.Targets(name=target.name, url=target.url)
    db.add(db_target)
    db.commit()
    db.refresh(db_target)

    return db_target

def delete_target(db: Session, target_id: int):
    db_target = get_target_from_id(db, target_id)

    if db_target is None:
        raise TargetNotFoundError("Target not found")

    db.delete(db_target)
    db.commit()
    return db_target

def update_target(db: Session, target_id: int, target: schemas.TargetBase):
    db_target = get_target_from_id(db, target_id)

    if db_target is None:
        raise TargetNotFoundError("Target not found")

    db_target.name = target.name
    db_target.url = target.url


    db.commit()
    db.refresh(db_target)

    return db_target

def update_target_status(db: Session, target_id: int, status_code: int):
    db_target = get_target_from_id(db, target_id)

    if db_target is None:
        raise TargetNotFoundError("Target not found")

    db_target.status_code = status_code
    db_target.last_checked = datetime.utcnow()

    db.commit()
    db.refresh(db_target)
    return db_target
