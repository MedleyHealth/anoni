# Anoni

## Purpose

To make medical data accessible and advance medical research.

Healthcare stands to benefit immensely from data-driven medicine. At the same time, healthcare must protect the privacy of its patients and their sensitive data from harm. Properly de-identified data enables the benefits while minimizing risk to patients.

De-identified medical data may be used for secondary purposes (ie. research) and be shared with others, under HIPAA law. And over 80% of all medical data resides in free text records: doctor's notes, nurses notes, radiology reports, etc. 

Historically, free text has been very difficult to properly de-identify. Anoni aims to make it achievable.

## Demo

A live version of the de-identification prototype is [here](https://deidentify.ml/demo).

Please do not enter any actual protected health information into the website.

## Setting Up Locally

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

Big thanks to [Explosion AI](https://explosion.ai) for their incredible NLP library called Spacy. 

