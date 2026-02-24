import json
from pathlib import Path

from jira2prov.model.collections import GithubHistoryDict
from jira2prov.db.sparql_client import KiekerClient


def get_github_issue_history(jira_id)->dict[str, GithubHistoryDict]:
    """Retrieve the history of an issue from a github2prov model using id of a jira issue. Some jira issues can map to
    multiple duplicate github issues. The return value of this function is a dict. where there are github duplicates
    this will have multiple keys"""

    results: dict[str, GithubHistoryDict]  = {}
    issues_map_path=Path("data/jira_to_gh_issues_map.json")
    kieker = KiekerClient()
    with issues_map_path.open("r") as in_file:
        jira_gh_issues_map=json.load(in_file)
        gh_issue_ids = jira_gh_issues_map[jira_id]
        for github_id in gh_issue_ids:
            events=kieker.get_github_issue_events(github_id)
            results[github_id]=events

    return results

def get_issue(issue_data):
    jira_id=issue_data["key"]
    github_history=get_github_issue_history(jira_id=jira_id)

    # # jira_issue=JiraIssue.from_json()
    # return jira_issue
