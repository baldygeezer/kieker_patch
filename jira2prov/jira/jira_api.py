import json
from dataclasses import dataclass, field
from pathlib import Path

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

data_dump = Path(__file__).parent / "data/jira_issues_dump/issues.jsonl"
input_list = Path(__file__).parent / "data/issues_list.txt"


@dataclass
class JiraClient:
    base_url: str
    _session: requests.Session = field(init=False, repr=False)

    def __post_init__(self):
        sesh = requests.Session()
        retries = Retry(
            total=5,
            backoff_factor=0.5,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"],
            raise_on_status=False,
        )
        sesh.mount("https://", HTTPAdapter(max_retries=retries, pool_connections=5, pool_maxsize=5))
        sesh.headers.update({"Accept": "application/json"})
        self._session = sesh

    @property
    def session(self) -> requests.Session:
        return self._session

    def _get_base_issue(self, issue_url: str) -> dict:
        # url=f"{self.base_url}/rest/api/3/issue/{key}"
        params = {"fields": "created,reporter,description,changelog",
                  "expand": "changelog"}
        response = self.session.get(issue_url, params=params, timeout=30)
        response.raise_for_status()
        json = response.json()
        fields = json["fields"]
        return {
            "id": json.get("id"),
            "key": json.get("key"),
            "created": fields.get("created"),
            "reporter": fields.get("reporter", {}).get("displayName"),
            "description": fields.get("description", {}),
            "changelog": json.get("changelog", {})
        }

    def get_issue_comments(self, issue_url: str, page_size=2) -> list[dict]:
        comments_url = issue_url + "/comment"
        page_start = 0
        results = []
        while True:
            params = {"startAt": page_start, "maxResults": page_size, "orderBy": "created"}
            response = self.session.get(comments_url, params=params, timeout=30)
            response.raise_for_status()
            json = response.json()
            comments = json["comments"]
            if not comments:
                break
            total = json.get("total")  # the total number of comments on the issue
            max_results = (json["maxResults"] or page_size)

            for comment in comments:
                # result = JiraComment(author_name=comment["author"]["displayName"],
                #                      created=comment["created"],
                #                      body=comment.get("body", ""),
                #                      id=comment["id"])
                results.append(
                    {"author_name": comment["author"]["displayName"],
                     "created": comment["created"],
                     "body": comment["body"],
                     "id": comment["id"]}
                )
                # results.append(result)

            page_start = (json["startAt"] or page_start) + max_results

            # stop if we got less than a full page
            if len(comments) < max_results:
                break
            else:
                # ...or stop if our page start is more than the number of comments the issue has
                if total is not None and page_start >= int(total):
                    break

        return results

    def get_jira_issue(self, jira_id: str) -> dict:
        issue_url = f"{self.base_url}/rest/api/3/issue/{jira_id}"
        base_issue = self._get_base_issue(issue_url)
        base_issue_comments = self.get_issue_comments(issue_url)
        return {"issue": base_issue, "comments": base_issue_comments}

    def dump_jira_data(self, jira_issue_id: str) -> dict:
        with data_dump.open("a") as dump:
            issue_dict = self.get_jira_issue(jira_issue_id)
            json.dump({jira_issue_id: issue_dict}, dump)
            dump.write("\n")

    def get_jira_issue_data(self) -> dict:
        pass
