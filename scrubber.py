from datetime import datetime
from operator import itemgetter

import spacy
import re
import pickle

nlp = spacy.load('en_core_web_sm')

with open('data/names.set', 'rb') as f:
    names_set = pickle.load(f)

geo = ['Illinois', 'IL', 'United States', 'US', 'United States of America', 'USA']

regex_patterns = [
    # ('[*ADDRESS*]', '\\b(\d{3,})\s?(\w{0,5})\s([a-zA-Z]{2,30})\s([a-zA-Z]{2,15})\.?\s?(\w{0,5})\\b'),
    ('DATE', '\\b([0]?[1-9]|[1][0-2])[./-]([0]?[1-9]|[1|2][0-9]|[3][0|1])([./-]([0-9]{4}|[0-9]{2}))?\\b'),
    ('EMAIL', '\\b([a-zA-Z0-9_\-\.]+)@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.)|(([a-zA-Z0-9\-]+\.)+))([a-zA-Z]{2,4}|[0-9]{1,3})(\]?)\\b'),
    ('PHONE', '\\b(\+\d{1,2}\s)?\(?\d{3}\)?[\s.-]\d{3}[\s.-]\d{4}\\b'),
    ('ZIPCODE', '\\b\d{5}(?:-\d{4})?\\b'),
    ('SSN', '\\b\d{3}-\d{2}-\d{4}\\b'),
    ('URL', '\\b(https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9]\.[^\s]{2,})\\b'),
    ('IPv4', '\\b(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\\b'),
    ('IPv6', '\\b(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]))\\b'),
]


def scrub_ml(doc):
    """

    """

    for ent in doc.ents:
        ent.merge()
    entries = map(replace_entity, doc)
    return [entry for entry in entries if entry is not None]


def replace_entity(token):
    """

    """

    phi_type = None

    if token.ent_iob != 0 and token.text.find('\n') == -1:
        if token.ent_type_ == 'PERSON':
            phi_type = 'PERSON'
        elif token.ent_type_ == 'ORG':
            phi_type = 'ORG'
        elif token.ent_type_ == 'GPE' and not [g for g in geo if g in token.text]:
            phi_type = 'GPE'
        # elif token.ent_type_ == 'DATE':
        #     phi_type = 'DATE'

    if phi_type:
        index_start = token.idx
        index_end = index_start + len(token)

        entry = new_phi_entry(token.text, index_start, index_end, phi_type, 'ML')
        return entry
    else:
        return None


def scrub_regex(ided_text):
    """

    """

    regex_entries = [new_phi_entry(m.group(), m.start(), m.end(), phi_type, 'REGEX')
                     for phi_type, pattern in regex_patterns
                     for m in re.finditer(pattern, ided_text)]

    return regex_entries


def scrub_dict(ided_text):
    """

    """

    indices = []
    doc = nlp(ided_text)

    for i, token in enumerate(doc):
        if token.text.upper() in names_set:
            entry = new_phi_entry(token.text, token.idx, token.idx + len(token), 'PERSON', 'DICT')
            indices.append(entry)

    return indices


def scrubber(ided_text):
    """
    Determines the location indices of PHI within the text by three methods:

        Machine learning
        Regex matching
        Dictionary lookup
    """

    doc = nlp(ided_text)

    regex_entries = scrub_regex(ided_text)
    ml_entries = scrub_ml(doc)
    dict_entries = scrub_dict(ided_text)

    a = regex_entries + ml_entries + dict_entries
    for ab in a:
        print(ab)

    return manage_conflicts(regex_entries + ml_entries + dict_entries)


def manage_conflicts(phi_entries):
    """

    """

    entries = sorted(phi_entries, key=itemgetter('index_start', 'index_end'))
    prev_begin = prev_end = 99999999

    for entry in entries[:]:
        current_begin = entry['index_start']
        current_end = entry['index_end']

        left_conflict = current_begin < prev_begin < current_end
        right_conflict = current_begin < prev_end < current_end
        inner_conflict = prev_begin <= current_begin and prev_end >= current_end

        if left_conflict or right_conflict or inner_conflict:
            entries.remove(entry)
        else:
            prev_begin = current_begin
            prev_end = current_end

    return entries



def replace_phi(ided_text, phi_entries):
    """
    Takes the original, identified text and replaces all instances of PHI with
    the appropriate replacement tag (ie. [*PERSON*], [*ORG*], etc.)
    """

    if not phi_entries:
        return ided_text

    deid_text = ''
    prev_end = 0

    for entry in phi_entries:
        index_start = entry['index_start']
        index_end = entry['index_end']
        phi_type = entry['phi_type']

        pre = ided_text[prev_end:index_start]
        prev_end = index_end

        deid_text += '{}[*{}*]'.format(pre, phi_type)

    deid_text += ided_text[index_end:]

    return deid_text


def new_phi_entry(text, index_start, index_end, phi_type, scrub_type):
    """
    Returns a JSON representation of an instance of PHI.
    """

    entry = {
        "text": text,
        "index_start": index_start,
        "index_end": index_end,
        "phi_type": phi_type,
        "scrub_type": scrub_type
    }

    return entry


def new_document(ided_text, deid_text, phi_entries):
    """
    Returns a JSON representation of the deidentified document.
    """

    document = {
        "ided_text": ided_text,
        "deid_text": deid_text,
        "phi_entries": phi_entries
    }

    return document


def deidentify(ided_text):
    """
    De-identifies text from a single text document. Returns a JSON
    representation of the identified text, the deidentified text, and the PHI
    occurrences within the text.

    {
        "ided_text": "John went to the Mayo Clinic. Email is john@doe.com."
        "deid_text": "[*PERSON*] went to [*ORG*]. Email is [*EMAIL*]"
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
            "index_start": 39,
            "index_end": 51,
            "phi_type": "EMAIL",
            "scrub_type": "REGEX"
            },
        ]
    }
    """

    phi_entries = scrubber(ided_text)
    deid_text = replace_phi(ided_text, phi_entries)
    document = new_document(ided_text, deid_text, phi_entries)

    # for entry in phi_entries:
    #     print(entry)

    return document


if __name__ == '__main__':
    pass

    # entries = get_data()
    #
    # for i, entry in enumerate(entries):
    #     # if i > 3: break
    #     if i % 100 == 0: print(i)
    #
    #     patient, note, text = entry
    #
    #     T += 'Patient {}\tNote {}\n'.format(patient, note)
    #
    #     doc = nlp(text)
    #     di = scrub(doc)
    #
    #     # for phi in phis:
    #     #     repl, pattern = phi
    #     #     di = scrubify(di, repl, pattern)
    #
    # with open('test.phi', 'w') as f:
    #     f.write(T)
    #
    # print(T)


# Regex matching
# Dictionary lookup
# Natural language processing via machine learning

# Reverse iteration through phi_entries to avoid disrupting prior indices
#
#     Must first order phi_entries somehow
#
#         By index start?
#         By index end?
#
# How to determine which PHI type to choose with overlap in indices?
#
#     In the demo case, do we choose WEBSITE or ORG?
