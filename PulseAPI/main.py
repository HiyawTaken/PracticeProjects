from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from crud import TargetNotFoundError
from database import get_db, engine
from sqlalchemy.orm import Session
import models, schemas, crud, scanner


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

@app.get("/targets/search")
def search_targets(name:str, db: Session = Depends(get_db)):
    return crud.find_target_from_name(db, name)

@app.get("/targets")
def get_targets(db: Session = Depends(get_db)):
    return crud.get_targets(db)

@app.get("/targets/{target_id}")
def get_a_target(target_id: int, db: Session = Depends(get_db)):
    return crud.get_target_from_id(db, target_id)

@app.post("/scan")
def scan_targets(db: Session = Depends(get_db)):

    targets = crud.get_targets(db)
    list_targets = [str(t.url) for t in targets]
    url_to_id = {t.url: t.id for t in targets}

    updated_status = scanner.monitor(list_targets)

    for url, status_code in updated_status.items():
            crud.update_target_status(db, url_to_id.get(url), status_code)

    return {"message": f"Scanned and updated {len(list_targets)} targets"}

@app.post("/targets")
def create_target(target: schemas.TargetBase, db: Session = Depends(get_db)):

     #check if target already exists
    db_target = crud.get_target_from_url(db, target.url)
    if db_target:
         raise HTTPException(status_code=400, detail="Target already exists")

    return crud.create_target(db, target)

@app.put("/targets/{target_id}")
def update_target(target_id: int, target: schemas.TargetBase, db: Session = Depends(get_db)):
    return crud.update_target(db, target_id, target)

@app.delete("/targets/{target_id}")
def delete_target(target_id: int, db: Session = Depends(get_db)):
    return crud.delete_target(db, target_id)
