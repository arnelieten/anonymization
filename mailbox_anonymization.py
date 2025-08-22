from flair.data import Sentence
from flair.models import SequenceTagger
from dotenv import dotenv_values
import json
import re
import os


REGEX_SSN = re.compile(r'\b\d{2}\.\d{2}\.\d{2}-\d{3}\.\d{2}\b')
REGEX_IBAN = re.compile(r'\b(?:BE\d{14}|BE\d{2} \d{4} \d{4} \d{4})\b')
REGEX_PHONE_NATIONAL = re.compile(r'\b04\d{2}(?:(?:[ .\/]?\d{2}){3}|(?:[ .\/]?\d{3}){2})\.?\b')
REGEX_PHONE_INTERNATIONAL = re.compile(r'(?<!\()(?<!\d)\+32\s?(?:4\d{2}(?:\d{6}|(?:[ .\/]?\d{2}){3})|[1-9]\d?(?:[ .\/]?\d{2,3}){2,3})(?!\d)(?!\))')
REGEX_FORM_STUDENT = re.compile(r'(?<=Hey! Nieuwe inzending via het contactformulier:)(.*?)(?=\|\||$)')
REGEX_FORM_TEACHER = re.compile(r'(?<=Hey! Nieuwe inzending voor \"Lesgever\":)(.*?)(?=\|\||$)')
REGEX_LINK = re.compile(r'https?:\/\/\S+')
REGEX_EMAIL_EXTERNAL = re.compile(r'\b[^\s]+@(gmail\.com|telenet\.be|hotmail.be|hotmail.com|outlook.be|outlook.com)\b')
REGEX_EMAIL_INTERNAL = re.compile(r'\b[^\s]+@slaagtat\.be\b')
REGEX_MENTION = re.compile(r'@[A-Z][a-z]+(?:\s[A-Z][a-z]+)?')


def anonymize_regex(text: str) -> str:
    text = REGEX_IBAN.sub("<IBAN>", text)
    text = REGEX_SSN.sub("<SSN>", text)
    text = REGEX_PHONE_NATIONAL.sub("<PHONE>", text)
    text = REGEX_PHONE_INTERNATIONAL.sub("<PHONE>", text)
    text = REGEX_FORM_STUDENT.sub(" <FORM>", text)
    text = REGEX_FORM_TEACHER.sub(" <FORM>", text)
    text = REGEX_LINK.sub("<LINK>", text) # check if this is necessary!!
    text = REGEX_EMAIL_EXTERNAL.sub("<EMAIL EXTERNAL>", text)
    text = REGEX_EMAIL_INTERNAL.sub("<EMAIL INTERNAL>", text)
    text = REGEX_MENTION.sub("<MENTION>", text)
    return text


def normalize_brackets(text):
    text = re.sub(r'<{2,10}', '<', text)
    text = re.sub(r'>{2,10}', '>', text)
    return text


tagger = SequenceTagger.load("flair/ner-dutch-large")


def anonymize_ner(text: str) -> str:
    sentence = Sentence(text)
    tagger.predict(sentence)
    entities = [(entity.text, entity.tag) for entity in sentence.get_spans('ner') if entity.tag == "PER"]
    
    anonymized_text = text
    for entity_text, entity_tag in entities:
        anonymized_text = anonymized_text.replace(entity_text, "<PERSON>")
    
    return anonymized_text


config = dotenv_values(".env")
MAILBOX_CLEANED_PATH = config["MAILBOX_CLEANED_PATH"]
MAILBOX_ANONYMIZED_PATH = config["MAILBOX_ANONYMIZED_PATH"]
processed_uids = set()

if os.path.exists(MAILBOX_ANONYMIZED_PATH):
    with open(MAILBOX_ANONYMIZED_PATH, "r", encoding="utf-8") as f:
        for line in f:
            try:
                obj = json.loads(line)
                if "uid" in obj:
                    processed_uids.add(obj["uid"])
            except json.JSONDecodeError:
                continue

print(f"Found {len(processed_uids)} already processed messages.")


with open(MAILBOX_CLEANED_PATH, "r", encoding="utf-8") as mailbox_cleaned, \
     open(MAILBOX_ANONYMIZED_PATH, "a", encoding="utf-8") as mailbox_anonymized:

    for line in mailbox_cleaned:
        obj = json.loads(line)
        uid = obj.get("uid")

        if uid in processed_uids:
            continue

        body = anonymize_regex(obj.get("body") or "")
        body = anonymize_ner(body)
        body = normalize_brackets(body)
        obj["body"] = body

        processed_uids.add(uid)

        obj.pop("subject")
        mailbox_anonymized.write(json.dumps(obj, ensure_ascii=False) + "\n")