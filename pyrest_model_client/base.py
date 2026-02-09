from pydantic import BaseModel


class BaseAPIModel(BaseModel):
    id: int | str | None = None
    resource_path: str = ""


def get_mode_fields(items: list[dict], model: type[BaseAPIModel]) -> list[BaseAPIModel]:
    return [model(**item) for item in items]
