from enum import Enum

from SPARQLWrapper import SPARQLWrapper, JSON


class KiekerQuery(Enum):
    ISSUE_EVENTS = """
    PREFIX prov: <http://www.w3.org/ns/prov#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    PREFIX github2prov: <http://purl.org/github2prov/>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    
    select  ?event ?event_type WHERE {{
        values ?issue{{<{issue}>}}
    
        ?issue a github2prov:issue. 
        
        {{   #the creation event
            ?issue prov:wasGeneratedBy ?event.
        }}
        UNION
        {{	# versioning events
            ?issue_version prov:specializationOf ?issue.
            ?issue_version prov:wasGeneratedBy ?event.
        }}
   
        ?event a ?event_type .
        FILTER NOT EXISTS {{?issue a github2prov:pull.}}
        FILTER (?event_type != prov:Activity)
    }}
    
    """

    def query(self, **params) -> str:
        return self.value.format(**params)


class KiekerClient:
    def __init__(self):
        self.kieker_client = SPARQLWrapper("http://localhost:7200/repositories/kieker")
        self.keiker_ii_client = SPARQLWrapper("http://localhost:7200/repositories/Kieker_ii")

    def _run(self, query_string: str, result_format=JSON) -> bytes | str | dict:
        client = self.keiker_ii_client
        client.setQuery(query_string)
        client.setReturnFormat(result_format)
        return client.query().convert()

    def get_github_issue_events(self, github_issue_id) -> dict:
        issue_iri=f"https://github.com/kieker-monitoring/kieker/issues/{github_issue_id}"
        query = KiekerQuery.ISSUE_EVENTS
        result_set = self._run(query.query(issue=issue_iri))
        events = []
        for item in result_set['results']['bindings']:
            event = item['event']['value']
            event_type = item['event_type']['value']
            events.append({"event":event, "event_type":event_type})
        return {"github_id": github_issue_id,
                "iri":issue_iri,
                "events":events
                }
