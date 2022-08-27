# -*- coding: utf-8 -*-

"""
This file is part of the Anki IPA add-on for Anki.
Parsing methods
Copyright: (c) 2019 m-rtin <https://github.com/m-rtin>
License: GNU AGPLv3 <https://www.gnu.org/licenses/agpl.html>
"""

import urllib
import bs4
import re
import requests
from typing import List, Optional

# Create a dictionary for all transcription methods
transcription_methods = {}
transcription = lambda f: transcription_methods.setdefault(f.__name__, f)


@transcription
def british(word: str) -> str:
    payload = {'action': 'parse', 'page': word, 'format': 'json', 'prop': 'wikitext'}
    r = requests.get('https://en.wiktionary.org/w/api.php', params=payload)
    try:
        wikitext = r.json()['parse']['wikitext']['*']
        p = re.compile("{{a\|UK}} {{IPA\|en\|([^}]+)}}")
        m = p.search(wikitext)
        if m is None:
            p = re.compile("{{a\|RP}} {{IPA\|en\|([^}]+)}}")
            m = p.search(wikitext)
        if m is None: 
            p = re.compile("{{IPA\|en\|([^}]+)\|([^}]+)}}")
            m = p.search(wikitext)
        if m is None: 
            p = re.compile("{{IPA\|en\|([^}]+)}}")
            m = p.search(wikitext)
            
        ipa = m.group(1)
        return remove_special_chars(word=ipa)
    except (KeyError, AttributeError):
        return ""

@transcription
def american(word: str) -> str:
    payload = {'action': 'parse', 'page': word, 'format': 'json', 'prop': 'wikitext'}
    r = requests.get('https://en.wiktionary.org/w/api.php', params=payload)
    try:
        wikitext = r.json()['parse']['wikitext']['*']
        p = re.compile("{{a\|US}} {{IPA\|en\|([^}]+)}}")
        m = p.search(wikitext)
        if m is None: 
            p = re.compile("{{a\|GA}}.*?{{IPA\|en\|([^}]+)}}")
            m = p.search(wikitext)
        if m is None: 
            p = re.compile("{{a\|GenAm}}.*?{{IPA\|en\|([^}]+)}}")
            m = p.search(wikitext)
        if m is None:
            p = re.compile("{{IPA\|en\|([^}]+)\|([^}]+)}}")
            m = p.search(wikitext)
        if m is None:
            p = re.compile("{{IPA\|en\|([^}]+)}}")
            m = p.search(wikitext)

        ipa = m.group(1)
        return remove_special_chars(word=ipa)
    except (KeyError, AttributeError):
        return ""

@transcription
def dict_us(word: str) -> str:
    try:
        search_word = word.replace(' ', '+')
        ipa = __search_oxford(search_word)
        if ipa is None:
            ipa = __search_cambridge(search_word)
        if ipa is None:
            ipa = __search_wordhunt(search_word)
        if ipa is None:
            ipa = ' '.join([american(x) for x in word.split(' ')])
        return remove_special_chars(word=ipa)
    except (KeyError, AttributeError):
        return ""


def __search_oxford(word: str) -> str:
    p = re.compile(r"phons_n_am.*?\"phon\">/(?P<ipa>.*?)/")
    return __search_dict('https://www.oxfordlearnersdictionaries.com/search/english/direct/?q=' + word, p)


def __search_cambridge(word: str) -> str:
    p = re.compile(r"us dpron.*?lpl-1\">(?P<ipa>.*?)</")
    return __search_dict('https://dictionary.cambridge.org/search/direct/?datasetsearch=english&q=' + word, p)


def __search_wordhunt(word: str) -> str:
    p = re.compile(r"transcription.*?\|(?P<ipa>.*?)\|<")
    return __search_dict('https://wooordhunt.ru/word/' + word, p)


def __search_dict(url: str, p: re.Pattern[str]) -> Optional[str]:
    try:
        r = requests.get(url, 
            headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'})
        m = p.search(r.text.replace('\n', ' '))
        if m is not None:
            match = m.group('ipa')
            if len(match) > 50:
                return None
            return match
        return None
    except:
        return None
    

@transcription
def russian(word: str) -> str:
    link = f"https://ru.wiktionary.org/wiki/{word}"
    return ", ".join(parse_website(link, {'class': 'IPA'}))


@transcription
def french(word: str) -> str:
    link = f"https://fr.wiktionary.org/wiki/{word}"
    return ", ".join(parse_website(link, {'title': 'Prononciation API'}))


@transcription
def spanish(word: str) -> str:
    link = f"https://es.wiktionary.org/wiki/{word}"
    return ", ".join(parse_website(link, {'style': 'color:#368BC1'}))


@transcription
def russian(word: str) -> str:
    link = f"https://ru.wiktionary.org/wiki/{word}"
    return ", ".join(parse_website(link, {'class': 'IPA'}))


@transcription
def french(word: str) -> str:
    link = f"https://fr.wiktionary.org/wiki/{word}"
    return ", ".join(parse_website(link, {'title': 'Prononciation API'}))


@transcription
def spanish(word: str) -> str:
    link = f"https://es.wiktionary.org/wiki/{word}"
    return ", ".join(parse_website(link, {'style': 'color:#368BC1'}))


@transcription
def german(word: str) -> str:
    payload = {'action': 'parse', 'page': word, 'format': 'json', 'prop': 'wikitext'}
    r = requests.get('https://de.wiktionary.org/w/api.php', params=payload)
    try:
        wikitext = r.json()['parse']['wikitext']['*']
        p = re.compile("{{IPA}} {{Lautschrift\|([^}]+)")
        m = p.search(wikitext)
        ipa = m.group(1)
        return ipa
    except (KeyError, AttributeError):
        return ""


@transcription
def polish(word: str) -> str:
    link = f"https://pl.wiktionary.org/wiki/{word}"
    return ", ".join(parse_website(
        link, {'title': 'To jest wymowa w zapisie IPA; zobacz hasło IPA w Wikipedii'}))


@transcription
def dutch(word: str) -> str:
    link = f"https://nl.wiktionary.org/wiki/{word}"
    return ", ".join(parse_website(link, {"class": "IPAtekst"}))


def parse_website(link: str, css_code: dict) -> List[str]:
    try:
        website = requests.get(link)
    except requests.exceptions.RequestException as e:
        return [""]
    soup = bs4.BeautifulSoup(website.text, "html.parser")
    results = soup.find_all('span', css_code) 
    transcriptions = map(lambda result: result.getText()
        .replace("/", "")
        .replace("]", "")
        .replace("[", "")
        .replace(".", "")
        .replace("\\", ""), results)
    return sorted(list(set(transcriptions)))


def remove_special_chars(word: str) -> str:
   word = word.replace("/", "").replace("]", "").replace("[", "").replace(".", "").replace("\\", "").replace(".", "")
   return word


def transcript(words: List[str], language: str) -> str:
    transcription_method = transcription_methods[language]
    transcribed_words = [transcription_method(word) for word in words]
    return " ".join(transcribed_words)
