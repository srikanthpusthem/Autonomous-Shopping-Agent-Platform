from enum import StrEnum


class ShippingSpeedPreference(StrEnum):
    FASTEST = "fastest"
    BALANCED = "balanced"
    CHEAPEST = "cheapest"


class RunStatus(StrEnum):
    CREATED = "created"
    PLANNING = "planning"
    SEARCHING = "searching"
    ANALYZING = "analyzing"
    RANKING = "ranking"
    DONE = "done"
    ERROR = "error"


class FeedbackType(StrEnum):
    PICK = "pick"
    NOT_INTERESTED = "not_interested"
    PREFERENCE = "preference"
