from datetime import datetime
import spacy
import re
import pickle

nlp = spacy.load('en_core_web_sm')

with open('data/names.set', 'rb') as f:
    names_set = pickle.load(f)

geo = ['Illinois', 'IL', 'United States', 'US', 'United States of America', 'USA']

phis = [
    # ('[*ADDRESS*]', '\\b(\d{3,})\s?(\w{0,5})\s([a-zA-Z]{2,30})\s([a-zA-Z]{2,15})\.?\s?(\w{0,5})\\b'),
    ('[*EMAIL*]', '\\b([a-zA-Z0-9_\-\.]+)@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.)|(([a-zA-Z0-9\-]+\.)+))([a-zA-Z]{2,4}|[0-9]{1,3})(\]?)\\b'),
    ('[*PHONE*]', '\\b(\+\d{1,2}\s)?\(?\d{3}\)?[\s.-]\d{3}[\s.-]\d{4}\\b'),
    ('[*ZIPCODE*]', '\\b\d{5}(?:-\d{4})?\\b'),
    ('[*SSN*]', '\\b\d{3}-\d{2}-\d{4}\\b'),
    ('[*URL*]', '\\b(https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9]\.[^\s]{2,})\\b'),
    ('[*IPv4*]', '\\b(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\\b'),
    ('[*IPv6*]', '\\b(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]))\\b'),
]




def replace_entity(token):
    space = ' ' if token.text_with_ws[-1] == ' ' else ''

    if token.ent_iob != 0 and token.text != '\n':
        if token.ent_type_ == 'PERSON':
            return '[*PERSON*]' + space
        elif token.ent_type_ == 'ORG':
            return '[*ORG*]' + space
        elif token.ent_type_ == 'GPE' and not [g for g in geo if g in token.text]:
            return '[*GPE*]' + space
        elif token.ent_type_ == 'DATE':
            try:
                if token.text.find('-') > -1:
                    year = datetime.strptime(token.text, '%m-%d-%Y').year
                elif token.text.find('/') > -1:
                    year = datetime.strptime(token.text, '%m/%d/%Y').year
                return '[*DATE-{}*]'.format(year) + space
            except:
                pass

    return token.string


def scrub_ml(doc):
    for ent in doc.ents:
        ent.merge()
    tokens = map(replace_entity, doc)
    return ''.join(tokens)


def scrub_rule(text, replacement, pattern):
    return re.sub(pattern, replacement, text)


def scrub_name(text):
    doc = nlp(text)

    di = ''

    for i, token in enumerate(doc):
        space = ' ' if token.text_with_ws[-1] == ' ' else ''
        if token.text.upper() in names_set:
            di += '[*NAME*]' + space
        else:
            di += token.text_with_ws

    return di


def deidentify(text):

    doc = nlp(text)
    di = scrub_ml(doc)

    for phi in phis:
        replacement, pattern = phi
        di = scrub_rule(di, replacement, pattern)

    di = scrub_name(di)

    return str(di)


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
