import enum


class UserRole(str, enum.Enum):
    STORE_STAFF = "store_staff"
    STORE_MANAGER = "store_manager"
    PURCHASE_STAFF = "purchase_staff"
    PURCHASE_MANAGER = "purchase_manager"
