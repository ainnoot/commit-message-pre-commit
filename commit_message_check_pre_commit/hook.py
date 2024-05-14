import sys
import re
from pathlib import Path
from abc import ABC
from typing import List, Tuple, Optional

TYPE_RE = r"([a-z]+)"
SCOPE_RE = r"(\([a-z]+[a-z_\-]*\))?"
BREAKING_CHANGE_RE = r"(\!)?"
DESCRIPTION_RE = r"([\S\s]+)"
CC_MASK = r"^{type}{scope}{breaking_change}\: {description}$"
VALID_TYPES = ("fix", "ci", "bump", "chore", "feat", "fix", "test")


class LintError(ABC):
    def __init__(self, string: str) -> None:
        self.string: str = string

    def __repr__(self) -> str:
        return self.string

    def __str__(self) -> str:
        return self.string


class MissingScopeOnBreakingChange(LintError):
    def __init__(self) -> None:
        return super().__init__("Missing scope on breaking change!")


class UnknownCommitType(LintError):
    def __init__(self, type: str) -> None:
        return super().__init__("Unknown commit type: {}".format(type))


class InvalidCommitMessageFormat(LintError):
    def __init__(self) -> None:
        return super().__init__(
            "Commit message does not match conventional commits spec."
        )


def build_re() -> str:
    return CC_MASK.format(
        type=TYPE_RE,
        scope=SCOPE_RE,
        breaking_change=BREAKING_CHANGE_RE,
        description=DESCRIPTION_RE,
    )


def validate_commit_message(commit_message: str) -> Tuple[bool, List[LintError]]:
    p = build_re()
    match = re.fullmatch(p, commit_message)

    return validate_match(match)


def validate_match(re_match: Optional[re.Match[str]]) -> Tuple[bool, List[LintError]]:
    if re_match is None:
        return False, [InvalidCommitMessageFormat()]

    type, scope, breaking_change, description = re_match.groups()

    violations: List[LintError] = []
    if breaking_change is not None and scope is None:
        violations.append(MissingScopeOnBreakingChange())

    if type not in VALID_TYPES:
        violations.append(UnknownCommitType(type))

    return not violations, violations


def run() -> None:
    if len(sys.argv) != 2:
        print("commit-message-check [git commit temp file]")
        sys.exit(1)

    commit_message = Path(sys.argv[1]).read_text()

    ok, violations = validate_commit_message(commit_message)
    if ok:
        sys.exit(0)

    for reason in violations:
        print("*", reason)

    sys.exit(1)
