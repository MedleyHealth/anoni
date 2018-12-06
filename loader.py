import spacy
import pickle
import os


def load_model(path='', model_name='en_core_web_sm'):
    """
    Loads a Spacy Language model, called nlp by convention. Tries to load a
    custom trained model at model/. If that does not exist, it loads the small
    English model from Spacy. If that fails, it raises an error and gives
    instructions for how to add a model.

    Keyword Args:
        path: String            The relative or absolute path to a Spacy model.
        model_size: String      The name of a pre-trained Spacy model.

    Returns:
        A Spacy Langugage object called nlp by convention.
    """

    if os.path.exists(path):
        try:
            nlp = spacy.load(path)
        except:
            raise ValueError(('Found directory "{}", but the Spacy model '
            'has an incorrect format or missing files.'.format(path)))
    else:
        try:
            nlp = spacy.load(model_name)
        except:
            raise OSError(('No Spacy model available for "{}" or "{}". '
            'Download a pre-trained model by "python -m spacy download '
            'en_core_web_sm" or add a custom trained model to the current '
            'directory and call it "model".'.format(path, model_name)))

    return nlp


def load_notes(path='data/notes/id.text'):
    """
    Returns the nursing notes. Has the format:

        START_OF_RECORD=1||||1||||
        JOHN ADMITTED TO MAYO CLINIC.
        ||||END_OF_RECORD

        START_OF_RECORD=1||||2||||
        ...
    """

    if os.path.exists(path):
        try:
            with open(path, 'r') as f:
                notes = f.readlines()
        except:
            raise ValueError(('Nursing notes found at {}, but encountered an '
            'error loading the text file.'.format(path)))

    else:
        raise OSError(('Nursing notes do not exist at {}. Please download '
        'the data from "https://www.physionet.org/physiotools/deid/#data" and '
        'save "id.text" to the directory "data/notes/".'.format(path)))

    return notes


def load_phi_locations(path='data/notes/id.phi'):
    """
    Returns the locations of PHI within each nursing note. The locations are
    character offsets within each note of the form begin/begin/end offset.

    Format (tab delimited):

        Patient 1	Note 1
        23	23	42
        114	114	121
        197	197	208
        Patient 1   Note 2
        ...
        Patient 2   Note 1
        ...
    """

    if os.path.exists(path):
        try:
            with open(path, 'r') as f:
                phi_locations = f.readlines()
        except:
            raise ValueError(('PHI locations found at {}, but encountered an '
            'error loading the text file.'.format(path)))

    else:
        raise OSError(('PHI locations do not exist at {}. Please download '
        'the data from "https://www.physionet.org/physiotools/deid/#data" and '
        'save "id.phi" to the directory "data/notes/".'.format(path)))

    return phi_locations


def load_phi_phrases(path='data/notes/id-phi.phrase'):
    """
    Returns the PHI phrases. Has the format:

        PATIENT #   NOTE #   INDEX-START   INDEX_END   PHI-TYPE   PHI-PHRASE
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

    if os.path.exists(path):
        try:
            with open(path, 'r') as f:
                phi_phrases = f.readlines()
        except:
            raise ValueError(('PHI phrases found at {}, but encountered an '
            'error loading the text file.'.format(path)))

    else:
        raise OSError(('PHI phrases do not exist at {}. Please download '
        'the data from "https://www.physionet.org/physiotools/deid/#data" and '
        'save "id-phi.phrase" to the directory "data/notes/".'.format(path)))

    return phi_phrases


def load_training_data(path='data/notes/ner.data'):
    """
    Loads the training data to train the Named Entity Recognizer (NER) of a
    custom Spacy model. The "data_generation.py" file generates and saves the
    data as a binary file. Data have the format:

        TRAIN_DATA = [
            ('John admitted to Mayo Clinic ER.', {
                'entities': [(0, 4, 'PTName'), (17, 28, 'HCPName')]
            }),
            ('No PHI here.', {
                'entities': []
            })
        ]
    """

    if os.path.exists(path):
        try:
            with open(path, 'rb') as f:
                data = pickle.load(f)
        except:
            raise ValueError(('Training data found at {}, but encountered an '
            'error loading the binary file.'.format(path)))

    else:
        raise OSError(('Training data does not exist at {}. Please run '
        '"python data_generation.py" to generate the training data after '
        'saving nursing notes to the directory data/notes/.'.format(path)))

    return data
