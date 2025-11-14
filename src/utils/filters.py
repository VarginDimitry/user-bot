from typing import Any, Generic, get_args, Literal, TypeVar, Union

from advanced_alchemy.filters import StatementFilter
from pydantic import BaseModel, model_validator, TypeAdapter
from sqlalchemy import Column, ColumnElement

ContainerValue = TypeVar("ContainerValue")


class ContainerFilter(BaseModel, Generic[ContainerValue]):
    value: ContainerValue
    filter_type: Literal["$eq"] = "$eq"

    def build_filter(self, column: Column) -> StatementFilter | ColumnElement[bool]:
        return column == self.value


class GTFilter(ContainerFilter):
    filter_type: Literal["$gt"] = "$gt"  # pyrefly: ignore[bad-override]

    def build_filter(self, column: Column) -> StatementFilter | ColumnElement[bool]:
        return column > self.value


class GTEFilter(ContainerFilter):
    filter_type: Literal["$gte"] = "$gte"  # pyrefly: ignore[bad-override]

    def build_filter(self, column: Column) -> StatementFilter | ColumnElement[bool]:
        return column >= self.value


class LTFilter(ContainerFilter):
    filter_type: Literal["$lt"] = "$lt"  # pyrefly: ignore[bad-override]

    def build_filter(self, column: Column) -> StatementFilter | ColumnElement[bool]:
        return column < self.value


class LTEFilter(ContainerFilter):
    filter_type: Literal["$lte"] = "$lte"  # pyrefly: ignore[bad-override]

    def build_filter(self, column: Column) -> StatementFilter | ColumnElement[bool]:
        return column <= self.value


class SearchFilter(ContainerFilter):
    filter_type: Literal["$search"] = "$search"  # pyrefly: ignore[bad-override]

    def build_filter(self, column: Column) -> StatementFilter | ColumnElement[bool]:
        return column.ilike(self.value)


class InFilter(ContainerFilter):
    filter_type: Literal["$in"] = "$in"  # pyrefly: ignore[bad-override]

    def build_filter(self, column: Column) -> StatementFilter | ColumnElement[bool]:
        return column.in_(self.value)


class NotInFilter(ContainerFilter):
    filter_type: Literal["$nin"] = "$nin"  # pyrefly: ignore[bad-override]

    def build_filter(self, column: Column) -> StatementFilter | ColumnElement[bool]:
        return column.not_in(self.value)


FilterTypes = (
    ContainerFilter
    | GTFilter
    | GTEFilter
    | LTFilter
    | LTEFilter
    | SearchFilter
    | InFilter
    | NotInFilter
)
FilterTypesTuple = get_args(FilterTypes)


class FiltersModel(BaseModel):
    @model_validator(mode="before")
    @classmethod
    def map_to_containers(cls, data: Any) -> Any:
        if isinstance(data, FiltersModel):
            return data

        for key, value in data.items():
            attr_type = cls.model_fields[key].annotation
            if value is None or isinstance(value, FilterTypes):
                continue
            elif isinstance(value, dict):
                typed_union = Union[
                    # pyrefly: ignore[not-a-type]
                    tuple(f[attr_type] for f in FilterTypesTuple)
                ]
                data[key] = TypeAdapter(typed_union).validate_python(value)
            elif isinstance(value, list):
                # pyrefly: ignore[bad-specialization]
                data[key] = InFilter[attr_type](value=value)
            else:
                data[key] = ContainerFilter[attr_type](value=value)

        return data

    def get_filter_dict(self) -> dict[str, ContainerFilter[Any]]:
        return {
            field: value
            for field in self.model_fields.keys()
            if (value := getattr(self, field)) is not None
        }
