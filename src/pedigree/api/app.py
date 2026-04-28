from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List

from .types import AncestorsResponse, Dog
from .data import load_data, build_index


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5500"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA = load_data()
INDEX = build_index(DATA)


def normalize_dog(dog: dict) -> dict:
    return {
        "id": str(dog["id"]),
        "name": dog["name"],
        "breed": dog["breed"],
        "sex": dog["sex"],
        "height_cm": (
            float(dog["height_cm"]) if dog.get("height_cm") is not None else None
        ),
        "weight_kg": (
            float(dog["weight_kg"]) if dog.get("weight_kg") is not None else None
        ),
        "sire_id": str(dog["sire_id"]) if dog.get("sire_id") else None,
        "dam_id": str(dog["dam_id"]) if dog.get("dam_id") else None,
    }


def get_dog(dog_id: str):
    dog = INDEX.get(str(dog_id))
    return normalize_dog(dog) if dog else None


def get_ancestors(dog_id: str, max_depth=5):
    result = []
    visited = set()

    def walk(current_id, depth):
        if depth >= max_depth:
            return

        current_id = str(current_id)

        if current_id in visited:
            return

        visited.add(current_id)

        dog = INDEX.get(current_id)
        if not dog:
            return

        for parent_key in ["sire_id", "dam_id"]:
            parent_id = dog.get(parent_key)
            if not parent_id:
                continue

            parent_id = str(parent_id)

            if parent_id in visited:
                continue

            parent = INDEX.get(parent_id)
            
            # NOTE: Related to inconsistency api tests
            # This logic ensures that missing or non-existent parent IDs
            # (e.g. broken lineage data injected in tests) are safely ignored
            # instead of raising errors or breaking traversal.
            if not parent:
                continue

            result.append(normalize_dog(parent))
            walk(parent_id, depth + 1)

    walk(str(dog_id), 0)
    return result


@app.get("/dogs", response_model=List[Dog], tags=["Pedigree"])
def dogs():
    return DATA


@app.get("/dogs/{dog_id}", response_model=Dog, tags=["Pedigree"])
def get_dog_endpoint(dog_id: str):
    dog = get_dog(dog_id)
    if not dog:
        raise HTTPException(status_code=404, detail="Dog not found")
    return dog


@app.get(
    "/dogs/{dog_id}/ancestors", response_model=AncestorsResponse, tags=["Pedigree"]
)
def ancestors_endpoint(dog_id: str):
    dog = get_dog(dog_id)
    if not dog:
        raise HTTPException(status_code=404, detail="Dog not found")

    ancestors = get_ancestors(dog_id)

    return {"dog": dog, "ancestors": ancestors, "has_ancestors": len(ancestors) > 0}


@app.post("/dogs", response_model=Dog, tags=["Pedigree"])
def create_dog(dog: Dog):
    dog = dog.model_dump()  # type: ignore

    dog_id = str(dog["id"])  # type: ignore

    if dog_id in INDEX:
        raise HTTPException(status_code=409, detail="Dog already exists")

    normalized = normalize_dog(dog)  # type: ignore

    DATA.append(normalized)
    INDEX[dog_id] = dog  # type: ignore

    return normalized


@app.delete("/dogs/{dog_id}", tags=["Pedigree"])
def delete_dog(dog_id: str):
    dog_id = str(dog_id)

    if dog_id not in INDEX:
        raise HTTPException(status_code=404, detail="Dog not found")

    INDEX.pop(dog_id)

    global DATA
    DATA = [d for d in DATA if str(d["id"]) != dog_id]

    return {"deleted": True, "id": dog_id}
