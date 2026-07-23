from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserSchema(BaseModel):
    user_name: str
    email: EmailStr
    password: str


class UserPublic(BaseModel):
    user_id: int
    user_name: str
    email: EmailStr
    model_config = ConfigDict(from_attributes=True)


class UserList(BaseModel):
    users: list[UserPublic]


class Token(BaseModel):
    access_token: str
    token_type: str


class FilterPage(BaseModel):
    offset: int = Field(ge=0, default=0)
    limit: int = Field(gt=0, default=100)
