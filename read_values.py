import json
import re
from collections import defaultdict
from pathlib import Path


def read_jsonl(path: str | Path):
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
            a_name = commit.get("author", {}).get("name")
            if a_name: names.add(a_name)
            c_name = commit.get("committer", {}).get("name")
            if c_name: names.add(c_name)
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
    merged = []
    for line in read_jsonl("data/timeline_events.jsonl"):
        if line.get("event") == "merged":
            merged.append(line)
    print(len(merged))
    return merged


def strip_field(filepath: str | Path, result_file: str | Path, field: str):
    lines = []
    with open(result_file, "w") as out_file:
        for line in read_jsonl(filepath):
            line.pop(field, None)
            lines.append(json.dumps(line, ensure_ascii=False) + "\n")
        out_file.writelines(lines)


def get_gh_jira_issues_map():
    mapping = {}
    with open("data/gh_to_jira_issues_map.json", "w") as out_file:
        for line in read_jsonl("data/kieker_issue_titles.jsonl"):
            issue_title = line.get("title")
            match = re.search(r"\[(KIEKER-[^\[\]]+)\]", issue_title)
            if match:
                jira_id = match.group(1)
                issue_number = line.get("number")
                mapping[issue_number] = jira_id

        out_file.write(json.dumps(mapping, ensure_ascii=False))


def get_gh_duplicate_issues():
    issues_map_path = Path("data/gh_to_jira_issues_map.json")
    mapped_issues = {}
    with issues_map_path.open("r") as in_file:
        mapped_issues = json.load(in_file)

    value_to_keys = defaultdict(list)
    for k, v in mapped_issues.items():
        value_to_keys[v].append(k)

    non_unique = {v: ks for v, ks in value_to_keys.items() if len(ks) > 1}

    # show counts, sorted
    for v, ks in sorted(non_unique.items(), key=lambda item: len(item[1]), reverse=True)[:30]:
        print(v, ks[:10])


def flip_map(orig: dict):
    flippy: dict[str, list[str]] = defaultdict(list)
    for k, v in orig.items():
        flippy[v].append(k)
    flipped = dict(flippy)

    with open("data/jira_to_gh_issues_map.json", "w") as out_file:
        out_file.write(json.dumps(flipped, ensure_ascii=False))

    return flipped


def process_content(content: dict) -> dict:
    issue_refs: list[str] = []
    user_mentions: list[str] = []
    body = """"""
    for item in content:
        if item["type"] == "paragraph":
            text,i_refs,usr_mentions = _process_paragraph(item)
            issue_refs.extend(i_refs)
            user_mentions.extend(usr_mentions)
            body.join(text)
        elif item["type"] == "bulletList":
                item_text = item['attrs'].get("text")

    return {
        "body": body,
        "issue_references": issue_refs
        "user_mentions": user_mentions
    }


def _process_paragraph(para: dict) -> tuple[str, list[str], list[str]]:
    issue_refs: list[str] = []
    user_mentions:list[str] = []
    parts = []
    text = """"""
    for item in para['content']:
        if item["type"] == "paragraph":
            txt,i_refs,u_mentions = _process_paragraph(item)
            issue_refs.extend(i_refs)
            user_mentions.extend(u_mentions)
            parts.append(txt)
        if item["type"] == "inlineCard":
            item_url = item['attrs'].get("url")
            if item_url:
                issue_refs.append(item_url)
                parts.append(item_url)
            else:
                print(f"Warning: inlineCard item has no 'url' field: {item}")
        if item["type"] == "mention":
            item_text = item['attrs'].get("text")
            if item_text:
                user_mentions.append(item_text)
                parts.append(item_text)
            else:
                print(f"Warning: mention item has no 'text' field: {item}")

        if item["type"] == "text":
            txt = item.get("text") or "\n"
            parts.append(txt)


    parts.append("\n")

    return text.join(parts), issue_refs , user_mentions


def process_bullet_list(bullet_list: dict) -> tuple[str, list[str], list[str]]:
    issue_refs: list[str] = []
    user_mentions: list[str] = []
    text=""""""


    # if item["type"] == "text":
    #     if len(text) == 0:
    #         parts.append(item)
    #     else:parts.append(f"{item}\n")
