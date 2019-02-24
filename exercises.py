
import signal
import random
import collections
import readline
import shutil
import os
import json

from colorama import init, Fore, Back, Style
import numpy


# TODOs
#     DONE Select types of exercises
#     DONE records (tracked)
#     DONE Select types of exercises
#     use records
#     maybe the code can be improved (particularly at the beginning of drill() with ordered dictionaries
#     full installation & use guide
#     performance: select the questions Before loading
#     Done Phonetics
#     exercise: HOMOPHONES
#     format review (limit to 99 questions/drill?)
#     Revise points
#     Drill options
#         examples
#         verbose (show all translations)
#     Accept new answer
#     Show data
#     revisar acentos
#     [, ] quitar automaticamente?
#     derivative words
#     puntos en material
#     correct: word field, answer with spaces: it then appears without them
#     exercise: match?


# Onthos: choice of exercises to ask
# * The current formula for the weighted probability of an item being asked is 
#   T/(1 + C^2), where C is the number of previous correct answers and T is the total
#   number of times it has been asked before (see exc. below)
#   note that "sorta" answers count as 0.5 correct answers
# * If an item is added to the material, the loading of the application will 
#   include it in the records file. Its record will be empty and, as an 
#   exception, its weight will be 2, which is equivalent to having been asked
#   twice with 0 correct answers


################################################################################
# GLOBALS #
###########


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MATERIAL_PATH = os.path.join(BASE_DIR, 'material.json')
RECORDS_PATH = os.path.join(BASE_DIR, 'records.json')

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
    ("Expression", {'ask': True}),
    ("Phrasal verbs", {'ask': True}),
    ("Word field", {'ask': True}),
    ("Idioms", {'ask': True}),
    ("Multiple choice", {'ask': True}),
    ("Pronunciation", {'ask': True})

])

INITIAL_WEIGHT = 2


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
        answers = [a.lstrip().rstrip() for a in ans.lower().split(',')]
        right, wrong = [], []

        # taking care of potentially repeated answers
        for a in answers: 
            if a in self.field and a not in right:
                right.append(a)
            if a not in self.field and a not in wrong:
                wrong.append(a)

        missing = [a for a in self.field if a not in answers]

        print('    Correct answers ({}): '.format(len(right)), ', '.join(right))
        print('    Missing answers ({}): '.format(len(missing)), ', '.join(missing))
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

        hint = ''.join([' ' if c in [' ', '?', '!'] else '_' for c in clean_idiom])
        
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
        return self.question + '-> ' + self.answers[0]


