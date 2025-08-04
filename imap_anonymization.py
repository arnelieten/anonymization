from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from presidio_analyzer.nlp_engine import NlpEngineProvider
from imap_tools import MailBox, AND
from dotenv import dotenv_values
from datetime import date
import json
import re


def setup_analyzer():
    configuration = {
        "nlp_engine_name": "spacy",
        "models": [{"lang_code": "nl", "model_name": "nl_core_news_lg"}],
    }

    provider = NlpEngineProvider(nlp_configuration=configuration)
    nlp_engine = provider.create_engine()

    analyzer = AnalyzerEngine(nlp_engine=nlp_engine, supported_languages=["nl"])
    return analyzer


def anonymize_regex(text):
    IBAN_pattern = re.compile(r"\b[A-Z]{2}[ .-]?[0-9]{2}(?:[ .-]?[0-9A-Z]{4}){3,4}\b", re.IGNORECASE)
    SSN_pattern = re.compile(r"\b(?:\d[ .-]?){10,12}\b", re.IGNORECASE)

    text = IBAN_pattern.sub("<IBAN>", text)
    text = SSN_pattern.sub("<SSN / PHONE>", text)
    return text


def anonymize_email(text):
    analyzer = setup_analyzer()
    anonymizer = AnonymizerEngine()

    text = anonymize_regex(text)
    results = analyzer.analyze(text=text, language="nl")
    anonymized_result = anonymizer.anonymize(text=text, analyzer_results=results)
    return anonymized_result.text


def flatten_email(text):
    return text.replace('\r', '').replace('\n', ' ')


def mailbox_to_json():
    config = dotenv_values(".env")
    MAIL_USERNAME = config["MAIL_USERNAME"]
    MAIL_PASSWORD = config["MAIL_PASSWORD"]
    OUTPUT_PATH = config["OUTPUT_PATH"]
    CUTOFF_DATE = date(2025, 8, 2)
    BATCH_SIZE = 4
    records = []
    count = 1

    with MailBox("imap.gmail.com").login(MAIL_USERNAME, MAIL_PASSWORD, "[Gmail]/Sent Mail") as mb:
        with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
            for email in mb.fetch(AND(date_gte=CUTOFF_DATE), reverse=True, mark_seen=False):
                record = {
                    "subject": email.subject,
                    "body": anonymize_email(flatten_email(email.text))
                }
                f.write(json.dumps(record, ensure_ascii=False) + '\n')
                if count < BATCH_SIZE:
                    count += 1
                else:
                    break

mailbox_to_json()

### think about checkpointing and rate limits!!
### check out this link https://support.google.com/a/answer/1071518