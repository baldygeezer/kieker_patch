import json
from abc import ABC
from dataclasses import dataclass
from datetime import date
from enum import Enum
from pathlib import Path
from typing import Self

from prov.identifier import QualifiedName, Namespace

from jira2prov.model.collections import GithubHistoryDict, JiraHistoryEventDict
from jira2prov.loader import get_github_issue_history
from user_lookup import github_user_from_name

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

class Jira2ProvItem(ABC):
    @classmethod
    def from_json(cls, data: dict) -> Self:
        pass

@dataclass(frozen=True)
class JiraComment(Jira2ProvItem):
    author_name: str
    created: str
    body: str
    id: str
    references:list

    @property
    def author_github(self) -> str:
        return NAME_LOOKUP.get(self.author_name)

    @classmethod
    def from_json(self, data: dict) -> Self:
        pass


class Jira2Prov(Enum):
    """not in use, may never be"""
    ASSIGNED = "Assigned"
    CLOSED = "Closed"
    WORKFLOWCHANGE = "WorkflowChange"
    FIXVERSION = "fixVersion"
    COMMENT = "Comment"
    # link to a remote entity that isn't an issue - eg. meeting minutes item
    REMOTEISSUELINK= "RemoteIssueLink"
    # to another issue
    LINK ="Link"

    @property
    def prefix(self)->str:
        pass


@dataclass(frozen=True)
class JiraHistoryItem(Jira2ProvItem):
    id: str
    type: str
    _start: str
    _end: str
    agent:str

    @classmethod
    def from_json(cls, history_item: JiraHistoryEventDict) -> Self:
        type = history_item["field"] + history_item["to_string"]
        return cls(id=history_item["id"],
                   type=type,
                    _start=history_item["date"],
                    _end=history_item["date"],
                    agent=history_item["agent"])
    @property
    def github_agent(self)->str:
        return NAME_LOOKUP.get(self.agent)

    @property
    def start(self)->date:
        return date.fromisoformat(self._start)
    @property
    def end(self)->date:
        return date.fromisoformat(self._end)

@dataclass(frozen=True)
class JiraIssue(Jira2ProvItem):
    id: str
    key: str
    created: str
    reporter: str
    comments: list[JiraComment]
    description:dict
    changelog:list
    github_history:list[GithubHistoryDict]
    _jira_history:list[JiraHistoryItem]

    @property
    def github_reporter(self) -> str|None:
        return NAME_LOOKUP.get(self.reporter)

    # @property
    # def created(self)->str:
    #     return ''

    @classmethod
    def from_json(cls, data) -> Self:
        jira_id = None
        issue=None
        for k,v in data.items():
            issue=v["issue"]
        jira_key = issue["key"]
        jira_id =issue["id"]

        changelog=[JiraHistoryEventDict(id=item["id"],
                                        fields=item["items"],
                                        to_string=item['items']["to_string"],
                                        from_string=item['items']["from_string"],
                                        agent=item["author"]["displayName"],
                                        date=item['created']) for item in issue["changelog"]["histories"]]
        comments = [JiraComment.from_json(comment) for comment in issue["comments"]]
        reporter = github_user_from_name(issue["reporter"])
        created=issue["created"]
        gh_history=get_github_issue_history(jira_id=jira_id)

        return cls(id=jira_id,
                   key=jira_key,
                   comments = comments,
                   created=created,
                   reporter=github_user_from_name(reporter),
                   github_history=gh_history,
                  _jira_history=[JiraHistoryItem.from_json(item) for item in changelog],
                   description=issue["description"],
                   changelog=changelog
                   )




class IssueEvents(Enum):
    comment = "<http://purl.org/github2prov/comment>"
    assigned = "<http://purl.org/github2prov/assigned>"
    labeled = "<http://purl.org/github2prov/labeled>"
    closed = "<http://purl.org/github2prov/closed>"
    unassigned = "<http://purl.org/github2prov/unassigned>"
    connected = "<http://purl.org/github2prov/connected>"
    renamed = "<http://purl.org/github2prov/renamed>"
    reopened = "<http://purl.org/github2prov/reopened>"