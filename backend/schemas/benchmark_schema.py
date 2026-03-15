from pydantic import BaseModel
from typing import List

class BenchmarkRequest(BaseModel):
    models: List[str]