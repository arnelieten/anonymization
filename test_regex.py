import re

use_cases = [
    "Dag Monika Dank",
    "Beste Sabrina In",
    "Beste Deiana Onze",
    "Dag Mattia Er",
    "Beste Mieke, Bedankt",
    "Geachte Maissa, Wat",
    "Beste Sofie Via",
    "Beste Tinne, Graag",
    "Hoi Tonika, Ik",
    "Hoi Luna, Zou",
    "Beste Samin, Excuses",
    "Hallo Luna, Even",
    "Hi Filip, Heel", #13 Basics
    "Beste Mr. Gelders, Dat",
    "Beste Mr. Stockmans, Nogmaals",
    "Beste meneer Bossuyt Dank",
    "Beste meneer Heylen We",
    "Beste meneer Cruts Dank",
    "Beste Mr. Charatyan, Het",
    "Beste mr. Heylen In",
    "Beste Mr. Heylen",
    "Beste Mevr. Leyssens, Al",
    "Beste Mevr. Van Laere, Geweldig",
    "Beste Mevr. van Kruijssen, Alvast",
    "Beste mevrouw Marien Het",
    "Beste mevrouw Beumont Dank",
    "Geachte heer Agneessens-Oosterlinck, Super",
    "Geachte heer Rommelaere Gelieve",
    "Beste Mevr. Mariën, Bedankt", #29 Formal
    "Beste Artuch, beste meneer Azizyan In",
    "Beste Mr. Janssens en Mevr. Libersens, Ik",
    "Beste mevrouw Barbara en Margot, Bedankt",
    "Beste Fee, Beste Mevr. Dombrecht, Super",
    "Beste Marlies, Beste Mevr. Vanruysevelt," #34 Combo
]


# to detect slaagtat emails
regex_pattern = r"\b(Dag|Beste|Geachte|Hoi|Hallo|Hi)\s+[A-Z][a-z]+,?(?=\s|$)"


for i, text in enumerate(use_cases, start=1):
    match = re.search(regex_pattern, text)
    print(f"Tekst {i}: {'✅ Match gevonden!' if match else '❌ Geen match.'}")
