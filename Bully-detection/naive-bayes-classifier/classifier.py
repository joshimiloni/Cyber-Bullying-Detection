#!/usr/bin/env python

from __future__ import division
from collections import Counter, defaultdict
from math import log,isinf
import csv
import codecs
import re
import random
import json

from lib import *

def featurize(datum):
    features = []
    last_word = '^'
    for word in lower(datum):
        features.append(word)
        features.append(last_word + "_" + word)
        last_word = word
    return set(features)


def train_classifier(data, class_of_interest):
 
  # 1. Collect count(c)
  # The total number of times we see each label.
  # This should have counts for 'True' (needs food), and 'False' (doesn't need food)
  total_counts = Counter()
  for datum in data:
    if datum.answer() == class_of_interest:
      total_counts[True] += 1
    else:
      total_counts[False] += 1

  # 2. Compute p(c)
  # The probability of each label. This should mirror total_counts.
  total_probs = Counter()
  total_probs[True] = total_counts[True] / (total_counts[True] + total_counts[False])
  total_probs[False] = total_counts[False] / (total_counts[True] + total_counts[False])

  # 3. Collect count(f | c)
  true_counts = Counter()
  false_counts = Counter()
  # For each tweet in our dataset...
  for datum in data:
    features = featurize(datum)
    for feature in features:
      if datum.answer() == class_of_interest:
        true_counts[feature] += 1
      else:
       false_counts[feature] += 1
  # Add an UNK count
  true_counts['__UNK__'] = 1
  false_counts['__UNK__'] = 1
  # Smooth the counts (add 0.1 fake counts to each feature)
  features = set(true_counts + false_counts)
  for feature in features:
      true_counts[feature] += 1.0
      false_counts[feature] += 1.0

  # 4. Compute p(f | c)
  true_probs = Counter()
  false_probs = Counter()
  # p(f | c) = count(f, c) / count(c)
  for feature in true_counts:
      true_probs[feature] = true_counts[feature] / total_counts[True];
  for feature in false_counts:
      false_probs[feature] = false_counts[feature] / total_counts[False];

  # 5. Return the model
  return [total_probs, true_probs, false_probs]


def classify(model, datum):

  # Unpack the model
  [total_probs, true_probs, false_probs] = model
  # Start the log scores at 0.0
  true_score = 0.0
  false_score = 0.0

  # Featurize the input
  features = featurize(datum)

  # Multiply in p(c)
  true_score += log(total_probs[True])
  false_score += log(total_probs[False])

  # Multiply in p(f | c) for each f
  for feature in features:
    if feature in true_probs:
      true_score += log(true_probs[feature])
    else:
      true_score += log(true_probs['__UNK__'])
    if feature in false_probs:
      false_score += log(false_probs[feature])
    else:
      false_score += log(false_probs['__UNK__'])

  # Some error checking
  if isinf(true_score) or isinf(false_score):
    print ("WARNING: either true_score or false_score is infinite")

  # Return the most likely class.
  return true_score > false_score


if __name__ == "__main__":
  # The free variables to set
  filename = 'datasets/new_data.csv'
  target_class = '1'

  # Load the data
  [train_data, dev_data, test_data] = load_data_from_csv(filename)

  # Train the classifier
  classifier = train_classifier(train_data, target_class)

  # Evaluate the classifier
  in_class = []
  not_in_class = []
  for datum in dev_data:
    if classify(classifier, datum):
      in_class.append(datum)
    else:
      not_in_class.append(datum)
  evaluate(target_class, in_class, not_in_class)

  import tweepy
  from tweepy import OAuthHandler

  # set up api keys
  consumer_key = "Duw3rXopMBHfM8OtNMy8NJLQr"
  consumer_secret = "oinn6izuprljeIgXsYp48c9acvqawAE5rCnrtzqyC2bIRqeRPV"
  access_token = "3058890440-7Q0qIMkrT31ZNlBpmzD77dQd2R9PLqqkcfPNcxL"
  access_secret = "ukrKwrLK5NKmCt4VdIZbqLcw0aldRznlj0YIoh7ZOxaHS"

  # set up auth and api
  auth = OAuthHandler(consumer_key, consumer_secret)
  auth.set_access_token(access_token, access_secret)
  api = tweepy.API(auth, wait_on_rate_limit=True)

  for status in tweepy.Cursor(api.home_timeline).items(1):
      print ("tweet: "+ status.text.encode('utf-8'))
      # get rid of punctuation
      tweet = status.text
      tweet = tweet.lower()
      if classify(classifier, Datum(tweet, '0')):
          print ("bullying")
          api.update_status("@" + status.author.screen_name+"\n You should stop bullying people. (I am a bot in testing, don't take this too seriously)", status.id)
      else:
          print ("not bullying")
          api.update_status("@" + status.author.screen_name+"\n Good job, you're not a bully! (I am a bot in testing, don't take this too seriously)", status.id)
