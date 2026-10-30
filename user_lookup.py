from pathlib import Path

from jira2prov.prov.provdoc import Jira2ProvNamespace

MISSING_NAMES_LOG = Path("missing_github_names.txt")

#  these have been redacted for the zenodo snapshot to avoid publishing developers real names
name_lookup = { }

lookup={

}

def github_user_from_name(real_name: str) -> str|None:
    normalised_name=real_name.strip().lower()
    github_user = lookup.get(normalised_name)
    if github_user is not None:
        return github_user
    _log_name_not_found(github_user=github_user,real_name=real_name)
    print(f"WARNING: github user for {real_name} not found in lookup. Check the log")
    return None

def get_normal_name(real_name: str) -> str|None:
    checked_name=name_lookup.get(real_name.strip().lower())
    if checked_name is not None:
        normalised_name=checked_name.strip().lower()
    else:
        normalised_name=real_name.strip().lower()
    return "".join(normalised_name.split())

def _log_name_not_found(github_user: str|None, real_name: str) -> None:
    if not github_user:
        with MISSING_NAMES_LOG.open("a") as log:
            log.write(real_name+"\n")

def mint_user_uri(real_name: str) -> str|None:
    uri = ''
    if real_name.startswith("@"):
        real_name = real_name.lstrip("@")
    github_user = github_user_from_name(real_name=real_name)
    if github_user is not None:
        uri = f"{Jira2ProvNamespace.USERS.url}{github_user}"
    else:
        username = get_normal_name(real_name=real_name)
        _log_name_not_found(real_name=real_name,github_user=github_user)
        uri=f"{Jira2ProvNamespace.PARS.url}{username}"

    return uri


