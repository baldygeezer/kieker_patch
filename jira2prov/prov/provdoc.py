import uuid
from enum import Enum

from prov.model import ProvDocument
from prov.identifier import Namespace, QualifiedName


def get_provdoc()-> ProvDocument:
    document = ProvDocument()
    for ns_val in ProvPubNameSpace:
        ns = Namespace(prefix=ns_val.prefix, uri=ns_val.url)
        document.add_namespace(ns)
    return document


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


def get_uuid5(value: str) -> str:
    ns = uuid.uuid5(uuid.NAMESPACE_URL, ProvPubNameSpace.PARS.url)
    return str(uuid.uuid5(ns, value))
