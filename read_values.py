import json
import re
from pathlib import Path


def read_jsonl(path: str):
    """iterate a jsonl file and access each line as dict"""
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            yield json.loads(line)


def print_user_names(filepath):
   names = set()
   for line in read_jsonl(filepath):
       commit = line.get("commit")
       print(commit)
       if commit:
           a_name = commit.get("author",{}).get("name")
           if a_name:names.add(a_name)
           c_name = commit.get("committer",{}).get("name")
           if c_name:names.add(c_name)
   for n in names:
        print(n)

def print_keys(filepath):
    event_keys = set()
    for line in read_jsonl(filepath):
        for k in line.keys():
            event_keys.add(k)
    for k in event_keys:
        print(k)
    return event_keys

def get_merged_events():
    merged=[]
    for line in read_jsonl("data/timeline_events.jsonl"):
        if line.get("event") == "merged":
            merged.append(line)
    print(len(merged))
    return merged

def strip_field(filepath:str|Path, result_file:str|Path, field:str):
    lines = []
    with open(result_file, "w") as out_file:
        for line in read_jsonl(filepath):
            line.pop(field, None)
            lines.append(json.dumps(line, ensure_ascii=False) + "\n")
        out_file.writelines(lines)

def get_gh_jira_issues_map():
    mapping={}
    with open("data/jira_issues_map.json", "w") as out_file:
        for line in read_jsonl("data/kieker_issue_titles.jsonl"):
            issue_title  = line.get("title")
            match = re.search(r"\[(KIEKER-[^\[\]]+)\]", issue_title)
            if match:
                jira_id = match.group(1)
                issue_number = line.get("number")
                mapping[issue_number]=jira_id

        out_file.write(json.dumps(mapping, ensure_ascii=False))