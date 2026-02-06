import prov.model as model
from prov.identifier import Namespace
import uuid
from model import ProvPubNameSpace, ghtp_types
from user_lookup import lookup
from read_values import read_jsonl
from prov.model import ProvDocument


def get_provdoc()-> ProvDocument:
    document = ProvDocument()
    for ns_val in ProvPubNameSpace:
        ns = Namespace(prefix=ns_val.prefix, uri=ns_val.url)
        document.add_namespace(ns)
    return document


def run_patch(filename):
    provdoc = get_provdoc()
    for commit in read_jsonl(filename):
        write_agent(commit=commit,type="author", provdoc=provdoc)
        write_agent(commit=commit,type="committer", provdoc=provdoc)
    provdoc.serialize("out.ttl", format='rdf', rdf_format='ttl')


def write_agent(commit:dict, type:str, provdoc:ProvDocument):
    agent = commit.get("commit",{}).get(type)
    commit_id = commit.get("url")
    if agent:
        agent_name = agent.get("name")
        github_id = lookup.get(agent_name)
        if not github_id:
            print(f"warning: unable to look up author {agent_name}")
            return
        if github_id.startswith("mailto:"):
            agent=mint_non_github_agent(user_value=github_id,
                                        provdoc=provdoc,
                                        name=agent_name)
        else:
            agent = provdoc.agent(f"users:{github_id}")
        activity = provdoc.activity(commit_id)

        activity.wasAssociatedWith(agent)
        provdoc.association(activity=activity,
                            agent=agent,
                            other_attributes={model.PROV_ROLE: type})

def mint_non_github_agent(user_value:str, provdoc:ProvDocument,name:str)-> model.ProvAgent:
    ns = uuid.uuid5(uuid.NAMESPACE_URL,ProvPubNameSpace.PARS.url)
    user_hash = uuid.uuid5(ns, user_value)
    url=f"{ProvPubNameSpace.PARS.url}{id}"
    return provdoc.agent(url,other_attributes={"foaf:name": name})


