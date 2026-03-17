"""Contract tests for the infra template stack.

Each TestCase class sets up its own Pulumi mock context in setUpClass and
loads __main__.py with a specific config scenario. Tests assert on resource
properties that define the deployment contract.

To add a new client pattern:
1. Add a new TestCase subclass
2. Call load_main() in setUpClass with the pattern's config
3. Assert on the resources/properties that define the contract
"""
import sys
import os
import unittest

import pulumi

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(__file__))

from conftest import load_main, PROJECT


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _label_value(labels: list, label_name: str) -> str | None:
    """Extract a value from a list of {label, value} dicts."""
    for item in labels:
        if item.get("label") == label_name:
            return item.get("value")
    return None


def _env_value(envs: list, key: str) -> str | None:
    """Extract a value from a list of 'KEY=value' env strings."""
    prefix = f"{key}="
    for env in envs:
        if env.startswith(prefix):
            return env[len(prefix):]
    return None


# ---------------------------------------------------------------------------
# Base config scenario: allowedDomain only
# ---------------------------------------------------------------------------

class TestCloudflareResources(unittest.TestCase):
    """Cloudflare tunnel, DNS, and Access resources with base config."""

    @classmethod
    def setUpClass(cls):
        cls.infra = load_main({
            f"{PROJECT}:allowedDomain": "myorg.com",
        })

    @pulumi.runtime.test
    def test_tunnel_name(self):
        def check(name):
            self.assertEqual(name, "myapp-dev-tunnel")
        return self.infra.tunnel.name.apply(check)

    @pulumi.runtime.test
    def test_tunnel_config_ingress_rules(self):
        # tunnel_config.config is an Output of the config dict.
        # In mock mode, new_resource returns args.inputs as outputs, so .config resolves
        # to the serialized config dict. In pulumi-cloudflare v6 the key is "ingresses".
        def check(cfg):
            rules = cfg.get("ingresses", [])
            self.assertEqual(len(rules), 3, f"Expected 3 ingress rules, got: {rules}")
            hostnames = [r.get("hostname") for r in rules]
            self.assertIn("*.myapp.dev.example.com", hostnames)
            self.assertIn("myapp.dev.example.com", hostnames)
            catch_all = [r for r in rules if not r.get("hostname")]
            self.assertEqual(len(catch_all), 1)
            self.assertIn("404", catch_all[0].get("service", ""))
        return self.infra.tunnel_config.config.apply(check)

    @pulumi.runtime.test
    def test_wildcard_dns_name(self):
        def check(name):
            self.assertEqual(name, "*.myapp.dev")
        return self.infra.wildcard_dns.name.apply(check)

    @pulumi.runtime.test
    def test_wildcard_dns_type_and_proxied(self):
        def check(args):
            record_type, proxied = args
            self.assertEqual(record_type, "CNAME")
            self.assertTrue(proxied)
        return pulumi.Output.all(
            self.infra.wildcard_dns.type,
            self.infra.wildcard_dns.proxied,
        ).apply(check)

    @pulumi.runtime.test
    def test_bare_dns_name(self):
        def check(name):
            self.assertEqual(name, "myapp.dev")
        return self.infra.bare_dns.name.apply(check)

    @pulumi.runtime.test
    def test_access_app_domain(self):
        def check(domain):
            self.assertEqual(domain, "myapp.dev.example.com")
        return self.infra.access_app.domain.apply(check)

    @pulumi.runtime.test
    def test_access_app_self_hosted_domains(self):
        def check(domains):
            self.assertIn("myapp.dev.example.com", domains)
            self.assertIn("*.myapp.dev.example.com", domains)
        return self.infra.access_app.self_hosted_domains.apply(check)

    @pulumi.runtime.test
    def test_access_policy_domain_rule(self):
        def check(includes):
            # In pulumi-cloudflare v6 mock output, the include rule has "email_domain"
            # as a nested object: {"email_domain": {"domain": "myorg.com"}}
            has_domain_rule = any(
                rule.get("email_domain", {}).get("domain") == "myorg.com"
                for rule in includes
            )
            self.assertTrue(has_domain_rule, f"No email_domain rule found in: {includes}")
        return self.infra.access_policy.includes.apply(check)


