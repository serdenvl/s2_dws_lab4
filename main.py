import pydantic
from fastapi import FastAPI, HTTPException

import random
from enum import Enum
from typing import Any
from dataclasses import dataclass


class NEnum(Enum):
    @staticmethod
    def _generate_next_value_(name: str, start: int, count: int, last_values: list[Any]) -> Any:
        return name

    @classmethod
    def names(cls):
        return {a.name for a in cls}


StrFields = NEnum('StrFields', 'name country category')
IntFields = NEnum('IntFields', 'points medals')
AnyFields = NEnum('AnyFields', 'name country category points medals')


class Human(pydantic.BaseModel):
    name: str
    country: str
    category: str
    points: int
    medals: int

    def get_attr_by_field(self, field: AnyFields):
        return getattr(self, field.name)

    @classmethod
    def sort_key(cls, field: AnyFields):
        def key(human: cls):
            return human.get_attr_by_field(field)
        return key


humans = {
    name: Human(
        name=name,
        country=random.choice(('country', 'COUNTRY', 'COunTRy')),
        category=random.choice(('super', 'norm', 'bad')),
        points=random.randint(0, 999),
        medals=random.randint(0, 9)
    )
    for name in "ABCDEFG"
}


app = FastAPI()


@app.get("/all")
def all_humans() -> list[Human]:
    """
    Returns all humans
    """
    return list(humans.values())


@app.get("/human/{name}")
def get_human(name: str) -> Human:
    try:
        return humans[name]
    except KeyError:
        raise HTTPException(status_code=404, detail='there is no human with that name')


@app.post("/human/{name}", status_code=201)
def add_human(name: str, human: Human) -> Human:
    human.name = name
    if name in humans:
        raise HTTPException(status_code=400, detail='there is already a human with that name')
    humans[name] = human
    return human


@app.put("/human/{name}")
def update_human(name: str, human: Human) -> Human:
    human.name = name
    if name not in humans:
        raise HTTPException(status_code=404, detail='there is no human with that name')
    humans[name] = human
    return human


@app.patch("/human/{name}")
def reward_human(name: str, medals_number: int) -> Human:
    if name not in humans:
        raise HTTPException(status_code=404, detail='there is no human with that name')
    human: Human = humans[name]
    human.medals += medals_number
    return human


@app.delete("/delete/{name}")
def delete_human(name: str) -> Human:
    try:
        human = humans[name]
        del humans[name]
    except KeyError:
        raise HTTPException(status_code=404, detail='there is no human with that name')

    return human


@app.get("/sort/{field}")
def sort_humans(field: AnyFields) -> list[Human]:
    return sorted(humans.values(), key=Human.sort_key(field))


@app.get("/min/{field}")
def min_field(field: AnyFields) -> Human:
    return min(humans.values(), key=Human.sort_key(field))


@app.get("/max/{field}")
def max_field(field: AnyFields) -> Human:
    return max(humans.values(), key=Human.sort_key(field))


@app.get("/mean/{field}")
def mean_field(field: IntFields) -> float:
    return sum(a.get_attr_by_field(field) for a in humans.values()) / len(humans)
