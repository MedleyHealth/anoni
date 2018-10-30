import spacy


def load_nlp(size='small', segmenter=False, disable=[]):
    """
    Loads the nlp object from Spacy, which implements the Spacy pipeline.

    Disables the Named Entity Recognizer (ner) for increased performance. This
    functionality is not currently used anywhere.

    The segmenter further disables the tagger to speed up the sentence
    segmentation process.

    Attributes:

        model_size: 'small' or 'medium'
        segmenter: True - turns off POS tagger to speed up sentence segmentation
    """

    if size == 'small':
        model_size = 'en_core_web_sm'
    else:
        model_size = 'en_coref_md'

    return spacy.load(model_size, disable=disable)


def print_tokens(s):
    """
    Input a sentence s from tokens.sents. Prints out the token index, the
    original text of the token, and the simple part-of-speech. Example:

        0 Our ADJ
        1 model NOUN
        2 offers VERB
        ...
    """

    print('\n')
    for n, token in enumerate(s):
        print(n, token, token.pos_, token.tag_, token.dep_)
    print('\n')


def print_ents(doc):
    print('\n')
    for ent in doc.ents:
        print(ent.text, ent.start_char, ent.end_char, ent.label_)


def printb(message, content):
    print('{} ['.format(message) + content + ']')
