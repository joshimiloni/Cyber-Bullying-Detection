#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
"""

from __future__ import division
import re
import csv
import random
import codecs
import numpy as np
from collections import Counter, defaultdict
try:
  from pandas import *
  pandas.set_option('display.max_colwidth', -1)
  pandas.set_option('display.width', 100)
except:
  pass
try:
  from IPython.display import display
  from IPython.display import HTML
except:
  pass
try:
  import web
  from web.wsgi import httpserver
except:
  pass

# -----------------------------------------------------------------------------
# BEGIN "MAGIC" CODE
# Don't get intimidated by this if you don't understand this part of the code.
# But, you're encouraged to go spelunking!
# -----------------------------------------------------------------------------


# -----
# BEGIN TOKENIZATION CODE
# -----
# (don't worry about this code)

_re_word_start    = r"[^\(\"\`{\[:;&\#\*@\)}\]\-,]"
"""Excludes some characters from starting word tokens"""

_re_non_word_chars   = r"(?:[?!)\";}\]\*:@\'\({\[])"
"""Characters that cannot appear within words"""

_re_multi_char_punct = r"(?:\-{2,}|\.{2,}|(?:\.\s){2,}\.)"
"""Hyphen and ellipsis are multi-character punctuation"""

_word_tokenize_fmt = r'''(
    %(MultiChar)s
    |
    (?=%(WordStart)s)\S+?  # Accept word characters until end is found
    (?= # Sequences marking a word's end
        \s|                                 # White-space
        $|                                  # End-of-string
        %(NonWord)s|%(MultiChar)s|          # Punctuation
        ,(?=$|\s|%(NonWord)s|%(MultiChar)s) # Comma if at end of word
    )
    |
    \S
)'''
"""Format of a regular expression to split punctuation from words, excluding period."""

def _word_tokenizer_re():
  """Compiles and returns a regular expression for word tokenization"""
  try:
    return _re_word_tokenizer
  except UnboundLocalError:
   _re_word_tokenizer = re.compile(
     _word_tokenize_fmt %
     {
       'NonWord':   _re_non_word_chars,
       'MultiChar': _re_multi_char_punct,
       'WordStart': _re_word_start,
     },
     re.UNICODE | re.VERBOSE
   )
   return _re_word_tokenizer

def word_tokenize(s):
  """Tokenize a string to split off punctuation other than periods"""
  return _word_tokenizer_re().findall(s)
# -----
# END TOKENIZATION CODE
# -----


# BEGIN CLASS datum
"""
  A class for Text datums
"""
class Datum:
  """
    Create a new Datum object, taking as input the text of the
    datum and the label associated with it.
    @param datumSurfaceForm:String The surface form of the datum.
    @param datumLabel:String The annotated label for this datum.
  """
  def __init__(self, datumSurfaceForm, datumLabel):
    if isinstance(datumSurfaceForm, unicode):
      self.datumTokens = word_tokenize(datumSurfaceForm)
    else:
      self.datumTokens = word_tokenize(unicode(datumSurfaceForm, 'utf-8'))
    self.datumLabel = datumLabel

  """
    Get the i^th token for a (tokenized) datum.
    @param index:Int The index of the i^th token (i.e., "i").
    @return:String The token at the given index.
  """
  def __getitem__(self,index):
    return self.datumTokens[index]

  """
    Get the actual label of this datum -- i.e., what humans thought
    the correct category for it should be.
    @return:String The label for the datum.
  """
  def answer(self):
    return self.datumLabel

  def __unicode__(self):
    return " ".join(self.datumTokens)

  def __str__(self):
    return unicode(self).encode('utf-8')

  def __repr__(self):
      return self.__str__()
# END CLASS datum

def lower(datum):
  """
    Lowercase the text in a tweet.

    @param datum:Datum The datum to lowercase
  """
  return Datum(" ".join([x.lower() for x in datum.datumTokens]), datum.datumLabel)


def load_data_from_csv(path):
    """
      Load the training+test data, at the given path.
      @param path:String The filepath of the full data. This should be a comma-separated
                         file with the first column being a block of text, and the
                         second column being the class label for that text.
      @return:(Datum[], Datum[], Datum[]) The train/dev/test data portion of the data
                                          at this path.
    """
    data = []

    f = codecs.open(path, encoding='utf-8')
    with open(path) as f:
        reader = csv.reader(f)
        next(reader) # ignore header
        for row in reader:
            data.append(Datum(row[0], row[1]))

    random.seed(7)
    random.shuffle(data)

    train_size = int(len(data) * 0.7)
    dev_size = int(len(data) * 0.3)
    return data[:train_size], data[train_size:train_size+dev_size], data[train_size+dev_size:]


def load_tweets(path = 'food.csv'):
    """
      Load the (training) tweets into a list.
      @return:Tweet[] A list of tweets that should be classified.
    """
    train, _, _ = load_data_from_csv(path)
    return train

def load_unseen_tweets(path = 'food.csv'):
    """
      Load the (training) tweets into a list.
      @return:Tweet[] A list of tweets that should be classified.
    """
    _, dev, _ = load_data_from_csv(path)
    return dev

"""
  Evaluate your accuracy on a particular label.
  @param label:String The label we are evaluating on.
  @param guessedTrue:Tweet[] The tweets we think are about this label.
  @param guessedFalse:Tweet[] The tweets we think are _not_ about this label.
