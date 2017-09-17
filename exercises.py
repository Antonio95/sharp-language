
import signal
import random
import collections
import readline

import json
from colorama import init, Fore, Back, Style


# TODOs
# format review (limit to 99 questions/drill?)
# Revise points
# Drill options:
#    examples
#    verbose (show all translations)
# Tracking system
# Accept new answer
# Select types of exercises
# Show data
# acentos
# [, ] quitar automaticamente?
# derivative words
# puntos en material
# PHONETICS; EXERCISES: HOMOPHONES


################################################################################
# GLOBALS #
###########

MATERIAL_PATH = '/home/antonio/Desktop/cpe/python/material.json'

ACCEPT_NEW = False

LETTERS = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'

N_MODIFIED_IDIOMS = 3

N_QUESTIONS_DIGITS = 2

SCORES = {'yes': 1, 'no': 0, 'sorta': 0.5}

FEEDBACK = {
    1: Fore.CYAN + 'Correct! One point' + Fore.RESET, 
    0.5: Fore.YELLOW + 'So-so: half a point' + Fore.RESET, 
    0: Fore.RED +'Whoops, incorrect: no points' + Fore.RESET
}

CASUAL = False

# In order to always display/ask about the types in the same order
QUESTIONS = collections.OrderedDict([
    ("Vocabulary", {'ask': True}),
    ("Fill in", {'ask': True}),
    ("Phrasal verbs", {'ask': True}),
    ("Expression", {'ask': True}),
    ("Word field", {'ask': True}),
    ("Idioms", {'ask': True}),
    ("Multiple choice", {'ask': True})
])


################################################################################
# CLASSES #
###########

class Question(object):

    def ask(self, mode):
        return

    def brief(self):
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

            return SCORES[corr]

    def brief(self):
        return self.word


class FillQuestion(Question):

    def __init__(self, sentence, word):
        self.sentence = sentence
        self.word = word

    def ask(self, mode=0):

        print(Fore.YELLOW + '[*] Fill in the gap:', self.sentence, Fore.RESET)

        ans = input('    ')

        if ans == self.word:
            return 1
        else:
            print('    Correct answer:', self.word)
            return 0

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

        return SCORES[corr]

    def brief(self):
        return self.sentence


class PhrasalQuestion(Question):

    def __init__(self, exp, meanings, separable, question):
        self.verb, self.particles = exp[0], exp[1:]
        self.meanings = meanings
        self.separable = separable
        self.question = question

    def ask(self, mode=None):

        if not mode:
            mode = random.randint(0, 1)

        if mode == 0:
            print(Fore.YELLOW + '[*] Translate:', self.verb, ' '.join(self.particles), Fore.RESET)
            ans = input('    ')

            if ans in self.meanings:
                return 1
            else:
                print('    Possible meanings:', ', '.join(self.meanings))
                corr = input_loop('    Accept ' + ans + '? (yes, no, sorta): ', ['yes', 'no', 'sorta'])

                return SCORES[corr]

        elif mode == 1:
            print(Fore.YELLOW + '[*] Complete with a phrasal verb:', self.question, Fore.RESET)
            ans = input('    ').lower().split(' ')

            exp = [self.verb] + self.particles
            
            if ans == exp:
                return 1
            else:
                print('    Expected answer: ' + '/'.join(exp))
                return 0

    def brief(self):
        return self.verb + ' ' + ' '.join(self.particles)


class FieldQuestion(Question):

    def __init__(self, prompt, field):
        self.prompt = prompt
        self.field = field

    def ask(self, mode=1):

        print(Fore.YELLOW + '[*] {} ({} words stored)'.format(self.prompt, len(self.field)), Fore.RESET)

        ans = input('    Enter any number of comma-separated words: ')
        answers = ans.lower().replace(' ', '').split(',')
        right, wrong = [], []

        # taking care of potentially repeated answers
        for a in answers: 
            if a in self.field and a not in right:
                right.append(a)
            if a not in self.field and a not in wrong:
                wrong.append(a)

        print('    Expected synonyms ({}): '.format(len(self.field)), ', '.join(self.field))
        print('    Correct answers ({}): '.format(len(right)), ', '.join(right))
        print('    Wrong answers ({}): '.format(len(wrong)), ', '.join(wrong))

        s, r = len(self.field), len(right)
        
        if float(r) / s >= mode:
            return 1
        elif 2 * float(r) / s >= mode:
            return 0.5
        else:
            return 0

    def brief(self):
        return self.prompt


