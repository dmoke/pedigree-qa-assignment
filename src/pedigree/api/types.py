from pydantic import BaseModel
from typing import Optional, List


class Dog(BaseModel):
    id: str
    name: str
    breed: str
    sex: str
    height_cm: float
    weight_kg: float
    sire_id: Optional[str] = None
    dam_id: Optional[str] = None


class AncestorsResponse(BaseModel):
    dog: Dog
    ancestors: List[Dog]
    has_ancestors: bool
