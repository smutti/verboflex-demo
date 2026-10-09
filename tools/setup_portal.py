#!/usr/bin/env python3
"""Create/resume demo products through VerboFlex's public API; never writes Git."""

import argparse
import getpass
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from uuid import UUID, uuid5

ROOT = Path(__file__).resolve().parents[1]
MARKER = "Synthetic Northstar showcase from smutti/verboflex-demo."


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


class Api:
    def __init__(self, origin, token):
        parsed = urllib.parse.urlsplit(origin)
        if (
            parsed.username
            or parsed.password
            or parsed.query
            or parsed.fragment
            or parsed.path not in ("", "/")
            or not parsed.hostname
            or parsed.scheme not in ("http", "https")
            or parsed.scheme == "http"
            and parsed.hostname not in ("localhost", "127.0.0.1", "::1")
        ):
            raise ValueError(
                "Use an HTTPS API origin (HTTP is allowed only for loopback)."
            )
        self.origin = origin.rstrip("/")
        self.token = token
        self.opener = urllib.request.build_opener(NoRedirect())

    def call(self, method, path, payload=None):
        if not path.startswith("/api/v1/"):
            raise ValueError("Unexpected API path")
        headers = {
            "Authorization": "Bearer " + self.token,
            "Accept": "application/json",
        }
        body = None
        if payload is not None:
            headers["Content-Type"] = "application/json"
            body = json.dumps(payload).encode()
        request = urllib.request.Request(
            self.origin + path, data=body, method=method, headers=headers
        )
        try:
            with self.opener.open(request, timeout=45) as response:
                raw = response.read()
        except urllib.error.HTTPError as exc:
            # Avoid printing request headers, credentials or arbitrary remote content.
            raise RuntimeError(
                f"{method} {path}: HTTP {exc.code}; inspect the portal and resume with the same receipt."
            ) from None
        return json.loads(raw) if raw else None

    def poll(self, path, success, failure):
        deadline = time.monotonic() + 180
        while time.monotonic() < deadline:
            result = self.call("GET", path)
            if result["state"] in success:
                return result
            if result["state"] in failure:
                raise RuntimeError(
                    f"Job stopped: {result['state']} ({result.get('error_code') or result.get('error_category') or 'inspect the portal'})"
                )
            time.sleep(2)
        raise RuntimeError("Job exceeded 180 seconds; resume with the same receipt.")


def save_receipt(path, state):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(state, indent=2) + "\n")
    temporary.replace(path)


def all_products(api):
    items = []
    cursor = None
    for _ in range(100):
        params = {"limit": 100}
        if cursor:
            params["cursor"] = cursor
        page = api.call(
            "GET", "/api/v1/admin/products?" + urllib.parse.urlencode(params)
        )
        items.extend(page["items"])
        cursor = page["next_cursor"]
        if not cursor:
            return items
    raise RuntimeError("Product listing exceeded the setup bound")


