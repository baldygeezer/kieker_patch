
from pathlib import Path

from prov.constants import PROV_ROLE
from prov.model import ProvDocument

from jira2prov.model.model import JiraComment, JiraIssue
from jira2prov.prov.provdoc import Jira2ProvNamespace, get_uuid5


jira_id_map_path=Path("../../data/jira_to_gh_issues_map.json")
jira_data_path=Path("../../data/jira_issues_dump/issues.jsonl")

def get_jira_comments(comments_data:list[dict])->list[JiraComment]:
    jira_comments=[]
    for comment in comments_data:
        jira_comment=JiraComment.from_json(comment)
        jira_comments.append(jira_comment)
    return jira_comments

def write_jira_prov(jira_issue:JiraIssue,prov_doc:ProvDocument):
    ###---Process the main issue---###
    github_user=jira_issue.github_reporter
    agent=prov_doc.agent(f"https://github.com/{github_user}")
    issue = prov_doc.entity(identifier=Jira2ProvNamespace.ISSUES.q_name(f"{jira_issue.key}"),
                            other_attributes={"prov:type": Jira2ProvNamespace.JIRA2PROV.q_name("issue")})
    issue.wasAttributedTo(agent)
    # link the issue to its github2prov equivalents
    for alt_issue in jira_issue.alternates:
        prov_doc.alternateOf(issue, alt_issue)

    ###---Process Events---###
    # There is always a creation, but this is not recorded in the jira history, so we do that before looping over the
    # events extracted from the jira API
    created_id=get_uuid5(jira_issue.id + "created" + str(jira_issue.created))
    created=prov_doc.activity(identifier=Jira2ProvNamespace.ISSUES.q_name(f"{jira_issue.key}/events/{created_id}"),
                              startTime=jira_issue.created,endTime=jira_issue.created,
                              other_attributes={"prov:type": Jira2ProvNamespace.JIRA2PROV.q_name("created")})
    asc = prov_doc.association(activity=created,
                               agent=agent,
                               other_attributes={PROV_ROLE: Jira2ProvNamespace.JIRA2PROV.q_name('actor')})
    created.wasAssociatedWith(agent)

    #store the previous event which generated the current version, which is the creation to start with, then update
    # these from the loop
    previous_event=created
    previous_event_start=jira_issue.created
    previous_version=None
    previous_version_double_event=None
    version_number=1 #start at version 1

    for jira_event in jira_issue.jira_history:
        event_attributes = {"prov:type": Jira2ProvNamespace.JIRA2PROV.q_name(jira_event.type)}

        if jira_event.type=="comment":
            jira_comment=jira_issue.comments.get(jira_event.id)
            mentions=len(jira_comment.mentions)
            refs=len(jira_comment.references)
            event_attributes["jira2prov:mentions"]=mentions
            event_attributes["jira2prov:refs"]=refs


        event_id = get_uuid5(jira_event.id + jira_event.type + str(jira_event.start))  # BUG!!!!!!!! if type is the same for simultanious events???
        event = prov_doc.activity(identifier=Jira2ProvNamespace.ISSUES.q_name(f"{jira_issue.key}/events/{event_id}"),
                                  startTime=jira_event.start, endTime=jira_event.end,
                                  # other_attributes={"prov:type": Jira2ProvNamespace.JIRA2PROV.q_name(jira_event.type)})
                                  other_attributes=event_attributes)

        agent = prov_doc.agent(f"https://github.com/{jira_event.github_agent}")
        asc = prov_doc.association(activity=event,
                                   agent=agent,
                                   other_attributes={PROV_ROLE: Jira2ProvNamespace.JIRA2PROV.q_name('actor')})
        event.wasAssociatedWith(agent)

        if jira_event.start == previous_event_start:
            this_version=previous_version
            previous_version=previous_version_double_event
            event.used(previous_version)
            previous_version=this_version
        else:
            this_version=prov_doc.entity(identifier=Jira2ProvNamespace.ISSUES.q_name(f"{jira_issue.key}#{version_number}"),
                                         other_attributes={"prov:type":Jira2ProvNamespace.JIRA2PROV.q_name("issue_version")})
            previous_version_double_event=previous_version
            if previous_version:  # there won't be if this is version 1
                event.used(previous_version)
            previous_version = this_version
            version_number += 1


        this_version.specializationOf(issue)
        this_version.wasGeneratedBy(event)
        # get ready for the next iteration - these must always be at the very end
        # if we have two simultaneous events they both create the bext version. if not, increment the version

        previous_event=event
        #OUTSIDE the if statement at the end of the loop iteration!!!!!
        previous_event_start=jira_event.start


    prov_doc.serialize("test.ttl", format='rdf', rdf_format='ttl')





    a=''




    "https://github.com/kieker-monitoring/kieker/issues/1000"