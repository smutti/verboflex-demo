"""Small regression checks for setup isolation and deliberate fixture contracts."""

import unittest

import setup_portal
import validate


class DemoChecks(unittest.TestCase):
    def test_baseline_contract(self):
        validate.validate()

    def test_reject_ambiguous_keys(self):
        with self.assertRaises(ValueError):
            validate.unique_pairs([("save", "A"), ("save", "B")])

    def test_token_destination_requires_https_except_loopback(self):
        for url in [
            "http://example.com",
            "https://example.com/api/v1",
            "https://user:password@example.com",
            "https://example.com?redirect=1",
            "file:///tmp/data",
            "https://example.com/#fragment",
            "http://127.0.0.1.evil.test",
        ]:
            with self.subTest(url=url), self.assertRaises(ValueError):
                setup_portal.Api(url, "synthetic-test-token")
        for url in [
            "https://example.com",
            "http://localhost:8000",
            "http://127.0.0.1:8000",
            "http://[::1]:8000",
        ]:
            self.assertTrue(setup_portal.Api(url, "synthetic-test-token").origin)

    def test_api_refuses_off_contract_paths_before_network(self):
        api = setup_portal.Api("http://localhost:8000", "synthetic-test-token")
        with self.assertRaises(ValueError):
            api.call("GET", "//example.com/")

    def test_redirects_do_not_forward_credentials(self):
        self.assertIsNone(setup_portal.NoRedirect().redirect_request())


if __name__ == "__main__":
    unittest.main()
