# Anoni

## Purpose

To make medical data accessible and advance medical research.

Healthcare stands to benefit immensely from data-driven medicine. At the same time, healthcare must protect the privacy of its patients and their sensitive data from harm. Properly de-identified data enables the benefits while minimizing risk to patients.

De-identified medical data may be used for secondary purposes (ie. research) and be shared with others, under HIPAA law. And with up to 70% [[1]](https://www.ncbi.nlm.nih.gov/pubmed/28323609) of all medical data resides in free text records: doctor's notes, nurses notes, radiology reports, etc. 

Historically, free text has been very difficult to properly de-identify. Anoni aims to make it achievable.


## Benchmarks for 2014 i2b2 De-Identification Dataset

**bert-large-uncased:** 98.17% dev F1-score (state-of-the-art)

**bert-base-uncased:** 98.12% dev F1-score

The previous state-of-the-art was 98.05% using GRU + text skeleton [[2]](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5872383/#Tab3). We're still verifying that our results are valid and comparable to the past works. We expect to see even higher performance once we fine tune the BERT large model. We will publish a whitepaper once done.

## Dataset

The i2b2 2014 de-identification dataset is the largest publically available dataset suitable for de-identification training. It contains 1,307 doctor's notes with PHI annotations. It has around 619k tokens (depending on the tokenizer), out of which about 42k tokens are PHI. There are exactly 11,893 PHI instances (PHI may contain multiple tokens).

There are many more PHI tokens than PHI instances because the WordPiece tokenizer for BERT puts all punctuation into a separate token. So, "03/12/2019" becomes a list of "03", "/", "12", "/", "2019". 1 PHI instance becomes 5 PHI tokens.

## Setting Up GPU Environment

BERT must be trained on a GPU. I personally use [Floydhub workspaces](https://docs.floydhub.com/guides/workspace/) because it's extremely simple if a bit pricey. Luckily, it only takes around 10-15 minutes to fine tune BERT base on the 16GB GPU2 (Tesla V100). The 12GB GPU takes around 1.25-1.5 hours, so it's actually cheaper to use the more expensive per hour GPU2.

APEX provides faster speeds on a CUDA-enabled GPU for BERT. Floydhub workspaces come with CUDA pre-installed, as well as all the other necessary Python libraries except [pytorch_pretrained_bert](https://github.com/huggingface/pytorch-pretrained-BERT) and [seqeval](https://github.com/chakki-works/seqeval). Run these commands from the workspace terminal:

```
git clone https://github.com/NVIDIA/apex.git
cd apex && python setup.py install && cd ..
pip install pytorch_pretrained_bert seqeval
```

If you're also going to be running the preprocessing script (ie. getting the doctor's notes in the right format for training), you're going to need a Spacy language model for sentence segmentation. Also run:

```
python -m spacy download en_core_web_md
```

The environment should now be setup to run the preprocessing and training scripts.

## Web App Demo

A live version of the de-identification prototype is [here](https://deidentify.ml/demo).

Please do not enter any actual protected health information into the website.

## Setting Up Web App Locally

Change into the directory you want to store the files, clone the repository, and change into the new directory:

```
cd /path/to/directory
git clone https://github.com/eric-yates/anoni.git
cd anoni
```

If Python >= 3.6 is not installed, download it [here](https://www.python.org/downloads/).

Create a virtual environment within the new directory:

```
pip install virtualenv
virtualenv -p python3 <your_env_name>
source activate <your_env_name>/bin
```

Install all the dependencies:

```
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

And to run the microservice locally on your computer:

`python api.py`

Now you're free to modify the source code and play around! Visit the website in your browser at:

[http://0.0.0.0:5000/](http://0.0.0.0:5000/)

## Acknowledgements

This project wouldn't be possible without [i2b2](https://www.i2b2.org/about/) for their 2014 de-identification dataset. Big thanks also to [Explosion AI](https://explosion.ai) and all its contributors for their incredible open-sourced NLP library called [Spacy](https://github.com/explosion/spaCy). Also big thanks to the folks at [HuggingFace](https://huggingface.co/) for their amazing Pytorch implementation of BERT ([pytorch_pretrained_bert](https://github.com/huggingface/pytorch-pretrained-BERT)).

