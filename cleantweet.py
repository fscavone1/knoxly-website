import re
import string
import csv

def strip_links(text):
    link_regex = re.compile('((https?):((//)|(\\\\))+([\w\d:#@%/;$()~_?\+-=\\\.&](#!)?)*)', re.DOTALL)
    links = re.findall(link_regex, text)
    for link in links:
        text = text.replace(link[0], ', ')
    return text


def strip_all_entities(text):
    entity_prefixes = ['@']
    for separator in string.punctuation:
        if separator not in entity_prefixes:
            text = text.replace(separator, ' ')
    words = []
    for word in text.split():
        word = word.strip()
        if word:
            if word[0] not in entity_prefixes:
                words.append(word)
    return ' '.join(words)


def clean(rows):
    refactored = []
    for line in rows:
        t = line[0]
        if '@' in t and 'https' in t:
            refactored.append(strip_all_entities(strip_links(t)))
        elif '@' in t:
            refactored.append(strip_all_entities(t))
        elif 'https' in t:
            refactored.append(strip_links(t))
        else:
            refactored.append(t)

    return refactored

