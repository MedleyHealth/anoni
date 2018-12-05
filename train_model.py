"""
Training spaCy's named entity recognizer (NER) on the Physio-Net gold standard
corpus of 2,434 nursing notes.

Modified from the example NER training script provided here:

    https://spacy.io/usage/training#section-ner

For more details, see the documentation:

    Training: https://spacy.io/usage/training
    NER: https://spacy.io/usage/linguistic-features#named-entities

Training data must be in the format below:

    TRAIN_DATA = [
        ('John admitted to Mayo Clinic ER.', {
            'entities': [(0, 4, 'PTName'), (17, 28, 'HCPName')]
        }),
        ('No PHI here.', {
            'entities': []
        })
    ]

Compatible with: spaCy v2.0.0+
"""

from __future__ import unicode_literals, print_function

import plac
import random
import spacy
import pickle
import os

from pathlib import Path
from spacy.util import minibatch, compounding
from data_generation import create_training_data


data_path = 'data/notes/ner.data'

### If NER data does not exist, create and save it to a binary file
if not os.path.exists(data_path):
    NER_DATA = create_training_data()

    with open(data_path, 'wb') as f:
        pickle.dump(NER_DATA, f)

### If NER data exists, load it from a binary file
else:
    with open(data_path, 'rb') as f:
        NER_DATA = pickle.load(f)


@plac.annotations(
    model=('Model name. Default "en_core_web_sm" model.', 'option', 'm', str),
    output_dir=('Output directory to save model.', 'option', 'o', Path),
    n_iter=('Number of training iterations.', 'option', 'n', int),
    train_size=('Proportion of training data.', 'option', 's', float))
def main(model='en_core_web_sm', output_dir=None, n_iter=100, train_size=0.8):
    """
    Load the model, set up the pipeline and train the entity recognizer.
    """

    ### Split the NER data into train and test sets
    N = len(NER_DATA)
    cutoff = int(N * train_size)
    TRAIN_DATA = NER_DATA[:cutoff]
    TEST_DATA = NER_DATA[cutoff:]

    ### Load a pre-trained model
    nlp = spacy.load(model)  # load existing spaCy model
    print('Loaded model "%s"' % model)

    ### Remove the pre-trained named entity recognizer, if present
    if 'ner' in nlp.pipe_names:
        nlp.remove_pipe('ner')

    ### Add a blank named entity recognizer
    ner = nlp.create_pipe('ner')
    nlp.add_pipe(ner, last=True)

    ### Add labels
    for _, annotations in TRAIN_DATA:
        for ent in annotations.get('entities'):
            ner.add_label(ent[2])

    ### Only train the NER by disabling other pipes
    pipes_to_disable = [pipe for pipe in nlp.pipe_names if pipe != 'ner']
    with nlp.disable_pipes(*pipes_to_disable):
        print('\nBEGIN TRAINING \n')
        optimizer = nlp.begin_training()
        for itn in range(n_iter):
            random.shuffle(TRAIN_DATA)
            losses = {}
            ### Batch up the examples using spaCy's minibatch
            batches = minibatch(TRAIN_DATA, size=compounding(4., 32., 1.001))
            for batch in batches:
                texts, annotations = zip(*batch)
                nlp.update(
                    texts,  # batch of texts
                    annotations,  # batch of annotations
                    drop=0.5,  # dropout - make it harder to memorise data
                    sgd=optimizer,  # callable to update weights
                    losses=losses)
            print('Losses @ i={}: {}'.format(itn, losses))

    ### Print statements to make sure the new model works
    test_model(nlp, TRAIN_DATA, 'TRAINING')
    test_model(nlp, TEST_DATA, 'TESTING')

    ### Save model to output directory
    if output_dir is not None:
        output_dir = Path(output_dir)
        if not output_dir.exists():
            output_dir.mkdir()
        nlp.to_disk(output_dir)
        print('\nSaved model to', output_dir)

        ### Test the saved model to make sure it saved correctly
        try:
            nlp2 = spacy.load(output_dir)
            doc = nlp2("It's a test, not a trap!")
        except:
            raise ValueError('Failed to load newly saved model.')


def test_model(nlp, data, msg):
    """

    """

    text = data[0][0]
    doc = nlp(text)

    print('\n', msg)
    print('\n', text)
    print('\nEntities', [(ent.text, ent.label_) for ent in doc.ents])


if __name__ == '__main__':
    plac.call(main)