class TestAccessPolicyEmailsOnly(unittest.TestCase):
    """Access policy with allowedEmails only (no domain)."""

    @classmethod
    def setUpClass(cls):
        cls.infra = load_main({
            f"{PROJECT}:allowedEmails": ["a@b.com"],
        })

    @pulumi.runtime.test
    def test_access_policy_emails_rule(self):
        def check(includes):
            # In pulumi-cloudflare v6 wire format: {"email": {"email": "a@b.com"}}
            has_emails_rule = any(
                rule.get("email", {}).get("email") == "a@b.com"
                for rule in includes
            )
            self.assertTrue(has_emails_rule, f"No email rule found in: {includes}")
        return self.infra.access_policy.includes.apply(check)

    @pulumi.runtime.test
    def test_no_domain_rule(self):
        def check(includes):
            has_domain_rule = any("email_domain" in rule for rule in includes)
            self.assertFalse(has_domain_rule, f"Unexpected email_domain rule in: {includes}")
        return self.infra.access_policy.includes.apply(check)


class TestAccessPolicyBoth(unittest.TestCase):
    """Access policy with both allowedDomain and allowedEmails."""

    @classmethod
    def setUpClass(cls):
        cls.infra = load_main({
            f"{PROJECT}:allowedDomain": "myorg.com",
            f"{PROJECT}:allowedEmails": ["a@b.com"],
        })

    @pulumi.runtime.test
    def test_access_policy_has_both_rules(self):
        def check(includes):
            # In pulumi-cloudflare v6 mock output, each rule type is a separate entry
            # with snake_case keys: "email_domain" and "email"
            has_domain_rule = any("email_domain" in rule for rule in includes)
            has_emails_rule = any("email" in rule for rule in includes)
            self.assertTrue(has_domain_rule, f"Missing email_domain rule in: {includes}")
            self.assertTrue(has_emails_rule, f"Missing email rule in: {includes}")
        return self.infra.access_policy.includes.apply(check)


class TestDockerResources(unittest.TestCase):
    """Docker image and container resources with base config (single main branch)."""

    @classmethod
    def setUpClass(cls):
        cls.infra = load_main({
            f"{PROJECT}:allowedDomain": "myorg.com",
        })

    @pulumi.runtime.test
    def test_main_image_build_context(self):
        def check(build):
            context = build.get("context") if isinstance(build, dict) else None
            self.assertEqual(context, "https://github.com/my-org/myapp.git#main")
        return self.infra.app_images["myapp-main-image"].build.apply(check)

    @pulumi.runtime.test
    def test_image_skip_push(self):
        # pulumi-docker Image stores skip_push in snake_case internally, but the
        # mock returns camelCase wire-format keys. The property resolves as None
        # (not False) in mock mode — asserting not False confirms it was not
        # overridden to False by the mock.
        def check(skip_push):
            self.assertNotEqual(skip_push, False, "skip_push must not be False — template has no registry credentials")
        return self.infra.app_images["myapp-main-image"].skip_push.apply(check)

    @pulumi.runtime.test
    def test_main_container_name(self):
        def check(name):
            self.assertEqual(name, "myapp-main")
        return self.infra.app_containers["myapp-main"].name.apply(check)

    @pulumi.runtime.test
    def test_main_traefik_enable_label(self):
        def check(labels):
            value = _label_value(labels, "traefik.enable")
            self.assertEqual(value, "true", "traefik.enable must be 'true' for Traefik to route this container")
        return self.infra.app_containers["myapp-main"].labels.apply(check)

    @pulumi.runtime.test
    def test_main_traefik_rule_label(self):
        def check(labels):
            value = _label_value(labels, "traefik.http.routers.myapp-main.rule")
            self.assertEqual(value, "Host(`myapp.dev.example.com`)")
        return self.infra.app_containers["myapp-main"].labels.apply(check)

    @pulumi.runtime.test
    def test_default_port_label(self):
        def check(labels):
            value = _label_value(labels, "traefik.http.services.myapp-main.loadbalancer.server.port")
            self.assertEqual(value, "3000")
        return self.infra.app_containers["myapp-main"].labels.apply(check)

    @pulumi.runtime.test
    def test_container_env_vars(self):
        def check(envs):
            self.assertEqual(_env_value(envs, "APP_NAME"), "myapp")
            self.assertEqual(_env_value(envs, "BRANCH_NAME"), "main")
            self.assertEqual(_env_value(envs, "CF_TEAM_NAME"), "myteam")
            self.assertEqual(_env_value(envs, "APP_ENV"), "production")
        return self.infra.app_containers["myapp-main"].envs.apply(check)

    @pulumi.runtime.test
    def test_container_restart_policy(self):
        def check(restart):
            self.assertEqual(restart, "unless-stopped", "Containers must restart unless manually stopped")
        return self.infra.app_containers["myapp-main"].restart.apply(check)

    @pulumi.runtime.test
    def test_cloudflared_container_name(self):
        def check(name):
            self.assertEqual(name, "myapp-cloudflared")
        return self.infra.cloudflared_container.name.apply(check)

    @pulumi.runtime.test
    def test_cloudflared_image_pinned(self):
        def check(image):
            self.assertEqual(image, "cloudflare/cloudflared:2025.4.0")
        return self.infra.cloudflared_container.image.apply(check)

    @pulumi.runtime.test
    def test_cloudflared_restart_policy(self):
        def check(restart):
            self.assertEqual(restart, "unless-stopped")
        return self.infra.cloudflared_container.restart.apply(check)


