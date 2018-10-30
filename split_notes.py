import re

def get_data():
    with open('id.text', 'r') as f:
        lines = f.readlines()

    d = []
    text = ''

    for i, line in enumerate(lines):

        if line[:16] == 'START_OF_RECORD=':
            patient, note = re.findall(r'\d+', line)

        elif line == '||||END_OF_RECORD\n':
            entry = [patient, note, text]
            d.append(entry)
            text = ''

        else:
            text += line

    return d
