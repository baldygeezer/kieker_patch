import uuid

import prov.model as model
from prov.model import ProvDocument

from jira2prov.prov.provdoc import get_provdoc, Jira2ProvNamespace
from read_values import read_jsonl
from user_lookup import mint_user_uri


def run_patch(input_json_file, output_rdf_file):
    provdoc = get_provdoc()
    for commit in read_jsonl(input_json_file):
        write_agent(commit=commit, type="author", provdoc=provdoc)
        write_agent(commit=commit, type="committer", provdoc=provdoc)
    # provdoc.serialize(output_rdf_file, format='rdf', rdf_format='ttl')
    provdoc.serialize(output_rdf_file, format='rdf',rdf_format="ttl")

def write_agent(commit: dict, type: str, provdoc: ProvDocument):
    agent = commit.get("commit", {}).get(type)
    commit_id = commit.get("url")
    if agent:
        agent_name = agent.get("name")
        # github_id = lookup.get(agent_name)
        # if not github_id:
        #     print(f"warning: unable to look up author {agent_name}")
        #     return
        # if github_id.startswith("mailto:"):
        #     agent = mint_non_github_agent(user_value=github_id,
        #                                   provdoc=provdoc,
        #                                   name=agent_name)

        # try and look up a github user id and make a github user uri

        agent = mint_agent(agent_name, provdoc)

        activity = provdoc.activity(commit_id)
        activity.wasAssociatedWith(agent)
        provdoc.association(activity=activity,
                            agent=agent,
                            other_attributes={model.PROV_ROLE: type})


def mint_non_github_agent_uuid5(user_value: str, provdoc: ProvDocument, name: str) -> model.ProvAgent:
    ns = uuid.uuid5(uuid.NAMESPACE_URL, Jira2ProvNamespace.PARS.url)
    user_hash = uuid.uuid5(ns, user_value)
    url = f"{Jira2ProvNamespace.PARS.url}{user_hash}"
    return provdoc.agent(url, other_attributes={"foaf:name": name})


def mint_agent(users_real_name: str, provdoc: ProvDocument, github_id: str | None = None) -> model.ProvAgent:
    uri = mint_user_uri(users_real_name)
    return provdoc.agent(uri, other_attributes={"foaf:name": users_real_name})
