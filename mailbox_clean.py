import json
from dotenv import dotenv_values
import re

seen = set()
config = dotenv_values(".env")
MAILBOX_EXTRACTED_PATH = config["MAILBOX_EXTRACTED_PATH"]
MAILBOX_CLEANED_PATH = config["MAILBOX_CLEANED_PATH"]

REGEX_GREETINGS = re.compile(r"(?:Beste|Dag|Hi|Hallo|Hoi|Geachte)\b.*?\r\n(?:[><]*\r\n)+")
REGEX_CLOSING_NEOL = re.compile(r"(?:Met Vriendelijke Groeten|Met vriendelijke groeten|Alvast bedankt en met vriendelijke groeten|Alvast bedankt en vriendelijke groeten|met vriendelijke groeten|Met vriendelijke groet|Vriendelijke groeten|Bedankt en groeten|Bedankt en groetjes|Bedankt en groet|Met warme groeten|Met warme groet|Warme groeten|Warme Groeten|Warme groet|Warme Groet|Vriendelijke groetjes|Hartelijke Groeten| Hartelijke groeten|Hartelijke Groet|Hartelijike groet|MVG|Mvg|mvg|Groetjes|Groeten)[\s\S]*?\|\|")
REGEX_CLOSING_EOL = re.compile(r"(?:Met Vriendelijke Groeten|Met vriendelijke groeten|Alvast bedankt en met vriendelijke groeten|Alvast bedankt en vriendelijke groeten|met vriendelijke groeten|Met vriendelijke groet|Vriendelijke groeten|Bedankt en groeten|Bedankt en groetjes|Bedankt en groet|Met warme groeten|Met warme groet|Warme groeten|Warme Groeten|Warme groet|Warme Groet|Vriendelijke groetjes|Hartelijke Groeten| Hartelijke groeten|Hartelijke Groet|Hartelijike groet|MVG|Mvg|mvg|Groetjes|Groeten)[\s\S]*")

REGEX_SQUARE_BRACKETS = r"\[(.*?)\]"
REGEX_ROUND_BRACKETS_WITH_AT = r"\([^()]*@[^()]*\)"
REGEX_SLAAGTAT = r"https://www\.slaagtat\.be/"
REGEX_ASTERISK = r"\*"


PATTERNS = [
    re.compile(REGEX_SQUARE_BRACKETS),
    re.compile(REGEX_ROUND_BRACKETS_WITH_AT),
    re.compile(REGEX_SLAAGTAT),
    re.compile(REGEX_ASTERISK),
]

def clean_email(text):
    text = text.replace('\r', '').replace('\n', ' ').replace('\t', ' ').replace('--', ' ')
    text = re.sub(r'<(?!PERSON>)|(?<!<PERSON)>', ' ', text)
    text = ' '.join(text.split())
    return text

with open(MAILBOX_EXTRACTED_PATH, "r", encoding="utf-8") as mailbox_extracted, \
     open(MAILBOX_CLEANED_PATH, "w", encoding="utf-8") as mailbox_cleaned:

    for line in mailbox_extracted:
        obj = json.loads(line)

        subject = (obj.get("subject") or "")
        if not (subject.startswith(("Re:", "Fwd:")) or subject not in seen):
            continue
        seen.add(subject)

        body = (obj.get("body") or "")
        body = REGEX_GREETINGS.sub("Beste <PERSON>, ", body)
        body = REGEX_CLOSING_NEOL.sub("||", body)
        body = REGEX_CLOSING_EOL.sub("", body)

        for pat in PATTERNS:
            body = pat.sub("", body)

        body = clean_email(body)
        obj["body"] = body

        if len(body.strip()) < 20:
            continue

        mailbox_cleaned.write(json.dumps(obj, ensure_ascii=False) + "\n")