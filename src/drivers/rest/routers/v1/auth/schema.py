from pydantic import BaseModel, EmailStr, Field, field_validator

from domain.entities.user import User, UserRole


class SignUpInput(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    email: EmailStr
    password: str = Field(max_length=72)
    role: UserRole = UserRole.USER

    @field_validator("password")
    @classmethod
    def validate_password_length(cls, value: str) -> str:
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters")
        return value


class SignInInput(BaseModel):
    email: EmailStr
    password: str = Field(max_length=72)


class RefreshInput(BaseModel):
    refresh_token: str


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: UserRole

    @classmethod
    def from_entity(cls, user: User) -> "UserResponse":
        return cls(id=user.id, name=user.name, email=user.email, role=user.role)


class TokenPairResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class SignUpResponse(BaseModel):
    user: UserResponse
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
