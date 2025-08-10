import json
from dotenv import dotenv_values

seen = set()
config = dotenv_values(".env")
MAILBOX_EXTRACTED_PATH = config["MAILBOX_EXTRACTED_PATH"]
MAILBOX_CLEANED_PATH = config["MAILBOX_CLEANED_PATH"]

with open(MAILBOX_EXTRACTED_PATH, "r", encoding="utf-8") as mailbox_extracted, \
     open(MAILBOX_CLEANED_PATH, "w", encoding="utf-8") as mailbox_cleaned:
    for line in mailbox_extracted:
        obj = json.loads(line)
        subj = obj.get("subject", "") or ""
        if subj.startswith(("Re:", "Fwd:")):
            mailbox_cleaned.write(json.dumps(obj, ensure_ascii=False) + "\n")
        elif subj not in seen:
            seen.add(subj)
            mailbox_cleaned.write(json.dumps(obj, ensure_ascii=False) + "\n")
