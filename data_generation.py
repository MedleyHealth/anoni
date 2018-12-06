import re
import pickle

from loader import load_notes, load_phi_locations, load_phi_phrases


def find_unique_entities():
    """
    Finds the unique entity types (ie. Age, PTName, etc.) in PHI phrases.
    """

    phi_phrases = load_phi_phrases()
    unique_entities = {entry.split()[4] for entry in phi_phrases}
    print(unique_entities)


def parse_notes(notes):
    """
    Transforms nursing notes into JSON-formatted documents. Each document has
    an associated patient number, note number, free text, and an empty list for
    the PHI locations to be filled in later by create_training_data().
    """

    documents = []
    text = ''

    for i, line in enumerate(notes):

        if line.startswith('START_OF_RECORD='):
            patient_num, note_num = re.findall(r'\d+', line)

        elif line.startswith('||||END_OF_RECORD'):

            document = {
                "patient_number": patient_num,
                "note_number": note_num,
                "ided_text": text,
                "ref_phi": []
            }

            documents.append(document)
            text = ''

        else:
            text += line

    return documents


def create_training_data():
    """
    Creates training data in the right format to train a Named Entity Recognizer
    in Spacy. Has the format:

        TRAINING_DATA = [
            ('John admitted to Mayo Clinic ER.', {
                'entities': [(0, 4, 'PTName'), (17, 28, 'HCPName')]
            }),
            ('No PHI here.', {
                'entities': []
            })
        ]
    """

    notes = load_notes()
    phi_phrases = load_phi_phrases()
    documents = parse_notes(notes)

    for phrase in phi_phrases:
        phrase_list = phrase.split(' ')

        patient_number = phrase_list[0]
        note_number = phrase_list[1]
        index_start = phrase_list[2]
        index_end = phrase_list[3]
        phi_type = phrase_list[4]

        document = next(d for d in documents
                        if d['patient_number'] == patient_number
                        and d['note_number'] == note_number)

        ref_phi = (int(index_start), int(index_end), phi_type)

        document['ref_phi'].append(ref_phi)

    return [(d['ided_text'], {'entities': d['ref_phi']}) for d in documents]


def save_training_data(path='data/notes/ner.data'):
    """
    Creates and saves the training data to "/data/notes/ner.data" by default.
    Make sure that all directories in the path exist before running this.
    """

    data = create_training_data()

    try:
        with open(path, 'wb') as f:
            pickle.dump(data, f)
    except:
        raise OSError(('Error opening file to write training data. Are '
        'you sure that all directories exist in the path {}?'.format(path)))


if __name__ == '__main__':

    save_training_data()
