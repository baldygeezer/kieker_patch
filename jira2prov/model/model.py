import datetime
import json
from abc import ABC
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Self

from prov.identifier import QualifiedName

from jira2prov.model.collections import GithubHistoryDict, JiraHistoryEventDict
from jira2prov.loader import get_github_issue_history
from jira2prov.prov.provdoc import ProvPubNameSpace
from read_values import process_content_block
from user_lookup import github_user_from_name

LOOKUP_PATH = Path("data/name_lookup.json")
with LOOKUP_PATH.open("r", encoding="utf-8") as f:
    NAME_LOOKUP: dict[str, str] = json.load(f)


class ghtp_types(Enum):
    COMMIT = QualifiedName(ProvPubNameSpace.GITHUB2PROV.namespace, "commit")

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
    mentions:list

    @property
    def author_github(self) -> str:
        return NAME_LOOKUP.get(self.author_name)

    @classmethod
    def from_json(cls, data: dict) -> Self:
        body, issue_refs, user_refs=process_content_block(data["body"]["content"])
        return cls(author_name=data["author_name"],
                   created=data["created"],
                   body=body,
                   id=data["id"],
                   references=issue_refs,
                   mentions=user_refs)





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
    def start(self)->datetime:
        return datetime.strptime(self._start, "%Y-%m-%dT%H:%M:%S.%f%z")

    @property
    def end(self)->datetime:
        return datetime.strptime(self._end, "%Y-%m-%dT%H:%M:%S.%f%z")

@dataclass(frozen=True)
class JiraIssue(Jira2ProvItem):
    id: str
    key: str
    created: str
    reporter: str
    comments: list[JiraComment]
    description:dict
    github_history:list[GithubHistoryDict]
    jira_history:list[JiraHistoryItem]

    @property
    def github_reporter(self) -> str|None:
        return NAME_LOOKUP.get(self.reporter)

    @classmethod
    def _process_changelog_items(cls, issue: dict):
        histories = issue["changelog"]["histories"]
        for history in histories:
            for item in history["items"]:
                event=JiraHistoryEventDict(id=history["id"],
                                            field=item["field"],
                                            to_string=item["toString"],
                                            from_string=item["fromString"],
                                            agent=history["author"]["displayName"],
                                            date=history['created'])
                yield JiraHistoryItem.from_json(event)

    @classmethod
    def from_json(cls, data) -> Self:
        jira_id = None
        issue=None
        comments=[]
        for k,v in data.items():
            issue=v["issue"]
            comments=v["comments"]
        jira_key = issue["key"]
        jira_id =issue["id"]
        jira_history = [log for log in cls._process_changelog_items(issue)]
        # changelog=[JiraHistoryEventDict(id=item["id"],
        #                                 fields=item["items"],
        #                                 to_string=item['items']["to_string"],
        #                                 from_string=item['items']["from_string"],
        #                                 agent=item["author"]["displayName"],
        #                                 date=item['created']) for item in issue["changelog"]["histories"]]

        comments = [JiraComment.from_json(comment) for comment in comments]
        reporter = github_user_from_name(issue["reporter"])
        created=issue["created"]
        gh_history=get_github_issue_history(jira_id=jira_key)

        return cls(id=jira_id,
                   key=jira_key,
                   comments = comments,
                   created=created,
                   reporter=github_user_from_name(reporter),
                   github_history=gh_history,
                   description=issue["description"],
                   jira_history=jira_history
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