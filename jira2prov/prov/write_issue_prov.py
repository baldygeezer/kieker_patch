
from pathlib import Path

from prov.constants import PROV_ROLE
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
    created_id=get_uuid5(jira_issue.id + "created" + str(jira_issue.created))
    created=prov_doc.activity(identifier=Jira2ProvNamespace.ISSUES.q_name(f"{jira_issue.key}/events/{created_id}"),
                              startTime=jira_issue.created,endTime=jira_issue.created,
                              other_attributes={"prov:type": Jira2ProvNamespace.JIRA2PROV.q_name("created")})
    asc = prov_doc.association(activity=created,
                               agent=agent,
                               other_attributes={PROV_ROLE: Jira2ProvNamespace.JIRA2PROV.q_name('actor')})
    created.wasAssociatedWith(agent)
    issue = prov_doc.entity(identifier=Jira2ProvNamespace.ISSUES.q_name(f"{jira_issue.key}"))
    issue.wasAttributedTo(agent)
    for alt_issue in jira_issue.alternates:
        prov_doc.alternateOf(issue,alt_issue)

    previous_event=created
    previous_event_start=jira_issue.created
    previous_event_version=None
    version_number=1
    for jira_event in jira_issue.jira_history:
        event_id=get_uuid5(jira_event.id + jira_event.type + str(jira_event.start)) #BUG!!!!!!!! if type is the same for simultanious events???
        event=prov_doc.activity(identifier=Jira2ProvNamespace.ISSUES.q_name(f"{jira_issue.key}/events/{event_id}"),
                                startTime=jira_event.start,endTime=jira_event.end,
                                other_attributes={"prov:type": Jira2ProvNamespace.JIRA2PROV.q_name(jira_event.type)})

        if previous_event_version:
            event.used(previous_event_version)

        agent=prov_doc.agent(f"https://github.com/{jira_event.github_agent}")
        asc=prov_doc.association(activity=event,
                                 agent=agent,
                                 other_attributes={PROV_ROLE:Jira2ProvNamespace.JIRA2PROV.q_name('actor')})
        event.wasAssociatedWith(agent)
        this_version=prov_doc.entity(identifier=Jira2ProvNamespace.ISSUES.q_name(f"{jira_issue.key}#{version_number}"),
                                     other_attributes={})
        this_version.wasGeneratedBy(previous_event)
        this_version.specializationOf(issue)

        # get ready for the next iteration - these must always be at the very end
        # if we have two simultaneous events they both create the bext version. if not, increment the version
        if jira_event.start != previous_event_start:
            version_number+=1
            previous_event_version = this_version

            previous_event=event
        previous_event_start=jira_event.start


    prov_doc.serialize("test.ttl", format='rdf', rdf_format='ttl')





    a=''




    "https://github.com/kieker-monitoring/kieker/issues/1000"