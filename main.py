from fastapi import FastAPI, Query
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base
import requests
from bs4 import BeautifulSoup

app = FastAPI()

# Database Setup (SQLite by default, update for PostgreSQL)
DATABASE_URL = "sqlite:///./leads.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database Model
class Lead(Base):
    __tablename__ = "leads"
    id = Column(Integer, primary_key=True, index=True)
    business_name = Column(String, index=True)
    location = Column(String)
    phone = Column(String)
    website = Column(String)

Base.metadata.create_all(bind=engine)

# Web Scraper Function
def scrape_businesses(industry: str, location: str):
    url = f"https://www.yelp.com/search?find_desc={industry}&find_loc={location}"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    businesses = []
    for biz in soup.select(".businessName__09f24__3Wql2"):
        name = biz.get_text()
        businesses.append({"business_name": name, "location": location})
    
    return businesses

# API Endpoint to Scrape Leads
@app.get("/scrape/")
def scrape(industry: str = Query(...), location: str = Query(...)):
    leads = scrape_businesses(industry, location)
    db = SessionLocal()
    for lead in leads:
        db_lead = Lead(**lead)
        db.add(db_lead)
    db.commit()
    db.close()
    return {"leads": leads}

# API Endpoint to Get Stored Leads
@app.get("/leads/")
def get_leads():
    db = SessionLocal()
    leads = db.query(Lead).all()
    db.close()
    return {"leads": leads}
