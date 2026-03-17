import pulumi
import pulumi_cloudflare as cloudflare
import pulumi_docker as docker

from helpers import sanitise_branch, make_branch_domain

config = pulumi.Config()
account_id = config.require("accountId")
zone_id = config.require("zoneId")
domain = config.require("domain")
app_slug = config.require("appSlug")
app_org = config.require("appOrg")
dev_subdomain = config.get("devSubdomain") or "dev"
cf_team_name = config.require("cfTeamName")
allowed_emails = config.get_object("allowedEmails")
allowed_domain = config.get("allowedDomain")

if not allowed_domain and not allowed_emails:
    raise Exception(
        "Pulumi config error: at least one of 'allowedDomain' or 'allowedEmails' must be set. "
        "Run: pulumi config set allowedDomain yourdomain.com"
    )
google_idp_id = config.require("googleIdpId")
app_port = int(config.get("appPort") or "3000")
branches = config.get_object("branches") or ["main"]

app_domain = f"{app_slug}.{dev_subdomain}.{domain}"

# ── Cloudflare: Tunnel ───────────────────────────────────────────────────────

tunnel = cloudflare.ZeroTrustTunnelCloudflared(
    "tunnel",
    account_id=account_id,
    name=f"{app_slug}-dev-tunnel",
    tunnel_secret=config.require_secret("tunnelSecret"),
    config_src="cloudflare",
)

tunnel_config = cloudflare.ZeroTrustTunnelCloudflaredConfig(
    "tunnel-config",
    account_id=account_id,
    tunnel_id=tunnel.id,
    config=cloudflare.ZeroTrustTunnelCloudflaredConfigConfigArgs(
        ingresses=[
            cloudflare.ZeroTrustTunnelCloudflaredConfigConfigIngressArgs(
                hostname=f"*.{app_domain}",
                service="http://localhost:80",
            ),
            cloudflare.ZeroTrustTunnelCloudflaredConfigConfigIngressArgs(
                hostname=app_domain,
                service="http://localhost:80",
            ),
            cloudflare.ZeroTrustTunnelCloudflaredConfigConfigIngressArgs(
                service="http_status:404",
            ),
        ],
    ),
)

# ── Cloudflare: DNS ──────────────────────────────────────────────────────────

tunnel_cname = tunnel.id.apply(lambda id: f"{id}.cfargotunnel.com")

wildcard_dns = cloudflare.DnsRecord(
    "wildcard-dns",
    zone_id=zone_id,
    name=f"*.{app_slug}.{dev_subdomain}",
    type="CNAME",
    content=tunnel_cname,
    proxied=True,
    ttl=1,
)

bare_dns = cloudflare.DnsRecord(
    "bare-dns",
    zone_id=zone_id,
    name=f"{app_slug}.{dev_subdomain}",
    type="CNAME",
    content=tunnel_cname,
    proxied=True,
    ttl=1,
)

# ── Cloudflare: Access ───────────────────────────────────────────────────────

access_app = cloudflare.ZeroTrustAccessApplication(
    "access-app",
    account_id=account_id,
    name=f"{app_slug} (dev)",
    domain=app_domain,
    self_hosted_domains=[app_domain, f"*.{app_domain}"],
    type="self_hosted",
    session_duration="24h",
    auto_redirect_to_identity=True,
)

include_rules = []
if allowed_domain:
    include_rules.append(
        cloudflare.ZeroTrustAccessPolicyIncludeArgs(
            email_domain=cloudflare.ZeroTrustAccessPolicyIncludeEmailDomainArgs(
                domain=allowed_domain,
            ),
        )
    )
if allowed_emails:
    for email in allowed_emails:
        include_rules.append(
            cloudflare.ZeroTrustAccessPolicyIncludeArgs(
                email=cloudflare.ZeroTrustAccessPolicyIncludeEmailArgs(
                    email=email,
                ),
            )
        )

access_policy = cloudflare.ZeroTrustAccessPolicy(
    "access-policy",
    account_id=account_id,
    name=f"Allow {app_slug} users",
    decision="allow",
    includes=include_rules,
)

# ── Docker: cloudflared tunnel ───────────────────────────────────────────────
# Token passed via env var to keep it out of `docker inspect` command args.

tunnel_token = cloudflare.get_zero_trust_tunnel_cloudflared_token_output(
    account_id=account_id,
    tunnel_id=tunnel.id,
)

cloudflared_container = docker.Container(
    "cloudflared",
    name=f"{app_slug}-cloudflared",
    image="cloudflare/cloudflared:2025.4.0",
    command=["tunnel", "run"],
    envs=[tunnel_token.token.apply(lambda t: f"TUNNEL_TOKEN={t}")],
    networks_advanced=[docker.ContainerNetworksAdvancedArgs(name="traefik-web")],
    restart="unless-stopped",
    opts=pulumi.ResourceOptions(depends_on=[tunnel_config]),
)

# ── Docker: app containers per branch ───────────────────────────────────────
# Each branch is built from GitHub and gets its own container + Traefik route.
# To add a branch:    pulumi config set --json branches '["main","feature-x"]'
# To remove a branch: pulumi config set --json branches '["main"]'
# Then: pulumi up

app_images: dict = {}
app_containers: dict = {}

for branch in branches:
    sanitised_branch = sanitise_branch(branch)
    safe_name = f"{app_slug}-{sanitised_branch}"
    _branch_domain = make_branch_domain(branch, app_domain)
    github_url = f"https://github.com/{app_org}/{app_slug}.git#{branch}"

    image = docker.Image(
        f"{safe_name}-image",
        build=docker.DockerBuildArgs(context=github_url),
        image_name=f"{safe_name}:latest",
        skip_push=True,
    )
    app_images[f"{safe_name}-image"] = image

    container = docker.Container(
        safe_name,
        name=safe_name,
        image=image.image_name,
        networks_advanced=[docker.ContainerNetworksAdvancedArgs(name="traefik-web")],
        labels=[
            docker.ContainerLabelArgs(label="traefik.enable", value="true"),
            docker.ContainerLabelArgs(
                label=f"traefik.http.routers.{safe_name}.rule",
                value=f"Host(`{_branch_domain}`)",
            ),
            docker.ContainerLabelArgs(
                label=f"traefik.http.services.{safe_name}.loadbalancer.server.port",
                value=str(app_port),
            ),
        ],
        envs=[
            f"APP_NAME={app_slug}",
            f"BRANCH_NAME={branch}",
            f"CF_TEAM_NAME={cf_team_name}",
            "APP_ENV=production",
        ],
        restart="unless-stopped",
    )
    app_containers[safe_name] = container

# ── Outputs ──────────────────────────────────────────────────────────────────

pulumi.export("app_url", f"https://{app_domain}")
pulumi.export("access_app_aud", access_app.aud)
