from pydantic import (
    BaseModel,
    field_validator
)

from typing import Optional, List, Literal
from typing import Any
from enum import Enum


# -------------------------
# Dependency Operator
# -------------------------
class DependencyOperator(str, Enum):

    EQUALS = "equals"

    NOT_EQUALS = "notEquals"

    IN = "in"


class ErrorCode(str, Enum):

    SCHEMA_ERROR = "SCHEMA_ERROR"

    RESPONSE_ERROR = "RESPONSE_ERROR"

    INVALID_FIELD_KEY = "INVALID_FIELD_KEY"

    INVALID_SCHEMA = "INVALID_SCHEMA"

    INVALID_TYPE = "INVALID_TYPE"

    INVALID_OPTIONS = "INVALID_OPTIONS"

    INVALID_FORMAT = "INVALID_FORMAT"

    MIN_VALUE_ERROR = "MIN_VALUE_ERROR"

    MAX_VALUE_ERROR = "MAX_VALUE_ERROR"

    DEPENDENCY_ERROR = "DEPENDENCY_ERROR"

    PYDANTIC_ERROR = "PYDANTIC_ERROR"

class WarningCode(str, Enum):

    LOW_CONFIDENCE = "LOW_CONFIDENCE"

    MISSING_FIELD = "MISSING_FIELD"
# -------------------------
# Schema Model
# -------------------------

class SchemaField(BaseModel):

    # internal unique id
    key: str

    # display name
    label: str

    type: Literal[
    "text",
    "enum_single",
    "enum_multi",
    "boolean"
]
    

    options: Optional[
        List[str]
    ] = None

    format: Optional[
        str
    ] = None


# -------------------------
# Response Model
# -------------------------

class ResponseField(BaseModel):

    # internal key (new)
    field_key: str

    # display label
    field_label: str

    value: Optional[Any] = None

    is_present: Optional[
        bool
    ] = None

    confidence_score: Optional[
        float
    ] = None

    # schema object (temporary keep)
    schema: SchemaField


    # -------------------------
    # confidence validation
    # -------------------------

    @field_validator(
        "confidence_score"
    )
    def validate_confidence(

        cls,

        v
    ):

        if v is not None:

            if not (

                0 <= v <= 1
            ):

                raise ValueError(

                    "Confidence score must be between 0 and 1"
                )

        return v


    # -------------------------
    # is_present validation
    # -------------------------

    @field_validator(
        "value"
    )
    def validate_value(

        cls,

        v,

        info
    ):

        is_present = info.data.get(
            "is_present"
        )

        # if field missing,
        # value should be null
        if is_present is False:

            if v is not None:

                raise ValueError(

                    "Value should be null when is_present is false"
                )

        return v