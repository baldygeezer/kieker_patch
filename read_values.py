import json
from pathlib import Path
from typing import List, Dict, Any

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
        # if line.get("event") is not None and line.get("commit_id") != "null":
        #     print(line["commit_id"])
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