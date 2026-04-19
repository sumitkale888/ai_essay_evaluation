from __future__ import annotations

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from celery.result import AsyncResult

from ..models import EssaySubmission
from ..core.file_extractor import FileExtractionError, extract_text_from_upload
from ..core.celery_app import celery_app
from ..core.evaluation import EssayEvaluator
from ..core.submission_pipeline import process_submission
from pyswip import Prolog
import os


router = APIRouter()

prolog = Prolog()
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
prolog_path = os.path.join(BASE_DIR, "prolog", "main_brain.pl").replace("\\", "/")
try:
    prolog.consult(prolog_path)
except Exception as e:
    print(f"Error consulting Prolog for processing routes: {e}")

evaluator = EssayEvaluator(prolog)


@router.post("/submit-essay-async")
def submit_essay_async(submission: EssaySubmission):
    task = celery_app.send_task(
        "evaluate_submission_task",
        args=[submission.student_id, submission.topic_id, submission.essay_text],
    )
    return {"status": "queued", "task_id": task.id}


@router.get("/task-status/{task_id}")
def get_task_status(task_id: str):
    task = AsyncResult(task_id, app=celery_app)
    payload = {"task_id": task_id, "state": task.state}

    if task.state == "SUCCESS":
        payload["result"] = task.result
    elif task.state == "FAILURE":
        payload["error"] = str(task.result)

    return payload


@router.post("/extract-essay-text")
async def extract_essay_text(file: UploadFile = File(...)):
    try:
        data = await file.read()
        extracted_text = extract_text_from_upload(file.filename or "", data)
        return {
            "filename": file.filename,
            "word_count": len(extracted_text.split()),
            "essay_text": extracted_text,
        }
    except FileExtractionError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Text extraction failed: {e}")


@router.post("/submit-file-async")
async def submit_file_async(
    student_id: int = Form(...),
    topic_id: int = Form(...),
    file: UploadFile = File(...),
):
    try:
        data = await file.read()
        extracted_text = extract_text_from_upload(file.filename or "", data)
        task = celery_app.send_task(
            "evaluate_submission_task",
            args=[student_id, topic_id, extracted_text],
        )
        return {
            "status": "queued",
            "task_id": task.id,
            "filename": file.filename,
            "word_count": len(extracted_text.split()),
        }
    except FileExtractionError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File submission failed: {e}")


@router.post("/submit-file")
async def submit_file(
    student_id: int = Form(...),
    topic_id: int = Form(...),
    file: UploadFile = File(...),
):
    try:
        data = await file.read()
        extracted_text = extract_text_from_upload(file.filename or "", data)
        return process_submission(student_id, topic_id, extracted_text, evaluator)
    except FileExtractionError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File submission failed: {e}")
