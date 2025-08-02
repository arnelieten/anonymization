from imap_tools import MailBox
from dotenv import dotenv_values


def flatten_email(text):
    return text.replace('\r', '').replace('\n', ' ')

def anonymize_email(msg):
    print("not ready yet")

def imap_to_json():
    config = dotenv_values(".env")
    MAIL_USERNAME= config["MAIL_USERNAME"]
    MAIL_PASSWORD= config["MAIL_PASSWORD"]

    with MailBox("imap.gmail.com").login(MAIL_USERNAME, MAIL_PASSWORD, "[Gmail]/Sent Mail") as mb:
        for msg in mb.fetch(limit=1, reverse=True, mark_seen=False):
            record = {
                "subject" : msg.subject,
                "sender" : msg.from_,
                "receiver" : msg.to,
                "date" : msg.date,
                "content" : flatten_email(msg.text)
            }

            print(record)

imap_to_json()