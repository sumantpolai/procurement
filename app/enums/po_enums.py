import enum


class POStatus(str, enum.Enum):
    DRAFT = "draft"
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    PARTIALLY_RECEIVED = "partially_received"
    RECEIVED = "received"
    CLOSED = "closed"


class POType(str, enum.Enum):
    STANDARD = "STANDARD"
    BLANKET = "BLANKET"
    CONTRACT = "CONTRACT"
    PLANNED = "PLANNED"


class MatchingType(str, enum.Enum):
    TWO_WAY = "TWO_WAY"
    THREE_WAY = "THREE_WAY"
    FOUR_WAY = "FOUR_WAY"
