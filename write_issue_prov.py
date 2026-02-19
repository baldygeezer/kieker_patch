import json
from pathlib import Path

from model import JiraComment, JiraIssue
from read_values import read_jsonl
from sparql_client import KiekerClient, KiekerQuery


def get_github_issue_history(github_issue_id=None, jira_id=None)->list[dict]:
    """Retrieve the history of an issue from a github2prov model. if the id of a jira issue is provided, this will be
    used to retrieve the equivalent github3prov issue's history. Some jira issues can map to multiple duplicate github
    issues. The return value of this function is a list and where there are github duplicates this will have multiple
    values"""

    gh_issue_ids=[]
    results = []
    jira_gh_issues_map=None
    issues_map_path=Path("data/jira_to_gh_issues_map.json")
    with issues_map_path.open("r") as in_file:
        jira_gh_issues_map=json.load(in_file)

    if github_issue_id:
        gh_issue_ids = [github_issue_id]
        jira_id = None
    elif jira_id:
        gh_issue_ids = jira_gh_issues_map[jira_id]
    else:
        raise ValueError("at least one of github_issue_id or jira_id must be provided")

    kieker=KiekerClient()
    for id in gh_issue_ids:
        events=kieker.get_github_issue_events(id)
        results.append(events)

    return results

def write_jira_prov():
    jira_id_map_path=Path("data/jira_to_gh_issues_map.json")
    jira_data_path=Path("data/jira_issues_dump/issues.jsonl")
    jira_gh_issues_map=None

    with jira_id_map_path.open("r") as in_file:
        jira_gh_issues_map=json.load(in_file)

    # for jira_id in jira_gh_issues_map.keys():
    for line in read_jsonl(jira_data_path):
        issue = JiraIssue.from_json(line)




def get_jira_comments(comments_data:list[dict])->list[JiraComment]:
    jira_comments=[]
    for comment in comments_data:
        jira_comment=JiraComment(comment)
        jira_comments.append(jira_comment)