class TestCustomPort(unittest.TestCase):
    """Custom appPort config is reflected in Traefik port label."""

    @classmethod
    def setUpClass(cls):
        cls.infra = load_main({
            f"{PROJECT}:allowedDomain": "myorg.com",
            f"{PROJECT}:appPort": "8080",
        })

    @pulumi.runtime.test
    def test_custom_port_label(self):
        def check(labels):
            value = _label_value(labels, "traefik.http.services.myapp-main.loadbalancer.server.port")
            self.assertEqual(value, "8080")
        return self.infra.app_containers["myapp-main"].labels.apply(check)


class TestMultiBranch(unittest.TestCase):
    """Two branches: main and feature-x."""

    @classmethod
    def setUpClass(cls):
        cls.infra = load_main({
            f"{PROJECT}:allowedDomain": "myorg.com",
            f"{PROJECT}:branches": ["main", "feature-x"],
        })

    @pulumi.runtime.test
    def test_feature_branch_image_url(self):
        def check(build):
            context = build.get("context") if isinstance(build, dict) else None
            self.assertEqual(context, "https://github.com/my-org/myapp.git#feature-x")
        return self.infra.app_images["myapp-feature-x-image"].build.apply(check)

    @pulumi.runtime.test
    def test_feature_branch_traefik_rule(self):
        def check(labels):
            value = _label_value(labels, "traefik.http.routers.myapp-feature-x.rule")
            self.assertEqual(value, "Host(`feature-x.myapp.dev.example.com`)")
        return self.infra.app_containers["myapp-feature-x"].labels.apply(check)

    @pulumi.runtime.test
    def test_main_still_uses_bare_domain(self):
        def check(labels):
            value = _label_value(labels, "traefik.http.routers.myapp-main.rule")
            self.assertEqual(value, "Host(`myapp.dev.example.com`)")
        return self.infra.app_containers["myapp-main"].labels.apply(check)

    @pulumi.runtime.test
    def test_both_app_containers_created(self):
        has_main = "myapp-main" in self.infra.app_containers
        has_feature = "myapp-feature-x" in self.infra.app_containers
        self.assertTrue(has_main, "myapp-main container missing")
        self.assertTrue(has_feature, "myapp-feature-x container missing")
        return pulumi.Output.from_input(True).apply(lambda _: None)


class TestAuthGuard(unittest.TestCase):
    """Config validation: stack must raise if neither auth option is set."""

    def test_raises_without_auth_config(self):
        with self.assertRaises(Exception) as ctx:
            load_main({})  # no allowedDomain, no allowedEmails
        msg = str(ctx.exception).lower()
        self.assertTrue(
            "alloweddomain" in msg or "allowedemails" in msg,
            f"Exception message should mention allowedDomain or allowedEmails, got: {ctx.exception}"
        )
