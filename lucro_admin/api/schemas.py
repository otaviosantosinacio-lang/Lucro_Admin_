from pydantic import BaseModel, EmailStr, ConfigDict


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
