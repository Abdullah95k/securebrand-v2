"""The one error every helper raises for an input it refuses; `code` names the rule."""


class ContractError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code
