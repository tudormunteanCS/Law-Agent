from pydantic import BaseModel,Field

class RewrittenQuery(BaseModel):
    rewritten_query: str = Field(..., description="Promptul rescris din care s-au extras termenii esentiali; sirul bag-of-words, fără semne de întrebare.")
    confidence: float = Field(..., ge=0, le=1, description="Probabilitatea (0..1) că răspunsul există deja în CONTEXT.")
