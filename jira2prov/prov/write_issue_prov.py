import json
from pathlib import Path

from jira2prov.model.model import JiraComment, JiraIssue
from read_values import read_jsonl


def write_jira_prov():
    jira_id_map_path=Path("../../data/jira_to_gh_issues_map.json")
    jira_data_path=Path("../../data/jira_issues_dump/issues.jsonl")
    jira_gh_issues_map=None

    with jira_id_map_path.open("r") as in_file:
        jira_gh_issues_map=json.load(in_file)

    # for jira_id in jira_gh_issues_map.keys():
    for line in read_jsonl(jira_data_path):
        issue = JiraIssue.from_json(line)




def get_jira_comments(comments_data:list[dict])->list[JiraComment]:
    jira_comments=[]
    for comment in comments_data:
        jira_comment=JiraComment.from_json(comment)
        jira_comments.append(jira_comment)
    return jira_comments