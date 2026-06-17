from pydantic import BaseModel, EmailStr


class UserSchema(BaseModel):
    nome_usuario: str
    email: EmailStr
    senha_hash: str


class UserPublic(BaseModel):
    id_usuario: int
    nome_usuario: str
    email: EmailStr
