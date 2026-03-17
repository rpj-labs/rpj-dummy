import re


def sanitise_branch(branch: str) -> str:
    """Sanitise a git branch name for use in Docker names and subdomains.

    Replaces any character outside [a-zA-Z0-9-] with '-', then strips
    leading and trailing hyphens.
    """
    return re.sub(r"[^a-zA-Z0-9-]", "-", branch).strip("-")


def make_branch_domain(branch: str, app_domain: str) -> str:
    """Return the domain for a branch deployment.

    main -> app_domain (bare)
    other -> {sanitised_branch}.{app_domain}
    """
    if branch == "main":
        return app_domain
    return f"{sanitise_branch(branch)}.{app_domain}"
