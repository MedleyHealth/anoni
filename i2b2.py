import re
import scrubber


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

    Source: https://www.i2b2.org/NLP/DataSets/
    """

    path = '/Users/ericyates/Documents/Medley.nosync/deid-1.1/id.phi'

    with open(path, 'r') as f:
        targets = f.readlines()

    return targets


def get_ided_text():
    """

    """

    path = '/id.text'

    with open(path, 'r') as f:
        ided_text = f.readlines()

    return ided_text


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
            documents = append(document)
            text = ''

        else:
            text += line

    return documents


def create_document(patient_number, note_number, ided_text):
    """

    """

    document = {
        "patient_number": patient_number,
        "note_number": note_number,
        "ided_text": ided_text
    }

    return document

if __name__ == '__main__':

    targets = get_targets()
    ided_text = get_ided_text()

    documents = parse_ided_text(ided_text)

    for document in documents:
        ided_text = document['ided_text']
        deid_document = scrubber.deidentify(ided_text)
        document["deid_text"] = deid_document['deid_text']
        document["phi_indices"] = deid_document['phi_indices']
