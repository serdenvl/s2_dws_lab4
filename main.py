from fastapi import FastAPI, HTTPException

import random
from enum import Enum
from typing import Any
from dataclasses import dataclass


class NEnum(Enum):
    @staticmethod
    def _generate_next_value_(name: str, start: int, count: int, last_values: list[Any]) -> Any:
        return name


StrFields = NEnum('StrFields', 'name country category')
IntFields = NEnum('IntFields', 'points medals')
AnyFields = NEnum('AnyFields', 'name country category points medals')


@dataclass
class Human:
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


@app.post("/add", status_code=201)
def add_human(human: Human) -> Human:
    if human.name in humans:
        raise HTTPException(status_code=400, detail='the name is already in use')
    humans[human.name] = human
    return human


@app.post("/update")
def update_human(name: str, field: AnyFields, new_value: str) -> Human:
    if field != StrFields.name:
        if name not in humans:
            raise HTTPException(status_code=400, detail='the name not in use')
    else:
        if new_value in humans:
            raise HTTPException(status_code=400, detail='the name is already in use')
        humans[new_value] = humans[name]
        name = new_value

    print(type(field))
    if field.name in IntFields:
        try:
            new_value = int(new_value)
        except ValueError:
            raise HTTPException(status_code=400, detail='wrong type of value')

    setattr(humans[name], field.name, new_value)
    return humans[name]


@app.post("/delete")
def delete_human(name: str) -> Human:
    try:
        human = humans[name]
        del humans[name]
    except KeyError:
        raise HTTPException(status_code=404, detail='the name not in use')

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