class IdiomQuestion(Question):

    def __init__(self, idiom, meaning):
        self.idiom = idiom
        self.meaning = meaning

    def ask(self, mode=0):

        # remove apostrophes?
        clean_idiom = self.idiom.replace("'", '')

        hint = ''.join([' ' if c == ' ' else '_' for c in clean_idiom])
        
        if len(clean_idiom) < N_MODIFIED_IDIOMS:
            raise Exception('Error: length of idiom: "{}" lower than number of characters to show ({}). Please modify your settings'.format(clean_idiom, N_MODIFIED_IDIOMS))

        modified = []

        for _ in range(N_MODIFIED_IDIOMS):
            ind = random.randint(0, len(clean_idiom) - 1)
            while clean_idiom[ind] not in LETTERS or ind in modified:
                ind = random.randint(0, len(clean_idiom) - 1)

            modified.append(ind)
        
        hint_list = list(hint)
        
        for ind in modified:
            hint_list[ind] = clean_idiom[ind]

        hint = ''.join(hint_list)

        print(Fore.YELLOW + '[*] Type in an idiom or expression which means:', self.meaning + Fore.RESET)
        input('    (Press Enter for hint when you have given it some thought)')
        print('    ' + hint)
        ans = input('    Answer: ')

        if ans.lower() == self.idiom.lower():
            return 1
        else:
            print('    Correct answer:', self.idiom)
            return 0

    def brief(self):
        return self.idiom


class MultipleChoiceQuestion(Question):

    def __init__(self, question, answers):
        self.question = question
        self.answers = answers

    def ask(self, mode=0):

        print(Fore.YELLOW + '[*]', self.question, Fore.RESET)

        right = self.answers[0]
        shuffled = list(self.answers)
        random.shuffle(shuffled)
        n = len(shuffled)

        for (i, opt) in enumerate(shuffled):
            print('    ', i + 1, ': ', opt, sep='')

        print('')

        ans = number_input_loop('    Enter the number corresponding to the right answer: ', 1, n) - 1
        
        if shuffled[ans] == right:
            return 1
        else:
            print("    Ouch, it was:", right)
            return 0
            

    def brief(self):
        return self.question


################################################################################
# METHODS #
###########

def signal_handler_casual_mode(signal, frame):
    
    global CASUAL

    CASUAL = not CASUAL    
    print('\u001b[s', '\u001b[;f', Fore.MAGENTA, 'Casual mode: ', 'ON ' if CASUAL else 'OFF', Fore.RESET, '\u001b[u', sep='', end='', flush=True)

def praise(grade):
    if 0 <= grade and grade < 40: print('Madre mia, la que ha liado pollito...')
    elif 40 <= grade and grade < 60: return 'Así se va a sacar el CPE tu prima'
    elif 60 <= grade and grade < 80: return 'Need to work on these a bit more!'
    elif 80 <= grade and grade < 90: return 'Good job! Practice makes perfect tho'
    elif 90 <= grade and grade < 100: return 'Amazing, you pompous piece of... knowledge'
    elif 100 == grade: return 'Flawless! Cleaner than a Norwegian spa. Keep it up!'
    else: return 'Whoops! Invalid grade: ' + str(grade)


def load():

    global QUESTIONS

    with open(MATERIAL_PATH, 'r') as file:
        material = json.load(file)

        QUESTIONS["Vocabulary"]["exercises"] = [VocabularyQuestion(*v) for v in material['vocabulary']]
        QUESTIONS["Fill in"]["exercises"] = [FillQuestion(*f) for f in material['fill']]
        QUESTIONS["Phrasal verbs"]["exercises"] = [PhrasalQuestion(*p) for p in material['phrasal']]
        QUESTIONS["Expression"]["exercises"] = [ExpressionQuestion(*e) for e in material['expression']]
        QUESTIONS["Word field"]["exercises"] = [FieldQuestion(*s) for s in material['field']]
        QUESTIONS["Idioms"]["exercises"] = [IdiomQuestion(*i) for i in material['idiom']]
        QUESTIONS["Multiple choice"]["exercises"] = [MultipleChoiceQuestion(*c) for c in material['choice']]