"""
def evaluate(label, guessedTrue, guessedFalse):
    truePositives = len([x for x in guessedTrue if x.answer() == label])
    trueNegatives = len([x for x in guessedFalse if x.answer() != label])
    falsePositives = len([x for x in guessedTrue if x.answer() != label])
    falseNegatives = len([x for x in guessedFalse if x.answer() == label])

    accuracy = (truePositives + trueNegatives)/(truePositives + trueNegatives + falsePositives + falseNegatives)
    precision = (truePositives)/(truePositives + falsePositives)
    recall = (truePositives)/(truePositives + falseNegatives)
    F1 = (2.0 * precision * recall) /(precision + recall if precision + recall > 0 else 1)

    #print "Accuracy:  %.3g" % (accuracy * 100.0)
    #print "Precision: %.3g" % (precision * 100.0)
    print "Recall:    %.3g" % (recall * 100.0)
    #print "F1:        %.3g" % (F1 * 100.0)



"""
  Print the mistakes made on this label.
  In particular, print out the false positives and the false negatives.
  @param label:String The label we are evaluating on.
  @param guessedTrue:Tweet[] The tweets we think are about this label.
  @param guessedFalse:Tweet[] The tweets we think are _not_ about this label.
"""
def show_mistakes(label, guessedTrue, guessedFalse):
  false_positives = [unicode(x) for x in guessedTrue if x.answer() != label]
  false_negatives = [unicode(x) for x in guessedFalse if x.answer() == label]

  while len(false_positives) < len(false_negatives):
    false_positives.append('')
  while len(false_negatives) < len(false_positives):
    false_negatives.append('')

  df = DataFrame({"False positives" : false_positives, "False negatives" : false_negatives})
  display(HTML(df.to_html()))



def start_server(predict, port):
  """
    This code runs a webserver that runs the predictions.
  """
  class home(object):
      def GET(self):
          return 'Hello, world!'

  class classify(object):
      def GET(self, text):
          web.header('Access-Control-Allow-Origin', '*')
          web.header('Access-Control-Allow-Credentials', 'true')
          datum = Datum(text.strip(), None)
          if predict(datum):
            return json.dumps({'class' : "True"})
          else:
            return json.dumps({'class' : "False"})

      def POST(self):
          data = web.input()
          web.header('Content-Type', 'text/json')
          web.header("Access-Control-Allow-Origin", "*");
          web.header("Access-Control-Expose-Headers", "Access-Control-Allow-Origin");
          #web.header("Access-Control-Allow-Headers", "Origin, X-Requested-With, Content-Type, Accept");
          if 'text' not in data:
              return json.dumps(None)
          datum = Datum(data['text'].strip(), None)
          if predict(datum):
            return json.dumps({'class' : "True"})
          else:
            return json.dumps({'class' : "False"})

  urls = (
    '/', 'home',
    '/classify', 'classify',
  )
  app = web.application(urls, {'home': home, 'classify' : classify})
  httpserver.runsimple(app.wsgifunc(), server_address=('0.0.0.0', port))
