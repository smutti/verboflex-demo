# Refresh and source changes

Use a disposable branch and a dedicated demo product. Keep `main` as the original catalog baseline. The supplied `demo/live` branch is available for this purpose; configure the product to import that branch **before** making changes.

## A normal refresh

1. Import the baseline of `demo/live` and leave one local draft for Italian `welcome_title`.
2. In a clean clone, switch to `demo/live` and edit `web/locales/en.json`: change `welcome_title` to `Welcome to your workspace`.
3. Remove `obsolete_notice` from **all four** files in `web/locales`. Deleting only the English entry would leave real target-only entries in the repository.
4. Add `release_banner` with an English source and optionally some target translations.
5. Review the diff, commit and push to `demo/live` using Git. This is a presenter action outside VerboFlex.
6. Run the product's refresh in the portal. Verify the new source, missing target rows, removed obsolete entries and the existing draft's source-change/reconciliation state.

The baseline validator intentionally fails after these edits: it checks the original demonstration contract. Review the changed fixture expectations if maintaining a new baseline. Do not modify `main` or disable validation just to make an exercise appear green.

## Rewritten history / rebase

A Git conflict occurs in Git before the updated branch can be imported. VerboFlex does not resolve textual Git merge conflicts. On a disposable branch, a rewrite that is no longer descended from the imported commit should trigger the portal's baseline-change review flow; inspect the comparison before accepting the new baseline. Never rewrite a shared or production branch for this exercise.

Use the project's existing integration tests for deterministic rewrite coverage. If demonstrating it live, create a fresh branch and product for that session, coordinate with anyone using it, and retain the original baseline. A standard fast-forward refresh and a rewritten-history confirmation are different demos.

## Full publication flow

VerboFlex does not yet write GitHub commits or pull requests. To demonstrate approval → change set → branch → commit → PR, copy the catalogs to a Bitbucket Cloud repository you control, connect it, and configure an allowed target branch there. Confirm the resulting PR diff contains only the intended changes. Do not imply that a GitHub demo import enables GitHub publication.
