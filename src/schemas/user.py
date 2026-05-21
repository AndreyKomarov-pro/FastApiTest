import re
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict, EmailStr, field_validator
from src.exceptions.validation import ValidationException
from src.models.user import UserModel
from src.models.user_profile import UserProfile

RF_PHONE_REGEX = re.compile(r'^(\+7|7|8)\d{10}$')

class UserProfileBody(BaseModel):
    phone: str | None = Field(default=None, max_length=20)
    address: str | None = Field(default=None, max_length=500)
    bio: str | None = Field(default=None)

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str | None) -> str | None:
        if v is not None:
            cleaned = v.strip()
            if not RF_PHONE_REGEX.match(cleaned):
                raise ValidationException(field="phone", message="Телефон должен быть в формате РФ: +7XXXXXXXXXX, 7XXXXXXXXXX или 8XXXXXXXXXX")
            return cleaned
        return v

    @field_validator("address")
    @classmethod
    def validate_address(cls, v: str | None) -> str | None:
        if v is not None and not v.strip():
            raise ValidationException(field="address", message="Адрес не может быть пустым если указан")
        return v.strip() if v else v

    @field_validator("bio")
    @classmethod
    def validate_bio(cls, v: str | None) -> str | None:
        if v is not None and not v.strip():
            raise ValidationException(field="bio", message="Bio не может быть пустым если указано")
        return v.strip() if v else v

class UserBody(BaseModel):
    username: str = Field(..., max_length=100)
    email: EmailStr
    full_name: str | None = Field(default=None, max_length=200)
    profile: UserProfileBody

    @field_validator("email", mode="before")
    @classmethod
    def validate_email(cls, v: str) -> str:
        if isinstance(v, str):
            return v.strip()
        return v

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValidationException(field="username", message="Имя пользователя не может быть пустым")
        return stripped

    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, v: str | None) -> str | None:
        if v is not None and not v.strip():
            raise ValidationException(field="full_name", message="Полное имя не может быть пустым если указано")
        return v.strip() if v else v

    def to_model(self) -> UserModel:
        user = UserModel(
            username=self.username,
            email=self.email,
            full_name=self.full_name,
        )
        user.profile = UserProfile(
            phone=self.profile.phone,
            address=self.profile.address,
            bio=self.profile.bio,
        )
        return user

class UserProfileUpdateBody(BaseModel):
    phone: str | None = Field(default=None, max_length=20)
    address: str | None = Field(default=None, max_length=500)
    bio: str | None = Field(default=None)

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str | None) -> str | None:
        if v is not None:
            cleaned = v.strip()
            if not RF_PHONE_REGEX.match(cleaned):
                raise ValidationException(field="phone", message="Телефон должен быть в формате РФ: +7XXXXXXXXXX, 7XXXXXXXXXX или 8XXXXXXXXXX")
            return cleaned
        return v

    @field_validator("address")
    @classmethod
    def validate_address(cls, v: str | None) -> str | None:
        if v is not None and not v.strip():
            raise ValidationException(field="address", message="Адрес не может быть пустым если указан")
        return v.strip() if v else v

    @field_validator("bio")
    @classmethod
    def validate_bio(cls, v: str | None) -> str | None:
        if v is not None and not v.strip():
            raise ValidationException(field="bio", message="Bio не может быть пустым если указано")
        return v.strip() if v else v


class UserUpdateBody(BaseModel):
    username: str | None = Field(default=None, max_length=100)
    email: EmailStr | None = None
    full_name: str | None = Field(default=None, max_length=200)
    profile: UserProfileUpdateBody | None = None

    @field_validator("email", mode="before")
    @classmethod
    def validate_email(cls, v: str | None) -> str | None:
        if isinstance(v, str):
            return v.strip()
        return v

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str | None) -> str | None:
        if v is not None:
            stripped = v.strip()
            if not stripped:
                raise ValidationException(field="username", message="Имя пользователя не может быть пустым")
            return stripped
        return v

    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, v: str | None) -> str | None:
        if v is not None and not v.strip():
            raise ValidationException(field="full_name", message="Полное имя не может быть пустым если указано")
        return v.strip() if v else v

    def apply_to(self, user: UserModel) -> None:
        for key, value in self.model_dump(exclude_unset=True, exclude={"profile"}).items():
            setattr(user, key, value)
        if self.profile:
            if user.profile:
                for key, value in self.profile.model_dump(exclude_unset=True).items():
                    setattr(user.profile, key, value)
            else:
                user.profile = UserProfile(
                    phone=self.profile.phone,
                    address=self.profile.address,
                    bio=self.profile.bio,
                )


class UserCreate(BaseModel):
    body: UserBody

class UserUpdate(BaseModel):
    body: UserUpdateBody

class UserProfileResponse(BaseModel):
    id: UUID
    phone: str | None
    address: str | None
    bio: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class UserResponse(BaseModel):
    id: UUID
    username: str
    email: EmailStr
    full_name: str | None
    created_at: datetime
    profile: UserProfileResponse | None

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_model(cls, model: UserModel) -> "UserResponse":
        return cls.model_validate(model)

    @classmethod
    def from_list(cls, models: list[UserModel]) -> list["UserResponse"]:
        return [cls.model_validate(m) for m in models]
