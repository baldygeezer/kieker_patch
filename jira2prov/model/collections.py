from typing import TypedDict


class GithubEventDict(TypedDict):
    event:str
    event_type:str


class GithubHistoryDict(TypedDict):
    github_id:str
    issue_iri: str
    events:list[GithubEventDict]


class JiraHistoryEventDict(TypedDict):
    id:str
    field: str
    from_string: str
    to_string: str
    date: str
    agent: str

class JiraIssueDescriptionDict(TypedDict):
    body: str
    refs: list[str]
    mentions: list[str]

