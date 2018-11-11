from abc import ABC, abstractmethod


class Requirement(ABC):
    @abstractmethod
    def __init__(self) -> None:
        pass

    @abstractmethod
    def validate(self, flags: dict) -> bool:
        pass


class NullFlagRequirement(Requirement):
    def __init__(self, flag_name: str):
        super().__init__()
        self.flag_name = flag_name

    def validate(self, flags: dict) -> bool:
        return self.flag_name not in flags


class SetFlagRequirement(Requirement):
    def __init__(self, flag_name: str):
        super().__init__()
        self.flag_name = flag_name

    def validate(self, flags: dict) -> bool:
        return self.flag_name in flags


class FlagEqualsRequirement(Requirement):
    def __init__(self, flag_name: str, value: object):
        super().__init__()
        self.flag_name = flag_name
        self.value = value

    def validate(self, flags: dict) -> bool:
        return self.flag_name in flags and flags[self.flag_name] == self.value


class FlagNotEqualsRequirement(Requirement):
    def __init__(self, flag_name: str, value):
        super().__init__()
        self.flag_name = flag_name
        self.value = value

    def validate(self, flags: dict) -> bool:
        return self.flag_name in flags and flags[self.flag_name] != self.value


class FlagOperation(ABC):
    @abstractmethod
    def __init__(self):
        pass

    def apply(self, flags: dict):
        pass


class SetFlagOperation(FlagOperation):
    def __init__(self, flag: str, value):
        super().__init__()
        self.flag = flag
        self.value = value

    def apply(self, flags: dict):
        flags[self.flag] = self.value


def requirement_from_dict(requirement_dict: dict) -> Requirement:
    if requirement_dict["type"] == "null_flag":
        return NullFlagRequirement(requirement_dict["flag"])
    elif requirement_dict["type"] == "set_flag":
        return SetFlagRequirement(requirement_dict["flag"])
    elif requirement_dict["type"] == "flag_equals":
        return FlagEqualsRequirement(requirement_dict["flag"], requirement_dict["value"])
    elif requirement_dict["type"] == "flag_does_not_equal":
        return FlagNotEqualsRequirement(requirement_dict["flag"], requirement_dict["value"])


def operation_from_dict(operation_dict: dict) -> FlagOperation:
    if operation_dict["operation"] == "set":
        return SetFlagOperation(operation_dict["flag"], operation_dict["value"])
