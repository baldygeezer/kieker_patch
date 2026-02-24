import json
from pathlib import Path

from prov.model import ProvDocument

from jira2prov.model.model import JiraComment, JiraIssue
from read_values import read_jsonl
from user_lookup import github_user_from_name

jira_id_map_path=Path("../../data/jira_to_gh_issues_map.json")
jira_data_path=Path("../../data/jira_issues_dump/issues.jsonl")


# def write_jira_prov():
#
#
#     with jira_id_map_path.open("r") as in_file:
#         jira_gh_issues_map=json.load(in_file)
#
#     # for jira_id in jira_gh_issues_map.keys():
#     for line in read_jsonl(jira_data_path):
#         issue = JiraIssue.from_json(line)




def get_jira_comments(comments_data:list[dict])->list[JiraComment]:
    jira_comments=[]
    for comment in comments_data:
        jira_comment=JiraComment.from_json(comment)
        jira_comments.append(jira_comment)
    return jira_comments

def write_jira_prov(issue:JiraIssue,prov_doc:ProvDocument):
    github_user=github_user_from_name(issue.reporter)
    issue_id=issue.key

    agent=prov_doc.agent(f"https://github.com/{github_user}")
    issue=prov_doc.entity(f"https://github.com/kieker-monitoring/kieker/issues/{issue_id}")
    issue.wasAttributedTo(agent)

    "https://github.com/kieker-monitoring/kieker/issues/1000"