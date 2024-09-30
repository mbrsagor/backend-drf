from enum import IntEnum


class UserTypes(IntEnum):
    ADMIN = 1
    # GUEST = 2
    COMPANY = 3
    SPONSOR = 4
    GUARD = 5

    @classmethod
    def get_choices(cls):
        return [(key.value, key.name) for key in cls]


class Gender(IntEnum):
    MALE = 1
    FEMALE = 2
    OTHER = 3

    @classmethod
    def get_gender(cls):
        return [(key.value, key.name) for key in cls]


class CategoryTypes(IntEnum):
    PACKAGE = 1
    EVENT = 2

    @classmethod
    def get_category(cls):
        return [(key.value, key.name) for key in cls]


class Transaction_Type(IntEnum):
    SPONSOR = 1
    TICKET = 2
    DONATION= 3

    @classmethod
    def get_transaction_type(cls):
        return [(key.value, key.name) for key in cls]
