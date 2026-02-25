import datetime
import json
from abc import ABC
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Self

from prov.identifier import QualifiedName

from jira2prov.loader import get_github_issue_history
from jira2prov.model.collections import GithubHistoryDict, JiraHistoryEventDict
from jira2prov.prov.provdoc import Jira2ProvNamespace
from read_values import process_content_block
from user_lookup import github_user_from_name

LOOKUP_PATH = Path("data/name_lookup.json")
DATE_FORMAT = "%Y-%m-%dT%H:%M:%S.%f%z"
with LOOKUP_PATH.open("r", encoding="utf-8") as f:
    NAME_LOOKUP: dict[str, str] = json.load(f)


class ghtp_types(Enum):
    COMMIT = QualifiedName(Jira2ProvNamespace.GITHUB2PROV.namespace, "commit")


class Jira2ProvItem(ABC):
    @classmethod
    def from_json(cls, data: dict) -> Self:
        pass


@dataclass(frozen=True)
class JiraComment(Jira2ProvItem):
    author_name: str
    created: datetime
    body: str
    id: str
    references: list
    mentions: list

    @property
    def author_github(self) -> str:
        return NAME_LOOKUP.get(self.author_name)

    @classmethod
    def from_json(cls, data: dict) -> Self:
        body, issue_refs, user_refs = process_content_block(data["body"]["content"])
        created = datetime.strptime(data["created"], DATE_FORMAT)
        return cls(author_name=data["author_name"],
                   created=created,
                   body=body,
                   id=data["id"],
                   references=issue_refs,
                   mentions=user_refs)


def _item_type(field: str, to_string) -> str:
    item_type = ""
    if field in ["status", "resolution"]:
        item_type = field + to_string
    else:
        item_type = field
    return item_type.replace(" ", "")


class Jira2Prov(Enum):
    """not in use, may never be"""
    ASSIGNED = "Assigned"
    CLOSED = "Closed"
    WORKFLOWCHANGE = "WorkflowChange"
    FIXVERSION = "fixVersion"
    COMMENT = "Comment"
    # link to a remote entity that isn't an issue - eg. meeting minutes item
    REMOTEISSUELINK = "RemoteIssueLink"
    # to another issue
    LINK = "Link"

    @property
    def prefix(self) -> str:
        pass


@dataclass(frozen=True)
class JiraHistoryItem(Jira2ProvItem):
    id: str
    type: str
    start: datetime
    end: datetime
    agent: str

    @classmethod
    def from_json(cls, history_item: JiraHistoryEventDict) -> Self:
        start = datetime.strptime(history_item["date"], DATE_FORMAT)
        end = datetime.strptime(history_item["date"], DATE_FORMAT)
        return cls(id=history_item["id"],
                   type=_item_type(field=history_item["field"], to_string=history_item["to_string"]),
                   start=start,
                   end=end,
                   agent=history_item["agent"])

    @property
    def github_agent(self) -> str:
        return NAME_LOOKUP.get(self.agent)


@dataclass()
class JiraIssue(Jira2ProvItem):
    """the data for a Jira issue. This may map to more than one github issue.
    :param id: the internal jira id
    :type id: str
    :param key: the id used in the issue url
    :type key: str
    :param created: the date string from the json data
    :type created: str
    :param reporter: github url of the reporter, the agent this issue will be attributed to
    :type reporter: str
    :param comments: a list of the comments mande on the issue
    :type comments: list[JiraComment]
    :param description: the description of the issue
    :type description: str
    :param github_history: a dict containing the history of the alternate issue/s on githhub. There can be duplicates of
     the github issues, so this is a dict keyed with github issue ids
     :type github_history: dict[str,list[dict]]
     :param jira_history: a list of events in the jira issue history
     :type jira_history:list[JiraHistoryItem]
     :param alternates: a list of the alternate issues on github. most of the time there will only be one, but there
     are sometimes duplicates
     :type alternates: list[str]
    """
    id: str
    key: str
    created: datetime
    reporter: str
    # comments: list[JiraComment]
    comments: dict[str, JiraComment]
    description: dict
    github_history: dict[str, GithubHistoryDict]
    jira_history: list[JiraHistoryItem]
    alternates: list[str]

    def __post_init__(self) -> None:
        for ident, comment in self.comments.items():
            comment_event = JiraHistoryItem(id=ident,
                                            type="comment",
                                            start=comment.created,
                                            end=comment.created,
                                            agent=comment.author_name)
            self.jira_history.append(comment_event)
        print(len(self.jira_history))
        self.jira_history.sort(key=lambda x: x.start)

    @property
    def github_reporter(self) -> str | None:
        return NAME_LOOKUP.get(self.reporter)

    @classmethod
    def _process_changelog_items(cls, issue: dict):
        histories = issue["changelog"]["histories"]
        for history in histories:
            for item in history["items"]:
                event = JiraHistoryEventDict(id=history["id"],
                                             field=item["field"],
                                             to_string=item["toString"],
                                             from_string=item["fromString"],
                                             agent=history["author"]["displayName"],
                                             date=history['created'])
                yield JiraHistoryItem.from_json(event)

    @classmethod
    def from_json(cls, data) -> Self:
        # jira_id = None
        issue = None
        comments = []
        for k, v in data.items():
            issue = v["issue"]
            comments = v["comments"]
        jira_key = issue["key"]
        jira_id = issue["id"]
        jira_history = [log for log in cls._process_changelog_items(issue)]
        comments_list = [JiraComment.from_json(comment) for comment in comments]
        comments = {comment.id: comment for comment in comments_list}
        reporter = github_user_from_name(issue["reporter"])
        created = issue["created"]
        gh_history = get_github_issue_history(jira_id=jira_key)
        alternates = []
        for gh_issue in gh_history.keys():
            alternates.append(f"https://github.com/kieker-monitoring/kieker/issues/{gh_issue}")

        return cls(id=jira_id,
                   key=jira_key,
                   comments=comments,
                   created=created,
                   reporter=reporter,
                   github_history=gh_history,
                   description=issue["description"],
                   jira_history=jira_history,
                   alternates=alternates
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
