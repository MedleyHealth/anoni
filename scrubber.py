from datetime import datetime
from operator import itemgetter

import spacy
import re
import pickle

from addins import regex_patterns, geo


nlp = spacy.load('en_core_web_sm')

with open('data/names.set', 'rb') as f:
    names_set = pickle.load(f)


def scrub_ml(doc):
    """
    Performs named entity recognition. Assumes that any entities are PHI.

    Args:
        doc: Object     A sequence of Token objects in Spacy.

    Returns:
        A list of PHI entries (from ML) with location indices.
    """

    for ent in doc.ents:
        ent.merge()
    entries = map(replace_entity, doc)

    return [entry for entry in entries if entry is not None]


def replace_entity(token):
    """
    Scrubs tokens of the following entity types:

        PERSON    Person name
        ORG       Organization
        GPE       Geopolitical entity

    For GPE entities, it further checks if the entity is at the state-level or
    higher. HIPAA allows for geographic descriptions such as state and country.
    If at the state-level or higher, it does not scrub the entity.

    Args:
        token: Object   A Spacy object for >= 1 word, punctuation, etc.

    Returns:
         A PHI entry if the token is an entity, else None.

    """

    phi_type = None

    if token.ent_iob != 0 and token.text.find('\n') == -1:
        if token.ent_type_ == 'PERSON':
            phi_type = 'PERSON'
        elif token.ent_type_ == 'ORG':
            phi_type = 'ORG'
        elif token.ent_type_ == 'GPE' and not [g for g in geo if g in token.text]:
            phi_type = 'GPE'

    if phi_type:
        index_start = token.idx
        index_end = index_start + len(token)
        entry = new_phi(token.text, index_start, index_end, phi_type, 'ML')
        return entry

    return None


def scrub_regex(text):
    """
    Performs regex matching on text. Assumes that any match is a PHI entry.

    Args:
        text: String    The original text with PHI still included.

    Returns:
        A list of PHI entries (from REGEX) with location indices.
    """

    return [new_phi(m.group(), m.start(), m.end(), phi_type, 'REGEX')
            for phi_type, pattern in regex_patterns
            for m in re.finditer(pattern, text)]


def scrub_dict(doc):
    """
    Performs dictionary lookup for each token in the doc. Assumes that any token
    in the dictionary is a PHI entry.

    Args:
        doc: Object     A sequence of Token objects in Spacy.

    Returns:
        A list of PHI entries (from DICT) with location indices.
    """

    return [new_phi(token.text, token.idx, token.idx+len(token),'PERSON','DICT')
            for token in doc if token.text.upper() in names_set]


def scrubber(text):
    """
    Determines the location indices of Personal Health Information (PHI) within
    the text by three methods:

        Machine learning
        Regex matching
        Dictionary lookup

    Args:
        text: String    The original text with PHI still included.

    Returns:
        A list of PHI entries with conflicts managed for overlapping entries.
    """

    doc = nlp(text)

    regex_entries = scrub_regex(text)
    dict_entries = scrub_dict(doc)
    ml_entries = scrub_ml(doc)

    return manage_conflicts(regex_entries + dict_entries + ml_entries)