def erase(nl=True):
    print('\u001b[2J\u001b[;f', end='\n' if nl else '')


def input_loop(prompt, expected):
    
    ans = None
    
    # no do-while in python </3
    while ans not in expected:
        ans = input(prompt).lower()

    # TODO give feedback?

    return ans


def number_input_loop(prompt, v_min, v_max):
    
    # TODO give feedback?

    ans = 0

    # Awkward flag due to the lack of do-while and potentially unbounded min/max
    enter = True

    while enter == True or ans < v_min or ans > v_max:
        ans = input(prompt)
        
        try:
            ans = int(ans)
            enter = False
        except:
            enter = True
            continue

    return ans


def drill(n=10, review=False):

    global QUESTIONS

    erase()

    print('Current settings:', Fore.YELLOW,
        '\n    * number of questions: {}'
        '\n    * review afterwards: {}\n'.format(n, review), Fore.RESET)

    settings = input_loop('Keep or change these settings? [keep, change]: ', ['keep', 'k', 'change', 'c'])

    if 'change' == settings or 'c' == settings:
        n = number_input_loop(Fore.YELLOW + '    * Enter the number of questions (1 to {}): '.format(10**N_QUESTIONS_DIGITS - 1) + Fore.RESET, 1, 10**N_QUESTIONS_DIGITS - 1)
        review = input_loop(Fore.YELLOW + '    * Give the option to review at the end? [yes, no]: ' + Fore.RESET, ['yes', 'no']) == 'yes'
        print(Fore.YELLOW + '    * Select which types of questions you want [yes, no]:' + Fore.RESET)
        for typ, val in QUESTIONS.items():
            val['ask'] = input_loop(Fore.YELLOW + ' ' * 8 + '- ' + typ + ': ' + Fore.RESET, ['yes', 'no']) == 'yes'

    erase()

    questions = []

    for val in QUESTIONS.values():
        if val['ask']:
            questions += val['exercises']

    if len(questions) < n:
        print(Fore.YELLOW + '/!\\ Number of requested questions ({}) larger than that of available ones ({})'
                            '\n    Drill reduced to {} questions'.format(n, len(questions), n), Fore.RESET + '\n')
        n = len(questions)

    selected_q = random.sample(questions, n)
    
    score = 0

    for q in selected_q:
        res = q.ask()
        print('    ->', FEEDBACK[res], end='\n\n')
        
        score += res
        grade = 100.0 * score / n
    
    print('Final score: {} out of {} ({}%). {}'.format(score, n, int(grade), praise(grade)))

    if review:

        ans = input_loop('Move on to review? (yes, no): ', ['yes', 'no'])
        if 'no' == ans:
            return

        erase()

        print('Score: {} out of {} ({}%)'.format(score, n, int(grade)), end='\n\n')
        print('In order to review, enter a sentence involving each of the previous questions\n'
              'If at some point you cannot remember any more questions, enter an empty line to finish')

        for i in range(n):
            if '' == input(Fore.YELLOW + '{:4}'.format(str(i + 1) + ':') + Fore.RESET):
                break

        print('\nThe concepts featured in the questions were: ')
        print('\n'.join([Fore.YELLOW + '{:4}'.format(str(i + 1) + '.') + Fore.RESET + q.brief() for (i, q) in enumerate(selected_q)]))


################################################################################
# MAIN #
########

init()
load()
signal.signal(signal.SIGTSTP, signal_handler_casual_mode)

erase()

print('Sharp Language v0.6, by Antonio Mejías', Fore.BLUE, '\nhttps://github.com/Antonio95/', Fore.RESET)
print('\nNumber of items stored:')
for typ, val in QUESTIONS.items():
    print('    ' + typ, ': ', len(val['exercises']), sep='')
print('    * Total:', sum([len(v['exercises']) for v in QUESTIONS.values()]))
print('\nUse ' + Fore.YELLOW + 'ctrl+z ' + Fore.RESET + 'at any time to switch casual mode on or off')
print('Use ' + Fore.RED + 'ctrl+c ' + Fore.RESET + 'at any time to quit')

input('\n(Press Enter to continue)')

drill(10, review=True)

input('\n(Press Enter to finish)')

erase(nl=False)
