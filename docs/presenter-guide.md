# A 10-minute demo

Start with **Demo · Northstar Web**. Keep English and Italian visible; add Vietnamese and Arabic when comparing coverage. Use the same sample product names throughout the presentation.

| Time | Action | What to show |
| --- | --- | --- |
| 0–1 min | Open the product summary | Coverage and which languages need work. Empty and absent translations both matter. |
| 1–2 min | Open Strings; search `save` | One key with its language rows; searchable language filters. |
| 2–3 min | Edit Italian `save_profile` | Suggestions includes `Save changes` at 100%. **Use** fills the editor; **Save** persists a local draft. |
| 3–4 min | Edit Italian `save_profile_changes` | A similar source appears with a score, highlighted differences and provenance. Verify it before saving. |
| 4–5 min | Search `settings_button` | The 12-character Italian value exceeds its maximum of 8. Red remains visible outside focus. Try `Opzioni` and save. |
| 5–6 min | Edit Italian `create_workspace` | The glossary warns about `workspace`. Replace with `Crea uno spazio di lavoro`. Glossary warnings are advisory. |
| 6–7 min | Filter missing translations | Fill Italian `empty_search`. For `new_feature`, choose **Add translation**, select the Italian catalog and enter `Esplora i progetti condivisi`. |
| 7–8 min | Choose **New key** | In the English JSON file create `tour_hint` with `Explore your workspace`. Leave the parent path `[]`. Save, then review it under **New entries**. |
| 8–9 min | Switch to Northstar Android, then Desktop | Inspect `files_selected` in Italian, Vietnamese and Arabic. Android uses named quantities; Qt uses ordered forms. Complete Arabic `uploads_pending` via **Add forms** or the empty-form editor. |
| 9–10 min | Review a saved change; open History and Comments | Approve or reject as a reviewer. Add a plain comment. Show activity in the dashboard. |

When adding a new key in Qt, also enter source text and context `Northstar`. For Android and iOS choose the relevant existing file. Each new-entry draft targets one file/language; a source draft does not instantly create every target translation or change imported coverage.

## Follow-up scenarios

- **Placeholders:** inspect `welcome_user` and `download_progress`. The same message uses `{name}` in JSON, `%1$s` in Android, `%1` in Qt and `%@` in iOS. Reuse stays within a format and checks compatible placeholders; do not present this as universal validation for every arbitrary edit.
- **Review states:** leave one draft, approve one and reject another, then use state filters. Imported repository text is not automatically reviewer-approved. Suggestions label their origin.
- **Mentions:** use a consenting demo account if demonstrating notifications. Selecting the user should close the chooser; posting a mention delivers a notification to that account.
- **Concurrent edits:** open the same translation in two sessions. Save one, then attempt a save from the older session; the version check should protect the newer edit. Refresh the older view rather than overwriting it.
- **MCP:** connect Codex or Claude to your instance's configured OAuth MCP endpoint. Ask it to find missing Italian translations in the demo product, inspect a key, or explain a suggestion. Require a deliberate write instruction before editing. Do not store tokens in this repository.
- **Audit and permissions:** show authorized changes in the admin audit view, then compare reviewer/translator/viewer access with separately configured accounts.
- **Backup/restore:** demonstrate only in an isolated deployment using the application runbook. Catalog fixtures do not provision or validate production backup infrastructure.

## Keep the claims precise

Saving is a local draft. **Use** is not a save. Approval is not a GitHub push. Missing imported values and unimported new-entry drafts have different coverage behavior. Scores describe text similarity, not translation quality. Do not use this dataset as evidence of production throughput.
