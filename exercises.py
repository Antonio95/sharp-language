
import random
import readline
import json
from colorama import init, Fore, Back, Style

# TODOs
# Revise points
# Rename synonyms
# Mode of synonyms
# Drill options:
#    review
#    examples
#    verbose (show all translations)
# Tracking system

################################################################################
# GLOBALS #
###########

MATERIAL_PATH = '/home/antonio/Desktop/cpe/python/material.json'

ACCEPT_NEW = False


_q_vocabulary, _q_fill, _q_expression, _q_synonyms = [], [], [], []

_scores = {'yes': 1, 'no': 0, 'sorta': 0.5}

_feedback = {
    1: Fore.CYAN + 'Correct! One point' + Fore.RESET, 
    0.5: Fore.YELLOW + 'So-so: half a point' + Fore.RESET, 
    0: Fore.RED +'Whoops, incorrect: no points' + Fore.RESET
}


################################################################################
# CLASSES #
###########

class Question(object):

    def ask(mode):
        return


class VocabularyQuestion(Question):

    def __init__(self, word, meanings):
        self.word = word
        self.meanings = meanings

    def ask(self, mode=0):

        print(Fore.YELLOW + '[*] Translate:', self.word, Fore.RESET)

        ans = input('    ')

        if ans in self.meanings:
            return 1
        else:
            print('    Possible meanings:', ', '.join(self.meanings))
            corr = input_loop('    Accept ' + ans + '? (yes, no, sorta): ', ['yes', 'no', 'sorta'])

            return _scores[corr]

    def brief(self):
        return self.word


class FillQuestion(Question):

    def __init__(self, sentence, word):
        self.sentence = sentence
        self.word = word

    def ask(self, mode=0):

        print(Fore.YELLOW + '[*] Fill in the gap:', self.sentence, Fore.RESET)

        ans = input('    ')

        print('    Correct answer:', self.word)

        return 1 if ans == self.word else 0

    def brief(self):
        return self.word


class ExpressionQuestion(Question):

    def __init__(self, sentence, meaning):
        self.sentence = sentence
        self.meaning = meaning

    def ask(self, mode=0):

        print(Fore.YELLOW + '[*] Translate:', self.meaning, Fore.RESET)

        ans = input('    ')

        print('    Suggested translation:', self.sentence)

        corr = input_loop('    Accept answer? (yes, no, sorta): ', ['yes', 'no', 'sorta'])

        return _scores[corr]

    def brief(self):
        return self.sentence


class SynonymsQuestion(Question):

    def __init__(self, word, synonyms):
        self.word = word
        self.synonyms = synonyms

    def ask(self, mode=1):

        print(Fore.YELLOW + '[*] Semantic field of: {} ({} words stored)'.format(self.word, len(self.synonyms)), Fore.RESET)

        ans = input('    Enter any number of comma-separated words: ')
        answers = ans.lower().replace(' ', '').split(',')
        right, wrong = [], []

        # taking care of potentially repeated answers
        for a in answers: 
            if a in self.synonyms and a not in right:
                right.append(a)
            if a not in self.synonyms and a not in wrong:
                wrong.append(a)

        print('    Expected synonyms ({}): '.format(len(self.synonyms)), ', '.join(self.synonyms))
        print('    Correct answers ({}): '.format(len(right)), ', '.join(right))
        print('    Wrong answers ({}): '.format(len(wrong)), ', '.join(wrong))

        s, r = len(self.synonyms), len(right)
        
        if float(r) / s >= mode:
            return 1
        elif 2 * float(r) / s >= mode:
            return 0.5
        else:
            return 0

    def brief(self):
        return self.word


################################################################################
# METHODS #
###########

def praise(grade):
    if 0 <= grade and grade < 40: print('Madre mia, la que ha liado pollito...')
    elif 40 <= grade and grade < 60: return 'Asi va a sacar el CPE tu prima.'
    elif 60 <= grade and grade < 80: return 'Need to work on these a bit more!'
    elif 80 <= grade and grade < 90: return 'Good job! Practice makes perfect tho'
    elif 90 <= grade and grade < 100: return 'Amazing, you pompous piece of... knowledge'
    elif 100 == grade: return 'Flawless! Cleaner than a Norwegian spa. Keep it up!'
    else: return 'Whoops! Invalid grade: ' + str(grade)


def load():

    global _q_vocabulary, _q_fill, _q_expression, _q_synonyms

    with open(MATERIAL_PATH, 'r') as file:
        material = json.load(file)

        _q_vocabulary = [VocabularyQuestion(v[0], v[1]) for v in material['vocabulary']]
        _q_fill = [FillQuestion(f[0], f[1]) for f in material['fill']]
        _q_expression = [ExpressionQuestion(e[0], e[1]) for e in material['expression']]
        _q_synonyms = [SynonymsQuestion(s[0], s[1]) for s in material['synonyms']]


def erase():
    print('\u001b[2J\u001b[;H')


def input_loop(prompt, expected):
    
    ans = ''
    
    # no do-while in python </3
    while ans not in expected:
        ans = input(prompt).lower()

    return ans


def drill(n=10, review=False):
    
    # print('Current setting:'
    #     '\n    number of questions: {}'
    #     '\n    review afterwards: {}'.format(n, review))

    # ')

    # controlar tamanyo
    selected_q = random.sample(_q_vocabulary + _q_fill + _q_expression + _q_synonyms, n)

    score = 0

    for q in selected_q:
        res = q.ask()
        print('    ->', _feedback[res], end='\n\n')
        
        score += res
        grade = 100.0 * score / n
    
    print('Final score: {} out of {} ({}%). {}\n'.format(score, n, int(grade), praise(grade)))

    if review:

        ans = input_loop('Move on to review? (yes, no): ', ['yes', 'no'])
        if 'no' == ans:
            return

        erase()

        print('Score: {} out of {} ({}%)'.format(score, n, int(grade)), end='\n\n')
        print('In order to review, enter a sentence involving each of the previous questions\n'
            'If at some point you cannot remember any more questions, press Enter twice')

        for i in range(n):
            new = input(str(i + 1) + ': ')
            if '' == new and '' == old:
                break
            old = new

        print('\nThe concepts featured in the exercises were: ')
        print('\n'.join([str(i + 1) + '. ' + q.brief() for q in selected_q]))


init()

load()

drill(5, review=True)

print('\n')
