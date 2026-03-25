from result import is_fail
from src.identity.domain.value_objects.email_value_object import EmailValueObject


def test_create_email_normalizes_value() -> None:
    result = EmailValueObject.create({"value": "  Test.User@Example.COM "})

    assert not is_fail(result)
    assert result.value.value == "test.user@example.com"


def test_create_email_rejects_invalid_value() -> None:
    result = EmailValueObject.create({"value": "not-an-email"})

    assert is_fail(result)