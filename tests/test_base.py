import pytest
from commit_message_check_pre_commit.hook import validate_commit_message


@pytest.mark.parametrize("type", ("ci", "bump", "chore", "feat", "fix", "test"))
def test_simple_commit(type):
    commit_message = "{type}: This is a commit!".format(type=type)
    ok, _ = validate_commit_message(commit_message)
    assert ok


def test_missing_type():
    commit_message = "(scope): Message."
    ok, _ = validate_commit_message(commit_message)
    assert not ok


def test_breaking_change_but_no_scope():
    commit_message = "feat!: various improvements, but slight changes to the grammar."
    ok, _ = validate_commit_message(commit_message)
    assert not ok
