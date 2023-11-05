from enum import Enum


class Environment(str, Enum):
    LOCAL = "local"
    TESTING = "testing"
    DEV = "dev"
    STAGING = "staging"
    PRODUCTION = "production"

    @property
    def is_local(self) -> bool:
        return self == Environment.LOCAL

    @property
    def is_testing(self) -> bool:
        return self == Environment.TESTING

    @property
    def is_debug(self) -> bool:
        return self != Environment.PRODUCTION
