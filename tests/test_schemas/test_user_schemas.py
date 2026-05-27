import pytest

from src.exceptions.validation import ValidationException
from src.schemas.user import UserBody, UserProfileBody, UserUpdateBody, UserProfileUpdateBody


class TestUserProfileBody:
    def test_valid_phone(self):
        p = UserProfileBody(phone="+79991234567")
        assert p.phone == "+79991234567"

    def test_phone_7_format(self):
        p = UserProfileBody(phone="79991234567")
        assert p.phone == "79991234567"

    def test_phone_8_format(self):
        p = UserProfileBody(phone="89991234567")
        assert p.phone == "89991234567"

    def test_invalid_phone_raises(self):
        with pytest.raises(ValidationException) as exc_info:
            UserProfileBody(phone="12345")
        assert exc_info.value.field == "phone"

    def test_none_phone_ok(self):
        p = UserProfileBody(phone=None)
        assert p.phone is None

    def test_empty_address_raises(self):
        with pytest.raises(ValidationException) as exc_info:
            UserProfileBody(address="   ")
        assert exc_info.value.field == "address"

    def test_empty_bio_raises(self):
        with pytest.raises(ValidationException) as exc_info:
            UserProfileBody(bio="   ")
        assert exc_info.value.field == "bio"


class TestUserBody:
    def test_valid_user(self):
        u = UserBody(
            username="user1",
            email="user@test.com",
            profile=UserProfileBody(),
        )
        assert u.username == "user1"

    def test_empty_username_raises(self):
        with pytest.raises(ValidationException) as exc_info:
            UserBody(
                username="   ",
                email="user@test.com",
                profile=UserProfileBody(),
            )
        assert exc_info.value.field == "username"

    def test_empty_email_raises(self):
        with pytest.raises(ValidationException) as exc_info:
            UserBody(
                username="user",
                email="   ",
                profile=UserProfileBody(),
            )
        assert exc_info.value.field == "email"

    def test_invalid_email_raises(self):
        with pytest.raises(Exception):
            UserBody(
                username="user",
                email="not-an-email",
                profile=UserProfileBody(),
            )

    def test_empty_full_name_raises(self):
        with pytest.raises(ValidationException) as exc_info:
            UserBody(
                username="user",
                email="user@test.com",
                full_name="   ",
                profile=UserProfileBody(),
            )
        assert exc_info.value.field == "full_name"

    def test_username_stripped(self):
        u = UserBody(
            username="  trimmed  ",
            email="user@test.com",
            profile=UserProfileBody(),
        )
        assert u.username == "trimmed"


class TestUserUpdateBody:
    def test_empty_username_raises(self):
        with pytest.raises(ValidationException) as exc_info:
            UserUpdateBody(username="   ")
        assert exc_info.value.field == "username"

    def test_none_username_ok(self):
        u = UserUpdateBody(username=None)
        assert u.username is None

    def test_partial_update(self):
        u = UserUpdateBody(username="newname")
        assert u.username == "newname"
        assert u.email is None
