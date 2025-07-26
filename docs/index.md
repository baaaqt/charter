# Библиотека для построения фильтров с помощью json

## Задача, которую должна решить эта библиотека

Библиотека предназначена для построения фильтров выборки из JSON в фильтры выборки SQLAlchemy и Beanie ODM.

Будет крайне полезна в связке с веб-фреймворками типа FastAPI, Starlette, LiteStar и т. п.


## Зачем?

В Python нет библиотеки для, чтобы работать с разными видами баз данных. Все они работают либо с SQL, либо узконаправлены по видам. Следовательно у каждой базы данных свое API выборки данных.


### Пример

Есть сущность описываемая в Python, как:

```python
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Entity:
    id: str
    created_at: datetime
    updated_at: datetime
```

**Задача:** Сделайте выборку данных созданных в период `[01.06.2025, 03.06.2025]` или обновленных в период `[04.06.2025, 05.06.2025]` (использована математическая нотация для обозначения отрезков).


Как будет выглядеть выборка с SQLAlchemy:
```python

import sqlalchemy as sa

sa.select(Entity).where(
    sa.or_(
        sa.and_(
            Entity.created_at >= datetime(day=1, month=6, year=2025),
            Entity.created_at <= datetiem(day=3, month=6, year=2025)
        ),
        sa.and_(
            Entity.updated_at >= datetime(day=4, month=6, year=2025),
            Entity.updated_at >= datetiem(day=5, month=6, year=2025)
        )
    )
)
```

Как в Beanie ODM:
```python
from beanie.operators import And, Or

Entity.find(
    Or(
        And(
            Entity.created_at >= datetime(day=1, month=6, year=2025),
            Entity.created_at <= datetiem(day=3, month=6, year=2025)
        ),
        And(
            Entity.updated_at >= datetime(day=4, month=6, year=2025),
            Entity.updated_at >= datetiem(day=5, month=6, year=2025)
        )
    )
)
```

Вроде бы не очень то плохо. Но при создании веб приложения и интеграции фильтров в этих приложениях с клиентами придется писать собственные обработчики и использовать API SQLAlchemy, Beanie ODM и т. п., оставляя для клиента одинаковое API фильтров.



Или в Python с помощью ***charter*** для ***SQLAlchemy***:
```python
from datetime import datetime

from charter import CriteriaBuilder
from sqlalchemy import ColumnElement


cb = CriteriaBuilder(Entity, backend="sqlalchemy")
criteria: Sequence[ColumnElement[Any]] = cb.where(
    cb.gte(
        "created_at",
        datetime(day=1, month=6, year=2025)
    ),
    cb.gte(
        "created_at",
        datetime(day=3, month=6, year=2025)
    )
).or_(
    cb.gte(
        "updated_at",
        datetime(day=4, month=6, year=2025)
    ),
    cb.gte(
        "updated_at",
        datetime(day=5, month=6, year=2025)
    )
).build()
```

Или в Python с помощью ***charter*** для ***beanie***:
```python
from datetime import datetime

from charter import CriteriaBuilder


cb = CriteriaBuilder(Entity, backend="beanie")
criteria: Sequence[Mapping[str, Any] | bool] = cb.where(
    cb.gte(
        "created_at",
        datetime(day=1, month=6, year=2025)
    ),
    cb.gte(
        "created_at",
        datetime(day=3, month=6, year=2025)
    )
).or_(
    cb.gte(
        "updated_at",
        datetime(day=4, month=6, year=2025)
    ),
    cb.gte(
        "updated_at",
        datetime(day=5, month=6, year=2025)
    )
).build()
```


Из `json`
```jsonc
from charter import CriteriaBuilder


cb = CriteriaBuilder(Entity, backend="sqlalchemy").from_json(
"""
{
    "or": [
        {
            "and": [
                {
                    "gte": ["created_at", "2025-06-01T00:00:00"]
                },
                {
                    "lte": ["created_at", "2025-06-03T00:00:00"]
                }
            ]
        },
        {
            "and": [
                {
                    "gte": ["updated_at", "2025-06-04T00:00:00"]
                },
                {
                    "lte": ["updated_at", "2025-06-05T00:00:00"]
                }
            ]
        }
    ]
}
"""
).
```
