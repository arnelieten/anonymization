from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from presidio_analyzer.nlp_engine import NlpEngineProvider
from imap_tools import MailBox, AND
from dotenv import dotenv_values
from datetime import date
import json

def setup_analyzer():
    configuration = {
        "nlp_engine_name": "spacy",
        "models": [{"lang_code": "nl", "model_name": "nl_core_news_lg"}],
    }

    provider = NlpEngineProvider(nlp_configuration=configuration)
    nlp_engine = provider.create_engine()

    analyzer = AnalyzerEngine(nlp_engine=nlp_engine, supported_languages=["nl"])
    return analyzer


def anonymize_email(text):
    analyzer = setup_analyzer()
    anonymizer = AnonymizerEngine()

    results = analyzer.analyze(text=text, language="nl")
    anonymized_result = anonymizer.anonymize(text=text, analyzer_results=results)

    return anonymized_result.text


def flatten_email(text):
    return text.replace('\r', '').replace('\n', ' ')


def mailbox_to_json():
    config = dotenv_values(".env")
    MAIL_USERNAME = config["MAIL_USERNAME"]
    MAIL_PASSWORD = config["MAIL_PASSWORD"]
    CUTOFF_DATE = date(2025, 8, 2)
    OUTPUT_PATH = "C:\\Users\\arnel\\Projects\\anonymization\\mailbox.json"
    records = []

    with MailBox("imap.gmail.com").login(MAIL_USERNAME, MAIL_PASSWORD, "[Gmail]/Sent Mail") as mb:
        for email in mb.fetch(AND(date_gte=CUTOFF_DATE), reverse=True, mark_seen=False):
            records.append ({
                "subject" : email.subject,
                "body" : anonymize_email(flatten_email(email.text))
            })

    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(records, f, indent=2)

mailbox_to_json()