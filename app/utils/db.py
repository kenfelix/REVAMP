from datetime import datetime
from typing import List

from pydantic import BaseModel, EmailStr

from ..config.db import get_db

db = get_db()


class Job(BaseModel):
    industry: str
    job_title: str
    experience_level: str
    skills: List[str]
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    timestamp: datetime = datetime.timestamp(datetime.utcnow())


class JobUpdate(BaseModel):
    skills: List[str]
    updated_at: datetime = datetime.utcnow()
    timestamp: datetime = datetime.timestamp(datetime.utcnow())


def insert_job(job: dict):
    if job is not None:
        new_job: Job = Job(**job)
        job_Indb = db.english.find_one(
            {
                "industry": new_job.industry,
                "job_title": new_job.job_title,
                "experience_level": new_job.experience_level,
            }
        )
        if job_Indb:
            skill_Indb = list(job_Indb["skills"])
            if skill_Indb != new_job.skills:
                unique_list = list(set(new_job.skills).union(set(skill_Indb)))
                job_update: JobUpdate = JobUpdate(skills=unique_list)
                db.english.find_one_and_update(
                    filter={"_id": job_Indb.get("_id")},
                    update={"$set": job_update.dict()},
                )
        else:
            db.english.insert_one(new_job.dict())
