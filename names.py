import pickle


def parse_names(path):

    with open(path) as f:
        names = [line.split()[0] for line in f]

    return set(names)


if __name__ == '__main__':

    male_names = parse_names('data/dist.male.first.txt')
    female_names = parse_names('data/dist.female.first.txt')
    # last_names = parse_names('data/dist.all.last.txt')

    with open('data/stopwords.txt') as f:
        stop_words = [line.rstrip().upper() for line in f]

    names_set = male_names | female_names #| last_names

    exceptions = ['WENT', 'TO', 'IN', 'PERSON', 'ON', 'PLENTY', 'HE', 'CAN',
                  'BE', 'OR', 'HAS', 'HOME', 'NUMBER', 'IP', 'PLEASURE', 'PAIN',
                  'BORN', 'MAN', 'DESIRE']

    for exception in exceptions:
        if exception in names_set:
            names_set.remove(exception)

    for stop_word in stop_words:
        if stop_word in names_set:
            names_set.remove(stop_word)

    with open('data/names.set', 'wb') as f:
        pickle.dump(names_set, f)
