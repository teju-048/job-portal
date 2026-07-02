# pyrefly: ignore [missing-import]
from sqlalchemy import Column, Integer, String
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True)
    password = Column(String)
    role = Column(String)


class CandidateProfile(Base):
    __tablename__ = "candidate_profiles"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String)
    skills = Column(String)
    education = Column(String)
    experience = Column(Integer)
    certifications = Column(String)
    languages = Column(String)
    assessment_score=Column(Integer,default=0)

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String)
    description = Column(String)
    skills = Column(String)
    experience_required = Column(Integer)

    company=Column(String)
    salary = Column(String)
    location = Column(String)
    job_type = Column(String)


class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)

    candidate_name = Column(String)
    job_title = Column(String)

class Assessment(Base):
    __tablename__ = "assessments"

    id = Column(Integer, primary_key=True)

    candidate_name = Column(String)

    score = Column(Integer)

class ShortlistedCandidate(Base):
    __tablename__ = "shortlisted"

    id = Column(Integer, primary_key=True, index=True)

    candidate_name = Column(String)
    job_title = Column(String)