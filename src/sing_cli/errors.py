class SingCliError(Exception):
    """Base class for expected CLI failures."""


class ExternalCommandError(SingCliError):
    def __init__(self, command: list[str], returncode: int, output: str) -> None:
        summary = output.strip() or f"exit code {returncode}"
        super().__init__(f"{command[0]} failed: {summary}")
        self.command = command
        self.returncode = returncode
        self.output = output
