from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from presidio_analyzer.nlp_engine import NlpEngineProvider
import re

def load_analyzer():
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
    custom_engine = load_analyzer()
    anonymizer = AnonymizerEngine()

    text = anonymize_regex(text)
    analyzed_text = custom_engine.analyze(text=text, language="nl")
    anonymized_text = anonymizer.anonymize(text=text, analyzer_results=analyzed_text)

    return anonymized_text.text