def setup(api, *, receipt, branch="main", name_prefix="Demo · Northstar"):
    manifest = json.loads((ROOT / "demo.json").read_text())
    identity = {
        "api_url": api.origin,
        "repository": manifest["repository"],
        "branch": branch,
        "name_prefix": name_prefix,
    }
    state = (
        json.loads(receipt.read_text())
        if receipt.exists()
        else {**identity, "products": {}}
    )
    if any(state.get(k) != v for k, v in identity.items()):
        raise ValueError(
            "Receipt belongs to a different server/repository/branch/name prefix"
        )
    inventory = all_products(api)
    for product in manifest["products"]:
        name = name_prefix + " " + product["name"].split("Northstar ", 1)[1]
        if product["slug"] not in state["products"] and any(
            p["name"] == name for p in inventory
        ):
            raise ValueError(
                f"Untracked name collision: {name}. Use a fresh prefix or the original receipt."
            )
    if "repository_id" not in state:
        repository = api.call(
            "POST",
            "/api/v1/admin/github/repositories",
            {"owner": "smutti", "repository": "verboflex-demo"},
        )
        state["repository_id"] = repository["id"]
        save_receipt(receipt, state)
    # GitHub receives no portal token. Use one public read for the exact branch tip.
    url = (
        "https://api.github.com/repos/smutti/verboflex-demo/commits/"
        + urllib.parse.quote(branch, safe="")
    )
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "VerboFlex-demo-setup",
        },
    )
    with urllib.request.build_opener(NoRedirect()).open(
        request, timeout=30
    ) as response:
        commit = json.load(response)["sha"]
    for spec in manifest["products"]:
        name = name_prefix + " " + spec["name"].split("Northstar ", 1)[1]
        print(f"{name}: configuring", flush=True)
        record = state["products"].get(spec["slug"])
        if record is None:
            product = api.call(
                "POST", "/api/v1/admin/products", {"name": name, "description": MARKER}
            )
            record = {"product_id": product["id"]}
            state["products"][spec["slug"]] = record
            save_receipt(receipt, state)
        pid = record["product_id"]
        path = f"/api/v1/admin/products/{pid}"
        product = api.call("GET", path)
        revision = product["candidate_revision"] or product["active_revision"]
        if product["name"] != name or revision["description"] != MARKER:
            raise ValueError(
                "Receipt points to a product whose identity/description changed"
            )
        if product["active_revision"] is None:
            candidate = product["candidate_revision"]
            mappings_path = path + "/candidate/mappings"
            mappings = api.call("GET", mappings_path)["items"]
            if not mappings:
                mapping = api.call(
                    "POST",
                    mappings_path,
                    {
                        "topology": "direct",
                        "repository_id": state["repository_id"],
                        "localization_root": spec["root"],
                        "source_branch": branch,
                        "allowed_target_branches": [branch],
                        "default_target_branch": branch,
                        "expected_candidate_version": candidate["version"],
                    },
                )
            elif len(mappings) == 1:
                mapping = mappings[0]
            else:
                raise ValueError("Unexpected additional demo mappings")
            if (
                mapping["primary_repository_id"] != state["repository_id"]
                or mapping["primary_localization_root"] != spec["root"]
                or mapping["primary_source_branch"] != branch
            ):
                raise ValueError("Demo mapping changed; refusing to overwrite it")
            record["mapping_id"] = mapping["id"]
            save_receipt(receipt, state)
            candidate = api.call("GET", path)["candidate_revision"]
            job = api.call(
                "POST",
                mappings_path + "/" + mapping["id"] + "/preview-jobs",
                {
                    "expected_candidate_version": candidate["version"],
                    "commits": [{"role": "direct", "commit_hash": commit}],
                },
            )
            job = api.poll(
                "/api/v1/admin/preview-jobs/" + job["id"],
                {"succeeded"},
                {"failed", "timed_out"},
            )
            candidates = job["result"]["layout_candidates"]
            if len(candidates) != 1 or candidates[0]["format"] != spec["format"]:
                raise ValueError("Unexpected detected layouts; inspect the preview")
            layout = candidates[0]
            api.call(
                "POST",
                "/api/v1/admin/preview-jobs/" + job["id"] + "/confirmation",
                {
                    "preview_digest": job["result"]["digest"],
                    "layout_candidate_id": layout["id"],
                    "layout_candidate_version": layout["version"],
                    "base_language": "en",
                },
            )
            candidate = api.call("GET", path)["candidate_revision"]
            api.call(
                "POST",
                path + "/publish",
                {
                    "candidate_revision_id": candidate["id"],
                    "expected_candidate_version": candidate["version"],
                },
            )
        current = api.call("GET", path + "/published/mapping-imports")["items"]
        if len(current) != 1 or current[0]["mapping_id"] != record["mapping_id"]:
            raise ValueError("Published demo mapping changed")
        if current[0]["state"] != "current":
            job = current[0]
            if job["state"] not in ("queued", "running"):
                job = api.call(
                    "POST",
                    path + "/published/mappings/" + record["mapping_id"] + "/imports",
                )
            api.poll(
                path + "/imports/" + job["id"],
                {"current"},
                {"import_failed", "review_required"},
            )
        terms_path = f"/api/v1/products/{pid}/glossary"
        existing = api.call("GET", terms_path)
        if existing["next_after"]:
            raise ValueError("Demo glossary unexpectedly exceeds one page")
        known = {t["id"] for t in existing["items"]}
        for index, term in enumerate(manifest["glossary"]):
            term_id = str(uuid5(UUID(pid), "verboflex-demo-glossary-" + str(index)))
            if term_id not in known:
                api.call(
                    "PUT", terms_path + "/" + term_id, {"expected_version": 0, **term}
                )
        if not record.get("constraints_configured"):
            for rule in manifest["constraints"]:
                query = urllib.parse.urlencode(
                    {"product_id": pid, "language": rule["language"], "q": rule["key"]}
                )
                groups = api.call("GET", "/api/v1/translations?" + query)["items"]
                groups = [g for g in groups if g["raw_key"] == rule["key"]]
                if len(groups) != 1:
                    raise ValueError("Expected one constraint demo key")
                detail = api.call("GET", f"/api/v1/translations/{groups[0]['id']}")
                if detail["constraint_version"] is None:
                    api.call(
                        "PUT",
                        f"/api/v1/translations/{groups[0]['id']}/constraints/{rule['language']}",
                        {"max_chars": rule["max_chars"], "expected_version": 0},
                    )
            record["constraints_configured"] = True
            save_receipt(receipt, state)
        summary = api.call("GET", path + "/summary")
        record["summary"] = summary
        record["workspace_path"] = f"/products/{pid}/strings"
        save_receipt(receipt, state)
        print(
            f"{name}: current; {summary['source_string_count']} source strings, {summary['missing_count']} missing; {record['workspace_path']}",
            flush=True,
        )
    return state


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--api-url", default="http://localhost:8000")
    parser.add_argument("--branch", default="main")
    parser.add_argument("--name-prefix", default="Demo · Northstar")
    parser.add_argument("--receipt", type=Path, default=ROOT / ".local/setup.json")
    args = parser.parse_args()
    token = os.environ.get("VERBOFLEX_TOKEN") or getpass.getpass(
        "Administrator bearer token: "
    )
    try:
        if not token:
            raise ValueError("Token is required")
        setup(
            Api(args.api_url, token),
            receipt=args.receipt,
            branch=args.branch,
            name_prefix=args.name_prefix,
        )
    except (ValueError, RuntimeError, urllib.error.URLError) as exc:
        raise SystemExit(str(exc)) from None
