# CI Test Reliability Implementation Plan

> **For Hermes:** Use subagent-driven-development skill to implement this plan task-by-task.

**Goal:** Make `keycrm_bot` testable from repo root, add CI, and cover KeyCRM client pagination/error behavior.

**Architecture:** Keep the PR small and production-safe. Use standard Python project metadata for pytest import reliability, add one GitHub Actions workflow, and test `KeyCRMClient` through `httpx.MockTransport` by injecting a test transport into the client.

**Tech Stack:** Python 3.11, pytest, httpx, python-telegram-bot, GitHub Actions.

---

### Task 1: Add pytest/project configuration

**Objective:** Make `pytest -q` import `app` reliably from the repository root.

**Files:**
- Create: `pyproject.toml`
- Test: `tests/test_report.py`

**Step 1: Write config**

Create `pyproject.toml` with pytest path configuration:

```toml
[tool.pytest.ini_options]
pythonpath = ["."]
testpaths = ["tests"]
```

**Step 2: Run tests**

Run: `pytest -q`
Expected: existing report tests pass instead of collection failing with `ModuleNotFoundError: No module named 'app'`.

**Step 3: Commit**

```bash
git add pyproject.toml
git commit -m "test: configure pytest imports"
```

### Task 2: Add KeyCRM client transport injection

**Objective:** Allow KeyCRM client tests to use `httpx.MockTransport` without network calls.

**Files:**
- Modify: `app/keycrm.py`
- Test: `tests/test_keycrm.py`

**Step 1: Write failing tests**

Add tests that instantiate `KeyCRMClient(settings, transport=mock_transport)` and verify pagination plus HTTP error wrapping.

**Step 2: Implement minimal change**

Update `KeyCRMClient.__init__` to accept optional `transport: httpx.AsyncBaseTransport | None = None` and pass it to `httpx.AsyncClient`.

**Step 3: Run tests**

Run: `pytest -q`
Expected: all tests pass.

**Step 4: Commit**

```bash
git add app/keycrm.py tests/test_keycrm.py
git commit -m "test: cover keycrm client pagination"
```

### Task 3: Add GitHub Actions pytest workflow

**Objective:** Verify tests automatically on PRs and main branch pushes.

**Files:**
- Create: `.github/workflows/tests.yml`

**Step 1: Add workflow**

Use `actions/setup-python` with Python 3.11, install `requirements.txt` and `pytest`, then run `pytest -q`.

**Step 2: Run local verification**

Run: `pytest -q`
Expected: pass.

**Step 3: Commit**

```bash
git add .github/workflows/tests.yml
git commit -m "ci: run pytest"
```

### Task 4: Final verification and PR

**Objective:** Push branch and open a small PR linked to issue #1.

**Files:**
- No code changes expected.

**Step 1: Verify status and tests**

Run:

```bash
git status --short
pytest -q
git log --oneline main..HEAD
```

Expected: only intended files changed and tests pass.

**Step 2: Push and open PR**

```bash
git push -u origin chore/ci-test-reliability
gh pr create --fill --body-file <body>
```

**Step 3: Check CI**

Run: `gh pr checks --watch`
Expected: GitHub Actions test workflow passes.
