############# Import Libraries #############
from pprint import pprint
import pandas as pd
import nltk
from nltk.tokenize import RegexpTokenizer
import numpy as np
import matplotlib.pyplot as plt
import contractions
import os
import json
import csv
import numpy as np
import math
############# Define Paths #############
ordered_vocab_path = os.path.abspath('.')
ordered_vocab_json_path = os.path.join(ordered_vocab_path, "vocab_order2.json")
train_pre_path = os.path.join(ordered_vocab_path, "training_pre_sentences.npy")
train_hyp_path = os.path.join(ordered_vocab_path, "training_hyp_sentences.npy")
train_label_path = os.path.join(ordered_vocab_path, "training_label.npy")
test_label_path = os.path.join(ordered_vocab_path, "test_label.npy")
test_pre_path = os.path.join(ordered_vocab_path, "test_pre_sentences.npy")
test_hyp_path = os.path.join(ordered_vocab_path, "test_hyp_sentences.npy")

####### Import Training/Testing Data #######

training_set = pd.read_csv('train.csv')
testing_set = pd.read_csv('test.csv')
testing_label = pd.read_csv('sample_submission.csv')


######## Filter for English Language #######

training_set = training_set.loc[training_set['lang_abv'] == 'en']
testing_label =  testing_label.loc[testing_set['lang_abv'] == 'en']
testing_set = testing_set.loc[testing_set['lang_abv'] == 'en']

####### Extract Sentecnces and Labels ######

trainingSet_sent1 = training_set.iloc[:,1]
trainingSet_sent2 = training_set.iloc[:,2]
trainingSetLabel = training_set.iloc[:,5]
trainingSet_premise = trainingSet_sent1.to_numpy(dtype = 'str')
trainingSet_hypothesis = trainingSet_sent2.to_numpy(dtype = 'str')
trainingSet_label = trainingSetLabel.to_numpy(dtype = 'int')

testingSet_sent1 = testing_set.iloc[:,1]
testingSet_sent2 = testing_set.iloc[:,2]
testingSetLabel  = testing_label.iloc[:,1]
testingSet_premise = testingSet_sent1.to_numpy(dtype = 'str')
testingSet_hypothesis = testingSet_sent2.to_numpy(dtype = 'str')
testingSet_label = testingSetLabel.to_numpy(dtype = 'int')

####### Standardize Sentences by lowering all words ######

trainingSet_premise_lower = np.char.lower(trainingSet_premise)
trainingSet_hypothesis_lower = np.char.lower(trainingSet_hypothesis)

testingSet_premise_lower = np.char.lower(testingSet_premise)
testingSet_hyp_lower = np.char.lower(testingSet_hypothesis)

####### Remove contractions and puncutation from all sentences ######

expanded_words = []
remove_contractions = []
new_words_pre = []
new_words_hyp = []
list_of_sent = []
list_of_sents = []
tokenizer = nltk.RegexpTokenizer(r"\w+")
for w in range(len(trainingSet_premise_lower)):
    remove_contractions = contractions.fix(trainingSet_premise_lower[w])
    new_words_pre.append(tokenizer.tokenize(str(remove_contractions)))
    list_of_sent.append(' '.join(new_words_pre[w]))
for w in range(len(trainingSet_hypothesis_lower)):    
    remove_contractions = contractions.fix(trainingSet_hypothesis_lower[w])
    new_words_hyp.append(tokenizer.tokenize(str(remove_contractions)))
    list_of_sents.append(' '.join(new_words_hyp[w]))

test_words_pre = []
test_words_hyp = []
testing_for_hyp = []
testing_for_pre = []
for w in range(len(testingSet_premise_lower)):
    remove_contractions = contractions.fix(testingSet_premise_lower[w])
    test_words_pre.append(tokenizer.tokenize(str(remove_contractions)))
    testing_for_pre.append(' '.join(test_words_pre[w]))
for w in range(len(testingSet_hyp_lower)):
    remove_contractions = contractions.fix(testingSet_hyp_lower[w])
    test_words_hyp.append(tokenizer.tokenize(str(remove_contractions)))
    testing_for_hyp.append(' '.join(test_words_hyp[w]))

