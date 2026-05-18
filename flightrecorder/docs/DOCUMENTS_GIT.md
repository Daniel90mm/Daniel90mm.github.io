# Documents git repo

`~/flightrecorder/documents/` is its own git repository, separate from the
merged site/source repo. This preserves append-only project document history
without contaminating the Hugo site's commit log.

## Initialization

`ensure_documents_repo(documents_path)` creates the directory and runs
`git init` if `.git` does not already exist. Idempotent -- safe to call on
every operation.

## Committing

`commit_documents_repo(documents_path, message)`:
1. Runs `ensure_documents_repo` first.
2. Stages all files with `git add .`.
3. Checks for changes with `git diff --cached --quiet`.
4. If the index is clean (no changes), **clean-tree commits are skipped**
   and the function returns `False`.
5. If there are changes, commits with author set to
   `flightrecorder <flightrecorder@example.invalid>` and returns `True`.

## Usage

Called by `apply_idea_operations()` after appending project documents, using
a message like `"Append ideas from <session-id>"`. The session-close pipeline
does not call `commit_documents_repo` directly -- it delegates to
`apply_idea_operations` which handles the commit when `commit_documents=True`.

## Why separate

- Project documents are irreplaceable runtime data. Their git history is an
  audit trail of what the system appended and when.
- Keeping them in their own repo avoids mixing automated commits with the
  public Hugo site's clean history.
- The canonical merged site/source repo at `~/hugo-site/` is disposable
  (re-clonable after push). The documents repo is the permanent record.
