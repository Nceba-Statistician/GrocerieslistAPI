from fastapi import FastAPI, Depends, HTTPException
import uvicorn, datetime
from faker import Faker
from pydantic import BaseModel
from typing import List, Dict, Any
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import Session, sessionmaker, declarative_base
from sqlalchemy import DateTime
from typing import Optional

# Database Setup

sqlalchemy_database_url = "sqlite:///groceries.db"
engine = create_engine(
    sqlalchemy_database_url, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class DBGroceryItem(Base):
    __tablename__ = "groceries"
    
    Id = Column(String, primary_key=True, index=True)
    Item = Column(String, index=True)
    datestamp = Column(DateTime)
    
# Creating the table in the database file

Base.metadata.create_all(bind=engine) 

# Dependency to Get a Database Session

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
class GroceryItemCreate(BaseModel):
    Item: str

class GroceryItemUpdate(GroceryItemCreate):
    pass
    
class GroceryItem(BaseModel):
    Id: str
    Item: str
    datestamp: datetime.datetime
    
    class Config:
        from_attributes = True        

app = FastAPI()

@app.get("/")
async def default():
    return {"message": "Welcome to the Groceries API."}

@app.get("/getitems", response_model=List[GroceryItem])
async def pull_items(db: Session = Depends(get_db)):
    items = db.query(DBGroceryItem).all()
    return items

@app.post("/postitems", response_model=GroceryItem)
async def post_items(item_data: GroceryItemCreate, db: Session = Depends(get_db)):
    new_uuid = Faker().uuid4().lower()
    dates = datetime.datetime.now()
    db_item = DBGroceryItem(
        Id=new_uuid,
        Item=item_data.Item,
        datestamp=dates
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item) 
    return db_item

@app.put("/putitems/{item_id}", response_model=GroceryItem)
async def put_items(item_id: str, item_data: GroceryItemUpdate, db: Session = Depends(get_db)):
    db_item = db.query(DBGroceryItem).filter(DBGroceryItem.Id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail=f"Item with Id '{item_id}' not found")
    db_item.Item = item_data.Item

    db.commit()
    db.refresh(db_item)
    
    return db_item

@app.delete("/deleteitems/{item_id}") 
async def delete_items(item_id: str, db: Session = Depends(get_db)):
    db_item = db.query(DBGroceryItem).filter(DBGroceryItem.Id == item_id).first()
    
    if db_item is None:
        raise HTTPException(status_code=404, detail=f"Item with Id '{item_id}' not found")
    db.delete(db_item)
    db.commit()
    
    return f"Successfully delete the Item with Id {item_id}"
   
    
if __name__ == "__main__":
    uvicorn.run("grocerieslistitems:app", host="127.0.0.1", port=8001, reload=True) 