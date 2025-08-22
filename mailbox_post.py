from dotenv import dotenv_values
import json
import os


config = dotenv_values(".env")
MAILBOX_ANONYMIZED_PATH = config["MAILBOX_ANONYMIZED_PATH"]
MAILBOX_POST_PATH = config["MAILBOX_POST_PATH"]


with open(MAILBOX_ANONYMIZED_PATH, "r", encoding="utf-8") as mailbox_anonymized, \
     open(MAILBOX_POST_PATH, "a", encoding="utf-8") as mailbox_post:
        for line in mailbox_anonymized:
            obj = json.loads(line)
            obj.pop("uid")
            mailbox_post.write(json.dumps(obj, ensure_ascii=False) + "\n")