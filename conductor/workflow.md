# Workflow: Kindle Butler Development

## Principles
1. **Research -> Strategy -> Execution**: Never code without understanding.
2. **Validate via Test**: Every feature must have a corresponding test (unit or e2e).
3. **Safety First**: Backup Kindle data before any destructive operation.
4. **Goat Principle**: Functionality > Aesthetics (though Rich UI is preferred).

## Standard Track Process
1. **Research**: Map existing code, find dependencies, verify Kindle mount behavior.
2. **Plan**: Create `plan.md` in the track folder.
3. **Act**: Implement changes surgically.
4. **Validate**: Run full test suite and `PROJECT_DIAGNOSTICS.md` checks.
5. **Verify**: User manual verification on real hardware (if possible) or via comprehensive mocks.

## Checkpoint Convention
Commits or plan markers should include `[checkpoint: hash]` or `[checkpoint: description]` to indicate a stable state.
