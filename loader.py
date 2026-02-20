import json
from pathlib import Path

from model import JiraIssue, GithubHistoryDict
from sparql_client import KiekerClient


def get_github_issue_history(github_issue_id=None, jira_id=None)->list[GithubHistoryDict]:
    """Retrieve the history of an issue from a github2prov model. if the id of a jira issue is provided, this will be
    used to retrieve the equivalent github3prov issue's history. Some jira issues can map to multiple duplicate github
    issues. The return value of this function is a list and where there are github duplicates this will have multiple
    values"""


    results:list[GithubHistoryDict] = []
    jira_gh_issues_map=None
    issues_map_path=Path("data/jira_to_gh_issues_map.json")
    with issues_map_path.open("r") as in_file:
        jira_gh_issues_map=json.load(in_file)

    if github_issue_id:
        gh_issue_ids = [github_issue_id]

    elif jira_id:
        gh_issue_ids = jira_gh_issues_map[jira_id]
    else:
        raise ValueError("at least one of github_issue_id or jira_id must be provided")

    kieker=KiekerClient()
    for id in gh_issue_ids:
        events=kieker.get_github_issue_events(id)
        results.append(events)

    return results

def get_issue(jira_id):
    github_history=get_github_issue_history(jira_id=jira_id)
    jira_issue=JiraIssue.from_json(github_history)
    return jira_issue
