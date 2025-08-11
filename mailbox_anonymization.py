from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from presidio_analyzer.nlp_engine import NlpEngineProvider
from dotenv import dotenv_values
import json
import re


configuration = {
    "nlp_engine_name": "spacy",
    "models": [{"lang_code": "nl", "model_name": "nl_core_news_lg"}],
}

provider = NlpEngineProvider(nlp_configuration=configuration)
nlp_engine = provider.create_engine()
analyzer = AnalyzerEngine(nlp_engine=nlp_engine, supported_languages=["nl"])
anonymizer = AnonymizerEngine()


REGEX_IBAN = re.compile(r"\b[A-Z]{2}[ .-]?[0-9]{2}(?:[ .-]?[0-9A-Z]{4}){3,4}\b", re.IGNORECASE)
REGEX_SSN = re.compile(r"\b(?:\d[ .-]?){10,12}\b")

def anonymize_regex(text: str) -> str:
    # text = REGEX_IBAN.sub("<IBAN>", text)
    # text = REGEX_SSN.sub("<SSN / PHONE>", text)
    return text

def anonymize_email(text: str) -> str:
    text = anonymize_regex(text)
    results = analyzer.analyze(text=text, language="nl")
    return anonymizer.anonymize(text=text, analyzer_results=results).text


config = dotenv_values(".env")
MAILBOX_CLEANED_PATH = config["MAILBOX_CLEANED_PATH"]
MAILBOX_ANONYMIZED_PATH = config["MAILBOX_ANONYMIZED_PATH"]

with open(MAILBOX_CLEANED_PATH, "r", encoding="utf-8") as mailbox_cleaned, \
     open(MAILBOX_ANONYMIZED_PATH, "w", encoding="utf-8") as mailbox_anonymized:

    for line in mailbox_cleaned:
        obj = json.loads(line)
        body = anonymize_regex(obj.get("body") or "")
        obj["body"] = body
        mailbox_anonymized.write(json.dumps(obj, ensure_ascii=False) + "\n")