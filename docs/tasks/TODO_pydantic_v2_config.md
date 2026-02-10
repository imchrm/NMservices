# TODO: Миграция admin моделей на Pydantic v2 ConfigDict

## Приоритет: Низкий (не блокирует MVP)
## Обнаружено: 2026-02-10, pytest warnings

---

## Проблема

В файле `src/nms/models/admin.py` используется deprecated `class Config` (стиль Pydantic v1).
При запуске pytest выдаётся 4 предупреждения:

```
PydanticDeprecatedSince20: Support for class-based `config` is deprecated,
use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0.
```

## Затронутые модели (4 шт.)

| Модель | Строка | Поле |
|--------|--------|------|
| `AdminUserResponse` | 20-21 | `from_attributes = True` |
| `AdminUserWithOrdersResponse` | 35-36 | `from_attributes = True` |
| `AdminOrderResponse` | 66-67 | `from_attributes = True` |
| `AdminOrderWithUserResponse` | 82-83 | `from_attributes = True` |

## Решение

Заменить `class Config` на `model_config = ConfigDict(...)` в каждой модели.

### До (deprecated):
```python
from pydantic import BaseModel

class AdminUserResponse(BaseModel):
    id: int
    # ...
    class Config:
        from_attributes = True
```

### После (Pydantic v2):
```python
from pydantic import BaseModel, ConfigDict

class AdminUserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    # ...
```

## Шаги выполнения

1. Добавить `ConfigDict` в импорт из `pydantic` (строка 6)
2. Заменить 4 `class Config` блока на `model_config = ConfigDict(from_attributes=True)`
3. Запустить `pytest` — убедиться что 4 warnings исчезли
4. Проверить что 30/30 тестов по-прежнему проходят

## Оценка

- Файл: `src/nms/models/admin.py`
- Изменений: ~10 строк
- Риск: минимальный (замена 1:1, без изменения логики)
