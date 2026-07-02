from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

import models
from models import Base

from database import engine, SessionLocal

app = FastAPI()

Base.metadata.create_all(bind=engine)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- HOME ----------------

@app.get("/")
def home():
    return {"message": "Intelligent Job Portal"}


# ---------------- REGISTER ----------------

class User(BaseModel):
    name: str
    email: str
    password: str
    role: str

@app.post("/register")
def register(user: User):

    db = SessionLocal()

    existing_user = db.query(models.User).filter(
        models.User.email == user.email
    ).first()

    if existing_user:

        db.close()

        return {
            "message": "Email already exists"
        }

    new_user = models.User(
        name=user.name,
        email=user.email,
        password=user.password,
        role=user.role
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    db.close()

    return {
        "message": "User Registered Successfully"
    }

# ---------------- LOGIN ----------------

class Login(BaseModel):
    email: str
    password: str

@app.post("/login")
def login(data: Login):

    db = SessionLocal()

    user = db.query(models.User).filter(
        models.User.email == data.email,
        models.User.password == data.password
    ).first()

    db.close()

    if user:

        return {
            "message": "Login Successful",
            "email": user.email,
            "role": user.role,
            "name":user.name
        }

    return {
        "message": "Invalid Email or Password"
    }


# ---------------- CANDIDATE PROFILE ----------------

class CandidateProfile(BaseModel):
    name: str
    skills: List[str]
    education: str
    experience: int
    certifications: List[str]
    languages: List[str]

@app.post("/candidate/profile")
def create_profile(profile: CandidateProfile):

    db = SessionLocal()

    candidate = models.CandidateProfile(
        name=profile.name,
        skills=",".join(profile.skills),
        education=profile.education,
        experience=profile.experience,
        certifications=",".join(profile.certifications),
        languages=",".join(profile.languages)
    )

    db.add(candidate)
    db.commit()
    db.refresh(candidate)

    db.close()

    return {
        "message":"Profile Created Successfully"
    }


# ---------------- JOBS ----------------

class Job(BaseModel):
    title: str
    description: str
    skills: List[str]
    experience_required: int
    company: str
    salary: str
    location: str
    job_type: str


@app.post("/jobs")
def create_job(job: Job):

    db = SessionLocal()

    new_job = models.Job(
        title=job.title,
        description=job.description,
        skills=",".join(job.skills),
        experience_required=job.experience_required,
        company=job.company,
        salary=job.salary,
        location=job.location,
        job_type=job.job_type
    )

    db.add(new_job)
    db.commit()

    db.close()

    return {
        "message": "Job Posted Successfully"
    }


@app.get("/jobs")
def get_jobs():

    db = SessionLocal()

    try:

        jobs = db.query(models.Job).all()

        output = []

        for job in jobs:

            output.append({
                "title": job.title,
                "description": job.description,
                "skills": job.skills,
                "experience_required": job.experience_required,
                "company": job.company,
                "salary": job.salary,
                "location": job.location,
                "job_type": job.job_type
            })

        return output

    except Exception as e:

        return {
            "error": str(e)
        }

    finally:

        db.close()

# ---------------- RELIABILITY SCORE ----------------

class ReliabilityInput(BaseModel):
    candidate_name: str

@app.post("/reliability-score")
def calculate_score(data: ReliabilityInput):

    db = SessionLocal()

    candidate = db.query(
        models.CandidateProfile
    ).filter(
        models.CandidateProfile.name ==
        data.candidate_name
    ).first()

    if not candidate:
        db.close()
        return {
            "message": "Candidate Not Found"
        }

    assessment_score = (
        candidate.assessment_score or 0
    )

    experience_score = min(
        (candidate.experience or 0) * 10,
        100
    )

    certification_score = 100 if (
        candidate.certifications and
        candidate.certifications.strip()
    ) else 0

    profile_score = 0

    if candidate.skills:
        profile_score += 25

    if candidate.education:
        profile_score += 25

    if candidate.languages:
        profile_score += 25

    if candidate.certifications:
        profile_score += 25

    reliability_score = int(
        (assessment_score * 0.70)
        +
        (experience_score * 0.10)
        +
        (certification_score * 0.05)
        +
        (profile_score * 0.15)
    )

    db.close()

    return {
        "reliability_score": reliability_score
    }
# ---------------- MATCH SCORE ----------------

class MatchInput(BaseModel):
    matched_skills: int
    total_skills: int

@app.post("/match-score")
def calculate_match(data: MatchInput):

    score = (data.matched_skills / data.total_skills) * 100

    return {
        "match_score": score
    }
# ---------------- ASSESSMENT ----------------

class AssessmentInput(BaseModel):
    candidate_name: str
    score: int

@app.post("/assessment")
def save_assessment(data: AssessmentInput):

    db = SessionLocal()

    candidate = db.query(
        models.CandidateProfile
    ).filter(
        models.CandidateProfile.name ==
        data.candidate_name
    ).first()

    if candidate:

        candidate.assessment_score = data.score

        db.commit()

    db.close()

    return {
        "message": "Assessment Saved"
    }
# ---------------- RECOMMENDATIONS ----------------
def calculate_reliability(candidate):

    assessment_score = (
        candidate.assessment_score or 0
    )

    experience_score = min(
        (candidate.experience or 0) * 10,
        100
    )

    certification_score = 100 if (
        candidate.certifications and
        candidate.certifications.strip()
    ) else 0

    profile_score = 0

    if candidate.skills:
        profile_score += 25

    if candidate.education:
        profile_score += 25

    if candidate.languages:
        profile_score += 25

    if candidate.certifications:
        profile_score += 25

    reliability_score = int(

        (assessment_score * 0.70)

        +

        (experience_score * 0.10)

        +

        (certification_score * 0.05)

        +

        (profile_score * 0.15)

    )

    return min(reliability_score, 100)
@app.get("/recommendations/{candidate_name}")
def get_recommendations(candidate_name: str):

    try:

        db = SessionLocal()

        candidate = db.query(
            models.CandidateProfile
        ).filter(
            models.CandidateProfile.name ==
            candidate_name
        ).first()

        if not candidate:

            db.close()

            return {
                "message": "Candidate Not Found",
                "recommended_jobs": []
            }

        candidate_skills = set()

        if candidate.skills:

            candidate_skills = {

                skill.strip().lower()

                for skill in candidate.skills.split(",")

            }

        jobs = db.query(
            models.Job
        ).all()

        recommendations = []

        reliability_score = calculate_reliability(
            candidate
        )

        # ---------------- TRUST BADGE ----------------

        if reliability_score >= 85:

            badge = "🏆 Platinum Trust"

            trust_level = (
                "Highly Reliable Candidate"
            )

        elif reliability_score >= 70:

            badge = "🥇 Gold Trust"

            trust_level = (
                "Reliable Candidate"
            )

        elif reliability_score >= 55:

            badge = "🥈 Silver Trust"

            trust_level = (
                "Moderately Reliable Candidate"
            )

        else:

            badge = (
                "⚠ Needs Improvement"
            )

            trust_level = (
                "Low Reliability Candidate"
            )

        for job in jobs:

            job_skills = set()

            if job.skills:

                job_skills = {

                    skill.strip().lower()

                    for skill in job.skills.split(",")

                }

            matched_skills = (
                candidate_skills.intersection(
                    job_skills
                )
            )

            if len(job_skills) > 0:

                match_score = int(
                    (
                        len(matched_skills)
                        /
                        len(job_skills)
                    ) * 100
                )

            else:

                match_score = 0

            # Experience Match

            if (
                job.experience_required
                and
                job.experience_required > 0
            ):

                experience_match = min(
                    int(
                        (
                            candidate.experience
                            /
                            job.experience_required
                        ) * 100
                    ),
                    100
                )

            else:

                experience_match = 100

            # Overall Score

            overall_score = int(

                (match_score * 0.6)

                +

                (experience_match * 0.2)

                +

                (reliability_score * 0.2)

            )

            # Confidence

            if overall_score >= 85:

                confidence = "Very High"

            elif overall_score >= 70:

                confidence = "High"

            elif overall_score >= 50:

                confidence = "Medium"

            else:

                confidence = "Low"

            recommendations.append({

                "job": job.title,

                "company": job.company,

                "location": job.location,

                "salary": job.salary,

                "job_type": job.job_type,

                "match_score": match_score,

                "experience_match":
                experience_match,

                "overall_score":
                overall_score,

                "confidence":
                confidence,

                "reliability_score":
                reliability_score,

                "trust_badge":
                badge,

                "trust_level":
                trust_level,

                "matched_skills":
                list(matched_skills),

                "missing_skills":
                list(
                    job_skills -
                    matched_skills
                )

            })

        recommendations.sort(

            key=lambda x:
            x["overall_score"],

            reverse=True

        )

        db.close()

        return {

            "candidate":
            candidate.name,

            "recommended_jobs":
            recommendations

        }

    except Exception as e:

        return {
            "error": str(e)
        }
# ---------------- SKILL IMPROVEMENT ----------------

@app.get("/skill-improvement")
def skill_improvement():

    return {
        "your_skills": [
            "Python",
            "SQL"
        ],
        "required_skills": [
            "Python",
            "SQL",
            "FastAPI",
            "Docker"
        ],
        "missing_skills": [
            "FastAPI",
            "Docker"
        ]
    }

# ---------------- ANALYTICS ----------------

@app.get("/analytics")
def analytics():

    db = SessionLocal()

    total_jobs = db.query(models.Job).count()

    total_candidates = db.query(
        models.CandidateProfile
    ).count()

    total_applications = db.query(
        models.Application
    ).count()

    total_shortlisted = db.query(
        models.ShortlistedCandidate
    ).count()

    db.close()

    return {
        "total_jobs": total_jobs,
        "total_candidates": total_candidates,
        "total_applications": total_applications,
        "total_shortlisted": total_shortlisted
    }
# ---------------- APPLY JOB ----------------

class Application(BaseModel):
    candidate_name: str
    job_title: str

@app.post("/apply-job")
def apply_job(data: Application):

    db = SessionLocal()

    application = models.Application(
        candidate_name=data.candidate_name,
        job_title=data.job_title
    )

    db.add(application)
    db.commit()

    db.close()

    return {
        "message":
        "Application Submitted Successfully"
    }
@app.get("/applications")
def get_applications():

    db = SessionLocal()

    apps = db.query(models.Application).all()

    output = []

    for app in apps:

        output.append({
            "candidate_name":app.candidate_name,
            "job_title":app.job_title
        })

    db.close()

    return output
@app.post("/language-assessment")
def language_assessment(profile: CandidateProfile):

    score = 0

    if "Python" in profile.languages:
        score += 40

    if "Java" in profile.languages:
        score += 30

    if "SQL" in profile.languages:
        score += 20

    if "JavaScript" in profile.languages:
        score += 10

    return {
        "language_score": score
    }


# ---------------- SHORTLIST ----------------


class Shortlist(BaseModel):
    candidate_name:str
    job_title:str

@app.post("/shortlist")
def shortlist(data:Shortlist):

    db = SessionLocal()

    candidate = models.ShortlistedCandidate(
        candidate_name=data.candidate_name,
        job_title=data.job_title
    )

    db.add(candidate)
    db.commit()

    db.close()

    return {
        "message":
        "Candidate Shortlisted"
    }
@app.get("/shortlisted")
def get_shortlisted():

    db = SessionLocal()

    candidates = db.query(
        models.ShortlistedCandidate
    ).all()

    output = []

    for c in candidates:

        output.append({
            "candidate_name":c.candidate_name,
            "job_title":c.job_title
        })

    db.close()

    return output
