from __future__ import annotations

import os

from pyswip import Prolog

from ..core.celery_app import celery_app
from ..core.evaluation import EssayEvaluator
from ..core.submission_pipeline import process_submission


prolog = Prolog()
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
prolog_path = os.path.join(BASE_DIR, "prolog", "main_brain.pl").replace("\\", "/")
prolog.consult(prolog_path)
evaluator = EssayEvaluator(prolog)


@celery_app.task(name="evaluate_submission_task")
def evaluate_submission_task(student_id: int, topic_id: int, essay_text: str):
    return process_submission(student_id, topic_id, essay_text, evaluator)