class PronunciationQuestion(Question):

    def __init__(self, word, example, alternatives):
        self.word = word
        self.example = example
        self.alternatives = alternatives

    def ask(self, mode=0):

        print(Fore.YELLOW + '[*] Select the correct pronunciation for the capitalised syllable: ' , self.word, Fore.RESET)

        right = self.alternatives[0]
        shuffled = list(self.alternatives)
        random.shuffle(shuffled)
        n = len(shuffled)

        for (i, opt) in enumerate(shuffled):
            print('    ', i + 1, ': ', opt, sep='')

        print('')

        ans = number_input_loop('    Enter the number corresponding to the right answer: ', 1, n) - 1
        
        if shuffled[ans] == right:
            outcome = 1
        else:
            print("    Ouch, it was:", right)
            outcome = 0

        print(Fore.YELLOW + '    You can practise by saying the following sentence out loud:\n    ' + self.example, Fore.RESET)            
        return outcome 


    def brief(self):
        return self.word + ': ' + self.alternatives[0]


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

    print ('Loading...')

    with open(RECORDS_PATH, 'r') as rf:
        records = json.load(rf)
    
        with open(MATERIAL_PATH, 'r') as mf:
            material = json.load(mf)

            for item in [inner for outer in material.values() for inner in outer.keys()]:
                if item not in records:
                    records[item] = [0, 0, INITIAL_WEIGHT]
                    print('Added item', item, 'to records')

    with open(RECORDS_PATH, 'w') as rf:
        json.dump(records, rf, indent='    ')

    QUESTIONS["Vocabulary"]["exercises"] = dict([(k, (v, records[k])) for k, v in material['vocabulary'].items()])
    QUESTIONS["Fill in"]["exercises"] = dict([(k, (v, records[k])) for k, v in material['fill'].items()])
    QUESTIONS["Phrasal verbs"]["exercises"] = dict([(k, (v, records[k])) for k, v in material['phrasal'].items()])
    QUESTIONS["Expression"]["exercises"] = dict([(k, (v, records[k])) for k, v in material['expression'].items()])
    QUESTIONS["Word field"]["exercises"] = dict([(k, (v, records[k])) for k, v in material['field'].items()])
    QUESTIONS["Idioms"]["exercises"] = dict([(k, (v, records[k])) for k, v in material['idiom'].items()])
    QUESTIONS["Multiple choice"]["exercises"] = dict([(k, (v, records[k])) for k, v in material['choice'].items()])
    QUESTIONS["Pronunciation"]["exercises"] = dict([(k, (v, records[k])) for k, v in material['pronunciation'].items()])

    print ('Loaded')    


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
        n = number_input_loop(Fore.YELLOW + '    * Enter the number of questions (1 to {}): '.format(10 ** N_QUESTIONS_DIGITS - 1) + Fore.RESET, 1, 10**N_QUESTIONS_DIGITS - 1)
        review = input_loop(Fore.YELLOW + '    * Give the option to review at the end? [yes, no]: ' + Fore.RESET, ['yes', 'no']) == 'yes'
        print(Fore.YELLOW + '    * Select which types of questions you want [yes, no]:' + Fore.RESET)
        for typ, val in QUESTIONS.items():
            val['ask'] = input_loop(Fore.YELLOW + ' ' * 8 + '- ' + typ + ': ' + Fore.RESET, ['yes', 'no']) == 'yes'

    erase()

    questions = {}

    for val in QUESTIONS.values():
        if val['ask']:
            questions.update(val['exercises'])

    if len(questions) < n:
        print(Fore.YELLOW + '/!\\ Number of requested questions ({}) larger than that of available ones ({})'
                            '\n    Drill reduced to {} questions'.format(n, len(questions), n), Fore.RESET + '\n')
        n = len(questions)

    id_to_class = {
        '1': VocabularyQuestion,
        '2': FillQuestion,
        '3': PhrasalQuestion,
        '4': ExpressionQuestion,
        '5': FieldQuestion,
        '6': IdiomQuestion,
        '7': MultipleChoiceQuestion,
        '8': PronunciationQuestion,
    }

    sorted_ids = list(questions.keys())
    sorted_weights = [questions[i][1][2] for i in sorted_ids]
    total_weight = sum(sorted_weights)
    sorted_weights = list(map(lambda x: x * 1.0 / total_weight, sorted_weights))
    selected_ids = numpy.random.choice(sorted_ids, size=n, replace=False, p=sorted_weights)
    selected_q = [id_to_class[i[0]](*questions[i][0]) for i in selected_ids]
    
    score, results = 0, []

    for q in selected_q:
        res = q.ask()
        print('    ->', FEEDBACK[res], end='\n\n')
        
        score += res
        results.append(res)
    
    grade = 100.0 * score / n
    
    print('Final score: {} out of {} ({}%). {}'.format(score, n, int(grade), praise(grade)))

    if review:

        ans = input_loop('Move on to review? (yes, no): ', ['yes', 'no'])
        if 'yes' == ans:
                
            erase()

            print('Score: {} out of {} ({}%)'.format(score, n, int(grade)), end='\n\n')
            print('In order to review, enter a sentence involving each of the previous questions\n'
                  'If at some point you cannot remember any more questions, enter an empty line to finish')

            for i in range(n):
                if '' == input(Fore.YELLOW + '{:4}'.format(str(i + 1) + ':') + Fore.RESET):
                    break

            print('\nThe concepts featured in the questions were: ')
            print('\n'.join([Fore.YELLOW + '{:4}'.format(str(i + 1) + '.') + Fore.RESET + q.brief() for (i, q) in enumerate(selected_q)]))

    if not CASUAL:

        print('Saving records, please do not exit now...')

        with open(RECORDS_PATH, 'r') as rf:
            records = json.load(rf)
        
            for n, i  in enumerate(selected_ids):
                previous = records[i]
                previous[0] += results[n]
                previous[1] += 1
                previous[2] = previous[1] * 1.0 / (1 + previous[0] ** 2)

        with open(RECORDS_PATH, 'w') as rf:
            json.dump(records, rf, indent='    ')

        print('Records saved')


def reset_records(filename=RECORDS_PATH):

    ans = input_loop('Are you sure you want to reset the answers record for ' + Fore.CYAN + filename + Fore.RESET + '? (yes, no): ', ['yes', 'y', 'no', 'n'])

    if ans in ['yes', 'y']:

        with open(filename, 'r') as file:
            questions = json.load(file)

            for k in questions.keys():
                questions[k] = [0, 0, INITIAL_WEIGHT]

        with open(filename, 'w') as file:
            json.dump(questions, file, indent='    ')

        print('Record reset successful')

    else:
        print('Record reset aborted')


def backup_records(target, source=RECORDS_PATH):

    ans = input_loop('Are you sure you want to backup the records from ' + Fore.CYAN + source + Fore.RESET + ' into ' + Fore.CYAN + target + Fore.RESET + '? (yes, no): ', ['yes', 'y', 'no', 'n'])

    if ans in ['yes', 'y']:
        shutil.copyfile(source, target)
        print('Record backup successful')
    else:
        print('Record backup aborted')


################################################################################
# MAIN #
########

init()
load()
signal.signal(signal.SIGTSTP, signal_handler_casual_mode)

erase()

print('Sharp Language v0.7.1, by Antonio Mejías', Fore.BLUE, '\nhttps://github.com/Antonio95/', Fore.RESET)
print('\nNumber of items stored:')
for typ, val in QUESTIONS.items():
    print('    ' + typ, ': ', len(val['exercises']), sep='')
print('    * Total:', sum([len(v['exercises']) for v in QUESTIONS.values()]))
print('\nUse ' + Fore.YELLOW + 'ctrl+z ' + Fore.RESET + 'at any time to switch casual mode on or off')
print('Use ' + Fore.RED + 'ctrl+c ' + Fore.RESET + 'at any time to quit')

input('\n(Press Enter to continue)')

drill(15, review=True)

input('\n(Press Enter to finish)')

erase(nl=False)

# reset_records()
