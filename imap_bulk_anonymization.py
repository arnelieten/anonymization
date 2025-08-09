from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from presidio_analyzer.nlp_engine import NlpEngineProvider
from imap_tools import MailBox, AND
from dotenv import dotenv_values
from datetime import date, datetime
import time
import json
import re


def load_general_analyzer():
    configuration = {
        "nlp_engine_name": "spacy",
        "models": [{"lang_code": "nl", "model_name": "nl_core_news_lg"}],
    }

    provider = NlpEngineProvider(nlp_configuration=configuration)
    nlp_engine = provider.create_engine()

    analyzer = AnalyzerEngine(nlp_engine=nlp_engine, supported_languages=["nl"])
    return analyzer


def load_names_analyzer():
    configuration = {
        "nlp_engine_name": "spacy",
        "models": [{"lang_code": "nl", "model_name": "xx_ent_wiki_sm"}],
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
    general_engine = load_general_analyzer()
    names_engine = load_names_analyzer()
    anonymizer = AnonymizerEngine()

    text = anonymize_regex(text)
    general_analyzed_text = general_engine.analyze(text=text, language="nl")
    general_anonymized_text = anonymizer.anonymize(text=text, analyzer_results=general_analyzed_text)

    names_analyzed_text = names_engine.analyze(text=general_anonymized_text.text, language="nl")
    names_anonymized_text = anonymizer.anonymize(text=general_anonymized_text.text, analyzer_results=names_analyzed_text)

    return names_anonymized_text.text


def flatten_email(text):
    return text.replace('\r', '').replace('\n', ' ').replace('\t', ' ')


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
    OUTPUT_PATH = config["OUTPUT_PATH"]
    CUTOFF_DATE = date(2025, 8, 2)
    ITERATIONS = 3
    ITERATION_COUNTER = 0
    BATCH_SIZE = 4

    with MailBox("imap.gmail.com").login(MAIL_USERNAME, MAIL_PASSWORD, "[Gmail]/Sent Mail") as mb:
        with open(OUTPUT_PATH, 'a', encoding='utf-8') as f:
            while ITERATION_COUNTER < ITERATIONS:
                BATCH_COUNTER = 0
                CHECKPOINT = load_checkpoint()
                print(CHECKPOINT)

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
                        "body": anonymize_email(flatten_email(email.text))
                    }
                    f.write(json.dumps(record, ensure_ascii=False) + '\n')

                save_checkpoint(int(email.uid))
                ITERATION_COUNTER += 1

start_time = time.time()
mailbox_to_json()
end_time = time.time()
print(f"Processing took {end_time - start_time:.2f} seconds.")