# Connect the demo

Use an administrator account on a VerboFlex instance with the authoring, plurals, reuse and glossary update (database schema 0041 or later).

## In the portal

For each product in the README:

1. Create the product under **Products**.
2. In **Repositories**, choose **GitHub**, enter `smutti/verboflex-demo` and connect.
3. Add a direct translation source: branch `main`, the exact root from the table, base language `en`.
4. Run the preview, check the detected format and languages, then confirm.
5. Publish the configuration and run the import. Wait for **Current**.
6. Open **Strings** and choose English, Italian, Vietnamese and Arabic.

Keep the roots separate. Importing the repository root also discovers documentation and combines independent format examples.

For each demo product, set a maximum of **8** for Italian `settings_button`. In **Glossary**, add these English → Italian entries:

| Source | Target | Type |
| --- | --- | --- |
| workspace | spazio di lavoro | Preferred |
| workspace | workspace | Forbidden |

These settings belong to VerboFlex, not to the localization files. `demo.json` is the machine-readable setup recipe; the portal does not automatically read it.

## Optional API setup

```sh
git clone https://github.com/smutti/verboflex-demo.git
cd verboflex-demo
python3 tools/setup_portal.py --api-url http://localhost:8000
```

The script prompts privately for an existing **administrator bearer token**. Obtain it through your normal instance authentication flow; it is never printed, written to the receipt, or sent to GitHub. Remote API URLs must use HTTPS. The API URL is the server origin, without `/api/v1`.

The script creates four products, imports the catalogs with the normal Celery jobs, adds two glossary entries per product, and sets the Italian limit. It does not create users, change roles or edit existing non-demo products. It records IDs in ignored `.local/setup.json` and refuses untracked name collisions. Keep this receipt to resume a partial setup. Re-running preserves saved translation proposals and existing glossary/constraint settings; it is not a reset command.

For a source-refresh session:

```sh
python3 tools/setup_portal.py --api-url http://localhost:8000 --branch demo/live
```

Use a fresh installation or a different `--receipt` and `--name-prefix` to create an independent copy. A receipt is tied to one server, repository and branch. Do not share receipts between installations.

A GitHub rate limit can temporarily stop preview/import. The script reports the failed stage and retains the receipt; resume after the provider recovers. It never publishes a partial import itself.

## Before presenting

Run `python3 tools/validate.py`, open all four products and check that imports are current. Confirm exact/fuzzy suggestions for Italian and the red warning on `settings_button`. Use a reviewer for approvals and a translator for editing if you want to demonstrate role differences. Accounts and OAuth clients are configured separately in your instance.

To reset completely, create a fresh demo copy with a new name prefix and receipt. Remove only old demo products through the portal when no longer needed. A repository refresh does not erase local proposals, comments or glossary terms.
