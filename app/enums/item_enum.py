from enum import Enum


class ItemType(str, Enum):
    TEXT = "text"
    SERVICE = "service"
    INVENTORY_ITEM = "inventory_item"


class ItemCategory(str, Enum):
    CONSUMABLE = "consumable"
    PHARMACEUTICALS = "Pharmaceuticals"
    EQUIPMENT = "equipment"
    OTHER = "other"
    
class ItemStatus(str, Enum):
    DRAFT = "Draft"
    APPROVED = "Approved"
    REJECTED = "Rejected"