####### Create a dictiontionary of words ######
new_words_total = new_words_pre + new_words_hyp
Dictionary_rep = [val for sublist in new_words_total for val in sublist]

# pruning vocab
from collections import Counter
c = Counter(Dictionary_rep)

with open("counter.json", "w") as f:
        json.dump(c, f)

#open the file where the Enums are stored.
with open('counter.json') as json_file1:
    data1 = json.load(json_file1)

#print(max(data1.values())) #outputs "the" : 12552
#total_count = len(data1) #outputs number of pairs : 12458

#divide the counts into incremental ranges of 5 or whatever is in interval
#add a list of dictionaries containing all the words&counts separated by their frequncy range
ranges_dict = {}
interval = 5

for key, val in data1.items():
    interval_place = math.ceil(val / interval)
    if interval_place in ranges_dict:
        ranges_dict[interval_place].append({key : val})
    else:
        ranges_dict[interval_place] = [{key : val}]

#make a list of all the range container sizes
size_of_ranges = []
for key, val in ranges_dict.items():
    size_of_ranges.append(len(ranges_dict[key]))

#Setting up the plotting
#x: ranges of counts , y: how many words fall into the ranges
width = 1
barlist = plt.bar(ranges_dict.keys(), size_of_ranges, width, color='g', align="center")
plt.title('Pre Truncate')
plt.ylabel('Frequnecy ')
plt.xlabel('Ranges of ' + str(interval))

#plt.show()

"""
#set every other bar to red for visual assessment
for i in range(len(barlist)):
    if (i % 2):
        barlist[i].set_color('r')
#outputs all of the original input data counts on one graph
#plt.plot(data1.keys(),data1.values(), width, color='r')
"""


#remove the word ranges
acceptable_range = 10

vocabulary_dict_ranges = {}
for key, val in ranges_dict.copy().items():
    if key >= acceptable_range:
        vocabulary_dict_ranges[key] = val


#make a list of all the range container sizes
size_of_ranges = []
for key, val in vocabulary_dict_ranges.items():
    size_of_ranges.append(len(vocabulary_dict_ranges[key]))

#Setting up the plotting
#x: ranges of counts , y: how many words fall into the ranges
width = 1
barlist = plt.bar(vocabulary_dict_ranges.keys(), size_of_ranges, width, color='r', align="center")
plt.title('Post Truncate'+ str(acceptable_range))
plt.ylabel('Frequnecy ')
plt.xlabel('Ranges of ' + str(interval))

#plt.show()

#save vocab sorted by ranges
with open("vocabulary_dict_ranges.json", "w") as f:
        json.dump(vocabulary_dict_ranges, f)


# save just a list of the words in the vocabulary alone
vocabulary_dict = {}
for key, val in vocabulary_dict_ranges.items():
    for i in range(len(vocabulary_dict_ranges[key])):
        for sub_key, sub_val in vocabulary_dict_ranges[key][i].items():
            vocabulary_dict[sub_key] = sub_val

#print(len(vocabulary_list))

with open("vocabulary_dic.json", "w") as f:
        json.dump(vocabulary_dict, f)
        
#takes the output dictionary of truncater 
with open('./vocabulary_dic.json') as json_file1:
    vocab_truncated = json.load(json_file1)

working_vocab = set(vocab_truncated)

# adding start, stop, unknown tokens
working_vocab.add("<s>")
working_vocab.add("</s>")
working_vocab.add("<unk>")
working_vocab.add("<pad>")
#print(working_vocab)


enum_val = []
enum_str = []
# get order of vocab and map vocab -> index in order
vocab_order = {w: i for i,w in enumerate(working_vocab)}

if os.path.exists(ordered_vocab_json_path):
    with open(ordered_vocab_json_path, "r") as f:
        vocab_order = json.load(f)
    print('loaded vocab')
else:
    with open(ordered_vocab_json_path, "w") as f:
        json.dump(vocab_order, f)

