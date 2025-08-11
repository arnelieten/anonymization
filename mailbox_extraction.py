from imap_tools import MailBox, AND
from dotenv import dotenv_values
from datetime import date, datetime
import json
import re

def split_email(text):
    REGEX_RESPONSE_ON = r"On(?:[\s\S]*?@[\s\S]*?)(?:\r?\n\r?\n|\r?\n>\r?\n>)"
    REGEX_RESPONSE_OP = r"Op(?:[\s\S]*?@[\s\S]*?)(?:\r?\n\r?\n|\r?\n>\r?\n>)"
    REGEX_FORWARD     = r"-{3,30}(?:[\s\S]*?@[\s\S]*?)(?:\r?\n\r?\n|\r?\n>\r?\n>)"

    REGEX_COMBINED = re.compile(
        f"(?:{REGEX_RESPONSE_ON}|{REGEX_RESPONSE_OP}|{REGEX_FORWARD})",
        flags=re.MULTILINE,
    )
    return REGEX_COMBINED.sub(" || ", text)


def load_checkpoint():
    config = dotenv_values(".env")
    CHECKPOINT_FILE = config["CHECKPOINT_FILE"]

    with open(CHECKPOINT_FILE, 'r') as f:
            data = json.load(f)
            lowest_key = min(data, key=data.get)
            checkpoint = data[lowest_key]
            return checkpoint
    
    
def save_checkpoint(uid):
    config = dotenv_values(".env")
    CHECKPOINT_FILE = config["CHECKPOINT_FILE"]

    with open(CHECKPOINT_FILE, 'r') as f:
        data = json.load(f)
        current_time = datetime.now().isoformat()
        data[current_time] = uid

    with open(CHECKPOINT_FILE, 'w') as f:
        json.dump(data, f)


def mailbox_to_json():
    config = dotenv_values(".env")
    MAIL_USERNAME = config["MAIL_USERNAME"]
    MAIL_PASSWORD = config["MAIL_PASSWORD"]
    MAILBOX_EXTRACTED_PATH = config["MAILBOX_EXTRACTED_PATH"]
    CUTOFF_DATE = date(2024, 8, 2)
    ITERATIONS = 500
    ITERATION_COUNTER = 0
    BATCH_SIZE = 100

    with MailBox("imap.gmail.com").login(MAIL_USERNAME, MAIL_PASSWORD, "[Gmail]/Sent Mail") as mb:
        with open(MAILBOX_EXTRACTED_PATH, 'a', encoding='utf-8') as f:
            while ITERATION_COUNTER < ITERATIONS:
                CHECKPOINT = load_checkpoint()
                
                for email in mb.fetch(
                    AND(date_gte=CUTOFF_DATE, uid=f"1:{CHECKPOINT-1}"),
                    reverse=True,
                    mark_seen=False,
                    bulk=True,
                    limit=BATCH_SIZE
                    ):
                    
                    record = {
                        "uid": email.uid,
                        "subject": email.subject,
                        "body": split_email(email.text)
                    }
                    f.write(json.dumps(record, ensure_ascii=False) + '\n')

                print(f"{67960 - CHECKPOINT} mails processed, now at uid: {CHECKPOINT}")
                save_checkpoint(int(email.uid))
                ITERATION_COUNTER += 1


mailbox_to_json()