def manage_conflicts(phi_entries):
    """
    Manages conflicts between overlapping PHI entries. The first occurrence of
    PHI in a set of overlapping PHI gets defined as the Reference PHI. The
    remaining PHI in the set are compared to the Reference PHI and given a
    conflict type by their relationship to the Reference PHI.

            Jane            Reference PHI

      Sarah Jane            Left conflict
            Jane Smith      Right conflict
            Jan             Inner conflict
      Sarah Jane Smith      Left and right conflict

    Currently, the algorithm removes any overlapping PHI except the Reference
    PHI. A more sophisticated approach would likely want to encapsulate the full
    range of overlapping PHI (ie. Sarah Jane Smith merged as one PHI). To do so,
    the algorithm must determine which phi_type to choose to represent the
    new, merged PHI entry. There is no guarantee that phi_type will be the same.

    Args:
        phi_entries: List   The PHI entries and locations within the text.

    Returns:
        A list of PHI entries with conflicts managed for overlapping entries.
    """

    phi_entries.sort(key=itemgetter('scrub_type'), reverse=True)
    phi_entries.sort(key=itemgetter('index_start'))

    prev_begin = prev_end = 99999999

    for entry in phi_entries[:]:
        current_begin = entry['index_start']
        current_end = entry['index_end']

        left_conflict = current_begin < prev_begin < current_end
        right_conflict = current_begin < prev_end < current_end
        inner_conflict = prev_begin <= current_begin and prev_end >= current_end

        if left_conflict or right_conflict or inner_conflict:
            phi_entries.remove(entry)
        else:
            prev_begin = current_begin
            prev_end = current_end

    return phi_entries



def replace_phi(text, phi_entries):
    """
    Takes the original, identified text and replaces all instances of PHI with
    the appropriate replacement tag (ie. [*PERSON*], [*ORG*], etc.)

    Args:
        text: String        The original text with PHI still included.
        phi_entries: List   The PHI entries and locations within the text.

    Returns:
        A de-identified string with all PHI replaced by [*PHI_TYPE*] tags.
    """

    if not phi_entries:
        return text

    deid = ''
    prev_end = 0

    for entry in phi_entries:
        index_start = entry['index_start']
        index_end = entry['index_end']
        phi_type = entry['phi_type']

        substring = text[prev_end:index_start]
        deid += '{}[*{}*]'.format(substring, phi_type)

        prev_end = index_end

    deid += text[index_end:]

    return deid


def new_phi(text, index_start, index_end, phi_type, scrub_type):
    """
    Factory function to create a JSON representation of a PHI entry.

    Args:
        text: String        Text value of the PHI.
        index_start: Int    Character offset from document start to PHI start.
        index_end: Int      Character offset from document start to PHI end.
        phi_type: String    Category of PHI (ie. PERSON, DATE,...).
        scrub_type: String  Method used by scrubber (ie. DICT, REGEX, or ML).

    Returns:
        A JSON representation of a PHI entry.
    """

    entry = {
        "text": text,
        "index_start": index_start,
        "index_end": index_end,
        "phi_type": phi_type,
        "scrub_type": scrub_type
    }

    return entry


def new_document(text, deid, phi_entries):
    """
    Factory function to create a JSON representation of the original text, the
    deidentified text, and the PHI entries within the text.

    Args:
        text: String        The original text with PHI still included.
        deid: String        The de-identified text with PHI replacements.
        phi_entries: List   The PHI entries and locations within the text.

    Returns:
        A JSON representation of the de-identified document.
    """

    document = {
        "text": text,
        "deid": deid,
        "phi_entries": phi_entries
    }

    return document


def deidentify(text):
    """
    De-identifies text from a single text document. Returns a JSON
    representation of the identified text, the deidentified text, and the PHI
    occurrences within the text.

    Args:
        text: String    The original text with PHI still included.

    Returns:
        A JSON representation of a de-identified document with form below:

    {
        "text": "John went to the Mayo Clinic on 01/01/2018."
        "deid": "[*PERSON*] went to [*ORG*] on [*DATE*]."
        "phi_entries": [
            {
            "index_start": 0,
            "index_end": 4,
            "phi_type": "PERSON",
            "scrub_type": "ML"
            },
            {
            "index_start": 13,
            "index_end": 28,
            "phi_type": "ORG",
            "scrub_type": "ML"
            },
            {
            "index_start": 32,
            "index_end": 42,
            "phi_type": "DATE",
            "scrub_type": "REGEX"
            },
        ]
    }
    """

    phi_entries = scrubber(text)
    deid = replace_phi(text, phi_entries)
    document = new_document(text, deid, phi_entries)

    return document


if __name__ == '__main__':
    pass
