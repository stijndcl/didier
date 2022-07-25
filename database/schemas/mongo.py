from bson import ObjectId
from pydantic import BaseModel, Field

__all__ = []


class PyObjectId(str):
    """Custom type for bson ObjectIds"""

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, value: str):
        """Check that a string is a valid bson ObjectId"""
        if not ObjectId.is_valid(value):
            raise ValueError(f"Invalid ObjectId: '{value}'")

        return ObjectId(value)

    @classmethod
    def __modify_schema__(cls, field_schema: dict):
        field_schema.update(type="string")


class MongoBase(BaseModel):
    """Base model that properly sets the _id field, and adds one by default"""

    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")

    class Config:
        """Configuration for encoding and construction"""

        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str, PyObjectId: str}
        use_enum_values = True