working_training_pre_text = [[vocab_order.get("<s>")] + [vocab_order.get(w, vocab_order.get("<unk>")) for w in s.split()] + [vocab_order.get("</s>")] for s in list_of_sent]
working_training_hyp_text = [[vocab_order.get("<s>")] + [vocab_order.get(w, vocab_order.get("<unk>")) for w in s.split()] + [vocab_order.get("</s>")] for s in list_of_sents]
working_testing_pre_text = [[vocab_order.get("<s>")] + [vocab_order.get(w, vocab_order.get("<unk>")) for w in s.split()] + [vocab_order.get("</s>")] for s in testing_for_pre]
working_testing_hyp_text = [[vocab_order.get("<s>")] + [vocab_order.get(w, vocab_order.get("<unk>")) for w in s.split()] + [vocab_order.get("</s>")] for s in testing_for_hyp]

all_sent = working_training_pre_text + working_training_hyp_text
# pad sentences
sentence_lengths = [len(s) for s in all_sent]

max_len = max(sentence_lengths)
text_matrix = np.full((len(working_training_pre_text), max_len), vocab_order["<pad>"], dtype=int)
for line_idx, line in enumerate(working_training_pre_text):
    line_length: int = len(line)

    if line_length > max_len:
        # truncate line
        # chop off from beginning
        text_matrix[line_idx, :] = line[max_len-line_length:] # truncate the begnning of the senetence

    elif line_length < max_len:
        # pad case....the pad tokens are already set, but we need to overwrite the correct values
        # in text_matrix[line_idx]

        text_matrix[line_idx, 0:line_length] = line

    else:
        text_matrix[line_idx, :] = line
        
np.save(train_pre_path, text_matrix)

text_matrix = np.full((len(working_training_hyp_text), max_len), vocab_order["<pad>"], dtype=int)
for line_idx, line in enumerate(working_training_hyp_text):
    line_length: int = len(line)

    if line_length > max_len:
        # truncate line
        # chop off from beginning
        text_matrix[line_idx, :] = line[max_len-line_length:] # truncate the begnning of the senetence

    elif line_length < max_len:
        # pad case....the pad tokens are already set, but we need to overwrite the correct values
        # in text_matrix[line_idx]

        text_matrix[line_idx, 0:line_length] = line

    else:
        text_matrix[line_idx, :] = line
        
np.save(train_hyp_path, text_matrix)

text_matrix = np.full((len(working_testing_hyp_text), max_len), vocab_order["<pad>"], dtype=int)
for line_idx, line in enumerate(working_testing_hyp_text):
    line_length: int = len(line)

    if line_length > max_len:
        # truncate line
        # chop off from beginning
        text_matrix[line_idx, :] = line[max_len-line_length:] # truncate the begnning of the senetence

    elif line_length < max_len:
        # pad case....the pad tokens are already set, but we need to overwrite the correct values
        # in text_matrix[line_idx]

        text_matrix[line_idx, 0:line_length] = line

    else:
        text_matrix[line_idx, :] = line
        
np.save(test_hyp_path, text_matrix)

text_matrix = np.full((len(working_testing_pre_text), max_len), vocab_order["<pad>"], dtype=int)
for line_idx, line in enumerate(working_testing_pre_text):
    line_length: int = len(line)

    if line_length > max_len:
        # truncate line
        # chop off from beginning
        text_matrix[line_idx, :] = line[max_len-line_length:] # truncate the begnning of the senetence

    elif line_length < max_len:
        # pad case....the pad tokens are already set, but we need to overwrite the correct values
        # in text_matrix[line_idx]

        text_matrix[line_idx, 0:line_length] = line

    else:
        text_matrix[line_idx, :] = line
        
np.save(test_pre_path, text_matrix)

text_matrix = np.full((len(trainingSet_label)), vocab_order["<pad>"], dtype=int)
for line_idx in range(len(trainingSet_label)):
    text_matrix[line_idx] = trainingSet_label[line_idx]

np.save(train_label_path, text_matrix)

text_matrix = np.full((len(testingSet_label)), vocab_order["<pad>"], dtype=int)
for line_idx in range(len(testingSet_label)):
    text_matrix[line_idx] = testingSet_label[line_idx]

np.save(test_label_path, text_matrix)
