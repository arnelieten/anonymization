from imap_tools import MailBox, AND
from dotenv import dotenv_values
from datetime import date
import json


def flatten_email(text):
    return text.replace('\r', '').replace('\n', ' ')

def anonymize_email(email):
    print("not ready yet")

def mailbox_to_json():
    config = dotenv_values(".env")
    MAIL_USERNAME = config["MAIL_USERNAME"]
    MAIL_PASSWORD = config["MAIL_PASSWORD"]
    CUTOFF_DATE = date(2024, 8, 1) # check this out tomorrow if it works!!
    OUTPUT_PATH = "C:\\Users\\arnel\\Projects\\anonymization\\mailbox.json"
    records = []

    with MailBox("imap.gmail.com").login(MAIL_USERNAME, MAIL_PASSWORD, "[Gmail]/Sent Mail") as mb:
        for email in mb.fetch(AND(date_gte=CUTOFF_DATE), reverse=True, mark_seen=False):
            records.append ({
                "subject" : email.subject,
                "body" : flatten_email(email.text)
            })

    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(records, f, indent=2)

mailbox_to_json()