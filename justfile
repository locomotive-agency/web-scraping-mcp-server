aider-lint +FILES:
    @uv run pre-commit run --files {{FILES}} >/dev/null || uv run pre-commit run --files {{FILES}}
