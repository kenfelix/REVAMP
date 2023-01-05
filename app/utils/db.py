from ..config.db import get_db

db = get_db()


def insert_job(job: dict):
    if job is not None:
        title = job.get("job title")
        rate = job.get("experience level")
        skills = job.get("required skills")
        job_Indb = db.english.find_one({"job title": title, "experience level": rate})
        if job_Indb:
            skill_Indb = job_Indb["required skills"]
            skills = list(set(skills.extend(skill_Indb)))
            db.english.update_one(
                filter={"_id": job_Indb.get("_id")},
                update={
                    "$set": {
                        "job title": title,
                        "experience level": rate,
                        "required skills": skills,
                    }
                },
            )
        else:
            db.english.insert_one(job)
