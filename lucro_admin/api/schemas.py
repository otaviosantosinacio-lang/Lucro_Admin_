from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserSchema(BaseModel):
    nome_usuario: str
    email: EmailStr
    senha_hash: str


class UserPublic(BaseModel):
    id_usuario: int
    nome_usuario: str
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
