import json
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from prov.identifier import QualifiedName, Namespace



LOOKUP_PATH = Path("data/name_lookup.json")
with LOOKUP_PATH.open("r", encoding="utf-8") as f:
    NAME_LOOKUP: dict[str, str] = json.load(f)


class ProvPubNameSpace(Enum):
    PARS = ("pars", "http://soton.ac.uk/pars#")
    PPUB = ("ppub", "http://soton.ac.uk/provpub#")
    ORCID = ("orcid", "https://orcid.org/")
    DOI = ("doi", "https://doi.org/")
    TIME = ("time", "http://www.w3.org/2006/time#")
    SCORO = ("scoro", "http://purl.org/spar/scoro/")
    PRO = ("pro", "http://purl.org/spar/pro/")
    FOAF = ("foaf", "http://xmlns.com/foaf/0.1/")
    PROV = ("prov", "http://www.w3.org/ns/prov#")
    FABIO = ("fabio", "http://purl.org/spar/fabio/")
    OWL = ("owl", "http://www.w3.org/2002/07/owl#")
    GITHUB2PROV = ("github2prov", "http://purl.org/github2prov/")
    KIEKER = ("kieker-monitoring_kieker", "https://github.com/kieker-monitoring/kieker/")
    COMMITS = ("commits_uri", "https://api.github.com/repos/kieker-monitoring/kieker/commits/")
    PULLS = ("pulls_uri", "https://github.com/kieker-monitoring/kieker/pull/")
    USERS = ("users", "https://github.com/")
    RDFS = ("rdfs", "http://www.w3.org/2000/01/rdf-schema#")
    XSD = ("xsd", "http://www.w3.org/2001/XMLSchema#")

    @property
    def prefix(self):
        return self.value[0]  # First item in the tuple

    @property
    def url(self):
        return self.value[1]

    @property
    def namespace(self)->Namespace:
        return Namespace(prefix=self.prefix, uri=self.url)

    @property
    def q_name(self)->QualifiedName:
        return QualifiedName(namespace=self.namespace,localpart=self.prefix)



class ghtp_types(Enum):
    COMMIT = QualifiedName(ProvPubNameSpace.GITHUB2PROV.namespace,"commit")


@dataclass(frozen=True)
class JiraComment:
    author_name: str
    created: str
    body: str
    id: str

    @property
    def author_github(self) -> str:
        return NAME_LOOKUP.get(self.author_name)


@dataclass(frozen=True)
class JiraIssue:
    id: str
    key: str
    created: str
    reporter: str
    comments: list[JiraComment]
    description:dict

    @property
    def github_reporter(self) -> str|None:
        return NAME_LOOKUP.get(self.reporter)
