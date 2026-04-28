from pydantic import BaseModel, ConfigDict, Field


class DogSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    breed: str
    sex: str

    height_cm: float = Field(ge=0)
    weight_kg: float = Field(ge=0)

    sire_id: str | None = None
    dam_id: str | None = None


class AncestorsResponseSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    dog: DogSchema
    ancestors: list[DogSchema]
    has_ancestors: bool
