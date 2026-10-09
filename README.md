# VerboFlex Demo

[![Validate demo catalogs](https://github.com/smutti/verboflex-demo/actions/workflows/validate.yml/badge.svg)](https://github.com/smutti/verboflex-demo/actions/workflows/validate.yml)

A ready-to-import showcase for [VerboFlex](https://github.com/smutti/verboflex), built around **Northstar**, a fictional collaboration app. All text is original synthetic sample content. There are no customer files, credentials, or runnable application dependencies.

**16 catalogs · 4 formats · 4 languages · 400 imported values**

English is the source language. Italian, Vietnamese and Arabic demonstrate incomplete coverage, different plural rules and right-to-left text. Translations are illustrative demo copy, not linguistically certified release content.

## Start here

1. [Connect the repository](docs/setup.md) to your VerboFlex instance.
2. Follow the [10-minute demo](docs/presenter-guide.md).
3. Try [repository refresh and conflict scenarios](docs/refresh-and-conflicts.md) on a separate demo branch.

| Demo product | Format | Translation root | Values |
| --- | --- | --- | ---: |
| Northstar Android | Android XML + native plurals | `android/app/src/main/res` | 111 |
| Northstar Web | JSON | `web/locales` | 89 |
| Northstar Desktop | Qt TS + native numerus forms | `desktop/translations` | 111 |
| Northstar iOS | Apple `.strings` | `ios/Resources` | 89 |

Create one product per row, select branch `main` and base language `en`. The optional setup script does this and adds the glossary and length-limit examples. A separate `demo/live` branch starts at the same catalogs and can be used for refresh demonstrations while preserving `main`.

## What you can show

| Feature | Ready-made example |
| --- | --- |
| Coverage dashboard | Different gaps in Italian, Vietnamese and Arabic |
| Multilingual editor and filters | Search `save`; compare source and target rows |
| Missing translations | Empty Italian `empty_search`; absent `new_feature` |
| New keys | Add `tour_hint` to an existing catalog and review the new entry |
| Native plurals | `files_selected`; incomplete Arabic `uploads_pending` |
| Exact reuse | Italian `save_profile` suggests `save_changes` at 100% |
| Fuzzy reuse | Italian `save_profile_changes` suggests `save_account_changes` |
| Character limits | Italian `settings_button`: 12 characters, maximum 8 after setup |
| Glossary | `create_workspace` contains a deliberately forbidden Italian term |
| Draft / approved / rejected | Edit a string, save, review and inspect history |
| Collaboration and activity | Add a comment; optionally mention a consenting demo participant |
| MCP + OAuth | Search, inspect suggestions and edit with your instance's configured client |
| Refresh and removed keys | Controlled source edits on a disposable demo branch |

GitHub currently supports **public import, refresh and local review** in VerboFlex. Saving or approving does not publish a GitHub commit or PR. To demonstrate the portal's complete branch/commit/PR submission flow, mirror these catalogs to a **Bitbucket Cloud** repository you control and configure that provider. Private GitHub import, cross-project reuse, JSON ICU plurals and Apple `.stringsdict` are outside this demo's supported scope.

## Validate

Python 3.11+; no packages required:

```sh
python3 tools/validate.py
```

Maintainers can also run the actual VerboFlex preview and import parsers (using that project's installed backend environment):

```sh
../verboflex/backend/.venv/bin/python tools/validate.py --verboflex-root ../verboflex
```

The validator protects intentional gaps and demo cases as well as file syntax. A source-change exercise changes those expectations: run it on a demo branch and retain `main` as the baseline. This small dataset is a functional showcase, not a load test.

MIT licensed. See [LICENSE](LICENSE).
