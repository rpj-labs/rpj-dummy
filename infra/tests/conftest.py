"""Shared test infrastructure for Pulumi infra stack tests.

To add a new config scenario:
1. Call load_main() with the appropriate overrides in setUpClass
2. Write a unittest.TestCase class with @pulumi.runtime.test methods

Extension point: add new keys to BASE_CONFIG or pass overrides to load_main()
for each new deployment pattern.
"""
import importlib.util
import json
import os
import sys
import types

import pulumi
import pulumi.runtime

PROJECT = "testproject"
STACK = "teststack"

INFRA_MAIN = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "__main__.py"))
INFRA_DIR = os.path.dirname(INFRA_MAIN)

# All keys that __main__.py calls config.require() or config.get() on.
# devSubdomain is omitted — the code defaults it to "dev", and all domain
# assertions in the test suite assume that default.
BASE_CONFIG = {
    "accountId": "test-account-id",
    "zoneId": "test-zone-id",
    "domain": "example.com",
    "appSlug": "myapp",
    "appOrg": "my-org",
    "cfTeamName": "myteam",
    # Required by config.require() but not used in any resource constructor:
    "googleIdpId": "test-idp-id",
    # tunnelSecret is a secret in production; in mock mode a plain string works:
    "tunnelSecret": "test-secret",
}


class InfraMocks(pulumi.runtime.Mocks):
    """Pass-through mock: returns resource name as id, passes inputs as outputs."""

    def new_resource(self, args: pulumi.runtime.MockResourceArgs):
        return [args.name + "_id", args.inputs]

    def call(self, args: pulumi.runtime.MockCallArgs):
        if args.token == "cloudflare:index/getZeroTrustTunnelCloudflaredToken:getZeroTrustTunnelCloudflaredToken":
            return {"token": "mock-tunnel-token", "id": "mock-id"}
        return {}


def load_main(extra_config: dict | None = None) -> types.ModuleType:
    """Set up Pulumi mocks with the given config and load __main__.py.

    Call this in setUpClass of each TestCase. Each call resets the Pulumi
    mock runtime, so different TestCase classes can use different configs.

    Args:
        extra_config: Keys to merge on top of BASE_CONFIG. Use PROJECT: prefix.
                      List/dict values are automatically JSON-serialized
                      (needed for config.get_object keys like branches, allowedEmails).

    Returns:
        The loaded __main__ module with all resource attributes accessible.

    Example:
        cls.infra = load_main({f"{PROJECT}:allowedDomain": "myorg.com"})
    """
    # Build full config dict with project-prefixed keys
    full_config: dict[str, str] = {}
    for k, v in BASE_CONFIG.items():
        full_config[f"{PROJECT}:{k}"] = v
    for k, v in (extra_config or {}).items():
        # Serialize list/dict values to JSON strings for config.get_object()
        full_config[k] = json.dumps(v) if isinstance(v, (list, dict)) else v

    # Reset Pulumi mock runtime — must happen before exec_module
    pulumi.runtime.set_mocks(InfraMocks(), project=PROJECT, stack=STACK, preview=False)
    pulumi.runtime.set_all_config(full_config)

    # Add infra dir to sys.path so __main__.py can find helpers.py
    if INFRA_DIR not in sys.path:
        sys.path.insert(0, INFRA_DIR)

    # Load __main__.py directly (not as a package — Pulumi runs it directly)
    spec = importlib.util.spec_from_file_location("infra", INFRA_MAIN)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
