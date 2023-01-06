from ..config.db import get_db
from datetime import datetime
from pydantic import BaseModel, EmailStr
from typing import List

db = get_db()


class Job(BaseModel):
    job_title: str
    experience_level: str
    skills: List[str]
    created_at: datetime = datetime.utcnow()
    timestamp: datetime = datetime.timestamp(datetime.utcnow())
    
class JobUpdate(BaseModel):
    job_title: str
    experience_level: str
    skills: List[str]
    updated_at: datetime = datetime.utcnow()
    timestamp: datetime = datetime.timestamp(datetime.utcnow())


def insert_job(job: dict):
    if job is not None:
        new_job: Job = Job(**job)
        job_Indb = db.english.find_one({"job_title": new_job.job_title, "experience_level": new_job.experience_level})
        if job_Indb:
            skill_Indb = list(job_Indb["skills"])
            if skill_Indb !=  new_job.skills:
                unique_list = list(set(new_job.skills).union(set(skill_Indb)))
                job_update: JobUpdate = JobUpdate(job_title=new_job.job_title, experience_level=new_job.experience_level, skills=unique_list)
                db.english.find_one_and_update(
                    filter={"_id": job_Indb.get("_id")},
                    update={
                        "$set": job_update.dict()
                    },
                )
        else:
            db.english.insert_one(new_job.dict())
