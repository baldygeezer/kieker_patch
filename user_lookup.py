from pathlib import Path

MISSING_NAMES_LOG = Path("missing_github_names.txt")

lookup_cased={
"christian" : "czirkelbach",
"ChristianWulf" : "ChristianWulf",
"Nils Ehmke": "nils-christian",
"Nina Marwede" : "svn:nina",
"nie" : "nils-christian",
"Jürgen Walter" : "juergen-walter",
"Holger Knoche" : "holgerknoche",
"duellmtk@studi.informatik.uni-stuttgart.de" : "duelle",
"Wilhelm" : "whasselbring",
"Andre van Hoorn": "avanhoorn",
"Christian Zirkelbach": "czirkelbach",
"Clemens Kurz": "cbkurz",
"Marc Adolf" : "madcau",
"Florian Fittkau" : "FFittkau",
"Thomas F. Duellmann" : "duelle",
"Danish Manzoor" : "danishmanzoor",
"Dennis Kieselhorst" : "deki",
"Thomas F. Düllmann" : "duelle",
"Pascale Brandt" : "mailto:pbr@informatik.uni-kiel.de",
"Bjoern Weissenfels" : "mailto:bjw@informatik.uni-kiel.de",
"Nils Christian Ehmke" : "nils-christian",
"Thomas Düllmann" : "duelle",
"Micky Singh Multani" : "mailto:msm@informatik.uni-kiel.de",
"Matthias Rohr" : "mailto:rohrrohr@googlemail.com",
"André van Hoorn" : "avanhoorn",
"GitHub" : "github",
"Tillmann Bielefeld" : "mailto:email@tielefeld.com",
"Christian Wulf" : "ChristianWulf",
"Henry Grow" : "mailto:hgr@informatik.uni-kiel.de",
"Imran Asad Gul" : "mailto:iag@informatik.uni-kiel.de",
"Reiner Jung":"rju"
}

lookup={
"david georg reichelt": "DaGeRe",
"andre van hoorn" : "avanhoorn",
"andré van hoorn" : "avanhoorn",
"bjoern weissenfels" : "mailto:bjw@informatik.uni-kiel.de",
"christian wulf" : "ChristianWulf",
"christian zirkelbach": "czirkelbach",
"christian" : "czirkelbach",
"christianwulf" : "ChristianWulf",
"clemens kurz": "cbkurz",
"danish manzoor" : "danishmanzoor",
"dennis kieselhorst" : "deki",
"duellmtk@studi.informatik.uni-stuttgart.de" : "duelle",
"florian fittkau" : "FFittkau",
"github" : "github",
"henry grow" : "mailto:hgr@informatik.uni-kiel.de",
"holger knoche" : "holgerknoche",
"imran asad gul" : "mailto:iag@informatik.uni-kiel.de",
"jürgen walter" : "juergen-walter",
"marc adolf" : "madcau",
"matthias rohr" : "mailto:rohrrohr@googlemail.com",
"micky singh multani" : "mailto:msm@informatik.uni-kiel.de",
"nie" : "nils-christian",
"nils christian ehmke" : "nils-christian",
"nils ehmke": "nils-christian",
"nina marwede" : "svn:nina",
"pascale brandt" : "mailto:pbr@informatik.uni-kiel.de",
"reiner jung":"rju",
"thomas düllmann" : "duelle",
"thomas f. duellmann" : "duelle",
"thomas f. düllmann" : "duelle",
"tillmann bielefeld" : "mailto:email@tielefeld.com",
"wilhelm" : "whasselbring"
}

def github_user_from_name(real_name: str) -> str|None:
    normalised_name=real_name.strip().lower()
    github_user = lookup.get(normalised_name)
    if github_user is not None:
        return f"https://github.com/{github_user}"
    _log_name_not_found(github_user=github_user,real_name=real_name)
    print(f"WARNING: github user for {real_name} not found in lookup. Check the log")
    return f"https://github.com/{normalised_name.strip(" ")}"

def _log_name_not_found(github_user: str|None, real_name: str) -> None:
    if not github_user:
        with MISSING_NAMES_LOG.open("a") as log:
            log.write(real_name+"\n")


