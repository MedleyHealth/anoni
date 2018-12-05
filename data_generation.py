import re
import scrubber
import pickle


def get_targets():
    """
    Opens the targets from the i2b2 de-identification challenge. Returns a list
    of the PHI indices (begin/begin/end) within each note for each patient.

    Format (tab delimited):

        Patient 1	Note 1
        23	23	42
        114	114	121
        197	197	208
        Patient 1   Note 2
        ...
        Patient 2   Note 1
        ...

    Source: https://www.physionet.org/physiotools/deid/
    """

    path = 'data/notes/id.phi'

    with open(path, 'r') as f:
        targets = f.readlines()

    return targets


def get_ided_text():
    """

    """

    path = 'data/notes/id.text'

    with open(path, 'r') as f:
        ided_text = f.readlines()

    return ided_text


def get_phi_phrases():
    """
    Returns the PHI phrases. Has the format:

        PATIENT #   NOTE #   INDEX-START   INDEX_END   PHI-TYPE   PHI-TEXT
        1           1        73            77          PTName     John
        1           3        20            31          HCPName    Mayo Clinic
        2           1        0             6           Date       1/1/18

    PHI phrases can be of the following PHI types:

        Age
        Other
        PTName
        Initial
        Location
        PTName
        Date
        DateYear
        Phone
        Relative
        ProxyName
        HCPName

    Training a named entity recognizer for a custom model uses these PHI types.
    """

    path = 'data/notes/id-phi.phrase'

    with open(path, 'r') as f:
        phi_phrases = f.readlines()

    return phi_phrases


def parse_ided_text(ided_text):
    """

    """

    documents = []
    text = ''

    for i, line in enumerate(ided_text):

        if line[:16] == 'START_OF_RECORD=':
            patient, note = re.findall(r'\d+', line)

        elif line == '||||END_OF_RECORD\n':
            document = create_document(patient, note, text)
            documents.append(document)
            text = ''

        else:
            text += line

    return documents


def create_document(patient_number, note_number, ided_text):
    """
    Factory method to create a JSON representation of the medical record
    documents.
    """

    document = {
        "patient_number": patient_number,
        "note_number": note_number,
        "ided_text": ided_text,
        "ref_phi": []
    }

    return document


def get_unique_entities():
    """ Finds the unique entity types (ie. Age, PTName, etc.) in PHI phrases."""

    phi_phrases = get_phi_phrases()
    unique_entities = {entry.split()[4] for entry in phi_phrases}
    print(unique_entities)


def create_training_data():

    ided_text = get_ided_text()
    documents = parse_ided_text(ided_text)

    phi_phrases = get_phi_phrases()

    for phrase in phi_phrases:
        phrase_list = phrase.split(' ')

        patient_number = phrase_list[0]
        note_number = phrase_list[1]
        index_start = phrase_list[2]
        index_end = phrase_list[3]
        phi_type = phrase_list[4]

        document = next(doc for doc in documents
                        if doc['patient_number'] == patient_number
                        and doc['note_number'] == note_number)

        ref_phi = (int(index_start), int(index_end), phi_type)

        document['ref_phi'].append(ref_phi)

    training_data = []

    for document in documents:
        text = document['ided_text']
        entities = document['ref_phi']

        entry = (text, {
            'entities': entities
        })

        training_data.append(entry)

    return training_data




if __name__ == '__main__':

    all_data = create_training_data()

    with open('data/notes/ner.data', 'wb') as f:
        pickle.dump(all_data, f)

    # targets = get_targets()
    # ided_text = get_ided_text()
    #
    # documents = parse_ided_text(ided_text)
    #
    # for i, document in enumerate(documents):
    #     ided_text = document['ided_text']
    #     deid_document = scrubber.deidentify(ided_text)
    #     document["deid"] = deid_document['deid']
    #     document["phi_entries"] = deid_document['phi_entries']
    #
    #     print(document)
    #     if i > 2:
    #         break
