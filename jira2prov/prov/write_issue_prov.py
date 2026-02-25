
from pathlib import Path

from prov.model import ProvDocument

from jira2prov.model.model import JiraComment, JiraIssue
from jira2prov.prov.provdoc import Jira2ProvNamespace, get_uuid5


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

def write_jira_prov(jira_issue:JiraIssue,prov_doc:ProvDocument):
    github_user=jira_issue.github_reporter
    issue_id=jira_issue.key

    agent=prov_doc.agent(f"https://github.com/{github_user}")
    created_id=get_uuid5(jira_issue.id + str(jira_issue.created))
    created=prov_doc.activity(identifier=Jira2ProvNamespace.ISSUES.q_name(f"/events/{created_id}"),
                              startTime=jira_issue.created,endTime=jira_issue.created,
                              other_attributes={"prov:type": f"{Jira2ProvNamespace.JIRA2PROV.prefix}:created"})

    issue=prov_doc.entity(f"https://github.com/kieker-monitoring/kieker/issues/{issue_id}")
    issue.wasAttributedTo(agent)
    prov_doc.serialize("test.ttl", format='rdf', rdf_format='ttl')


    for alt_issue in jira_issue.alternates:
        prov_doc.alternateOf(issue,alt_issue)

    for event in jira_issue.jira_history:
        if event.type=="Created":
            a=''




    "https://github.com/kieker-monitoring/kieker/issues/1000"