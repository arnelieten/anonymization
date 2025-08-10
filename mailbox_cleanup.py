import json

seen = set()
with open("test_mailbox.jsonl") as fin, open("output_mailbox.jsonl", "w") as fout:
    for line in fin:
        obj = json.loads(line)
        subj = obj["subject"]
        if subj.startswith(("Re:", "Fwd:")):
            fout.write(json.dumps(obj, ensure_ascii=False) + "\n")
        elif subj not in seen:
            seen.add(subj)
            fout.write(json.dumps(obj, ensure_ascii=False) + "\n")