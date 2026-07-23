from pathlib import Path

from jira2prov.prov.provdoc import Jira2ProvNamespace

MISSING_NAMES_LOG = Path("missing_github_names.txt")

name_lookup = {
"bjoern weissenfels" : "bjorn weissenfels",
"björn weißenfels":"bjorn weissenfels",
"tillmann bielefeld" : "tillmann bielefeld",
"tillmann carlos bielefeld":"tillmann bielefeld",
"armin möbius":"armin mobius",
"marius löwe":"marius lowe",
"pascal brandt": "pascale brandt", }

lookup={
"andre van hoorn" : "avanhoorn",
"andré van hoorn" : "avanhoorn",
"christian wulf" : "ChristianWulf",
"christian zirkelbach": "czirkelbach",
"christian" : "czirkelbach",
"christianwulf" : "ChristianWulf",
"clemens kurz": "cbkurz",
"danish manzoor" : "danishmanzoor",
"david georg reichelt": "DaGeRe",
"dennis kieselhorst" : "deki",
"ducan okanovic":"okism",
"duellmtk": "duelle",
"duellmtk@studi.informatik.uni-stuttgart.de" : "duelle",
"dusan okanovic":"okism",
"dušan okanović":"okism",
"felix magedanz": "FlxMgdnz",
"florian fittkau" : "FFittkau",
"github" : "github",
"holger knoche" : "holgerknoche",
"jan waller": "JanWaller",
"jurgen walter" : "juergen-walter",
"jürgen walter" : "juergen-walter",
"lars blumke": "labl-ppi",
"lars blümke": "labl-ppi",
"mad@informatik.uni-kiel.de" : "madcau",
"marc adolf" : "madcau",
"micky singh multani" : "msm-ppi",
"nie" : "nils-christian",
"nils christian ehmke" : "nils-christian",
"nils ehmke": "nils-christian",
"reiner jung":"rju",
"robert von massow": "RvonMassow",
"robin finkbeiner":"renderfehler",
"sebastian harner": "Rackles",
"sonke reimer" : "SonReimer",
"soren henning":"SoerenHenning",
"sven ulrich":"SvenUlrich",
"sönke reimer" : "SonReimer",
"sören henning":"SoerenHenning",
"teerat pitakrat":"teeratpitakrat",
"thomas dullmann" : "duelle",
"thomas düllmann" : "duelle",
"thomas f. duellmann" : "duelle",
"thomas f. dullmann" : "duelle",
"thomas f. düllmann" : "duelle",
"tom frotscher":"ShaggsOn",
"wilhelm" : "whasselbring",
"Wilhelm Hasselbring" : "whasselbring"
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


