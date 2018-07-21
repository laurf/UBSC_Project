# -*- coding: utf-8 -*-

import pandas as pd
import re
from replacers import SpellingReplacer
from replacers import RegexpReplacer
from replacers import RepeatReplacer
from nltk.corpus import stopwords

#LOADING DATA FROM CSV FILE
def load_data(path):
    cols = ['datetime','text']
    df = pd.read_csv(path, skiprows = 1, names = cols)
    # above line will be different depending on where you saved your data, and your file name
    df.head()
    return df

df = load_data("./tweets_parcial_limpios.csv")

#REMOVING @-mentions, HTML tags #REPLACING ’´ WITH ' - done
def cleaning_data(df):
    df['text'] = df['text'].replace({r'<[^>]+>': ''}, regex=True) # remove HTML tags
    df['text'] = df['text'].replace({r'(?:@[\w_]+)': ''}, regex=True) # remove @mentions
    df['text'] = df['text'].replace({'’': '\''}, regex=True) # replace ’ with '
    df['text'] = df['text'].replace({'´': '\''}, regex=True) # replace ´ with '
    return df

#CASE-FOLDING FOR CASE INSENSITIVE MATCHING - done
def case_folding(df):
    for index, row in df.iterrows():
        #df.at[index, 'text'] = row['text'].casefold() Python3
        df.at[index, 'text'] = row['text'].lower() #Python2
    return df

#REMOVING URLs
def removing_urls(df):
    for index, row in df.iterrows():
        df.at[index, 'text'] = re.sub(r'(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'".,<>?«»“”‘’]))', '', row['text'])
        
        #df.at[index, 'text'] = ' '.join(row['text'].split())
        #html http:// https:// punctuations numbers emojis to words
    return df

#CORRECTING SPELLING - done - only works in Python 2 and needs the enchant, aspell and pyenchant
def spelling_corr(df):
    replacer = SpellingReplacer()
    for index, row in df.iterrows():
        df.at[index, 'text'] = replacer.replace(row['text'])
    return df

#REMOVING STOPWORDS
def removing_stopwords(df):
    to_remove = ['no', 'nor', 'not', 'don', "don't", 'ain', 'aren', "aren't", 'couldn', "couldn't", 'didn', "didn't", 'doesn', "doesn't", 'hadn', "hadn't", 'hasn', "hasn't", 'haven', "haven't", 'isn', "isn't"]
    new_stopwords = set(stopwords.words('english')).difference(to_remove)
    for w in new_stopwords:
        print(r'\b{0}\b'.format(w))
        df['text'] = df['text'].replace({r'\b{0}\b'.format(w): ''}, regex=True)
    return df

"""
from nltk.stem import PorterStemmer # import Porter stemmer
from nltk.stem.lancaster import LancasterStemmer
from nltk.stem.Snowball import SnowballStemmer
pst = PorterStemmer()   # create obj of the PorterStemmer
lst = LancasterStemmer() # create obj of LancasterStemmer
lst.stem("I really like eating")
>>>pst.stem("shopping")
"""

#TRANSFORMING CONTRACTIONS - done
def trans_contractions(df):
    replacer = RegexpReplacer()
    for index, row in df.iterrows():
        df.at[index, 'text'] = replacer.replace(row['text'])
    return df

#REMOVING REPEATING CHARACTERS - want to run it after I remove URLs
def removing_repeat(df):
    replacer = RepeatReplacer()
    for index, row in df.iterrows():
        df.at[index, 'text'] = replacer.replace(row['text'])
    return df

#REMOVING EXTRA WHITE SPACES
def removing_extra_white_spaces(df):
    for index, row in df.iterrows():
        df.at[index, 'text'] = ' '.join(row['text'].split())
    return df

#______________________OTHER CODE_______________________
  
#SPLITTING INTO TWO DATAFRAMES
def splitting_dataframe(df):
    split_date = pd.datetime(2017, 6, 1)
    df_pre = df.loc[df['datetime'] < split_date]
    df_post = df.loc[df['datetime'] >= split_date]
    return df_pre, df_post
  
#COUNTING THE FREQUENCY OF THE WORDS
def counting_words(df):
    words = df.text.str.split(expand=True).stack().value_counts()
    return words

#words_pre = counting_words(df_pre)
#words_post = counting_words(df_post)

#GETTING THE TWEET FREQUENCY BY DATES
def tweets_by_dates(df):
    df['datetime'] = pd.to_datetime(df['datetime']) #Changing the column datetime from string to datetime format
    tweet_frequency = df['datetime'].dt.date.value_counts()
    return tweet_frequency

# Export to csv
def export_csv(df):
    df.to_csv("tweetslimpios.csv", index=False)

#export_csv(df)

#________________________________________________WORKING ON_____________________________________



#REMOVING EMOTICONS?- no funciona por ahora
df['text'] = df['text'].replace({r"""(?:[:=;] # Eyes[oO\-]? # Nose (optional)[D\)\]\(\]/\\OpP] # Mouth)""": ''}, regex=True) # remove emoticons NOPE

#REMOVING HASHTAGS? - será mejor borrar sólo es símbolo? Si lo hacemos como abajo borra el símbolo y la palabra, no seeeeee
df['text'] = df['text'].replace({r"(?:\#+[\w_]+[\w\'_\-]*[\w_]+)": ''}, regex=True) # remove hash-tags
  
"""
from pattern.en import sentiment, polarity, subjectivity, positive
for index, row in df.iterrows():
    print(row['text'], sentiment(row['text']))
    if index >=20:
        break
    
def analize_sentiment(data):
    '''
    Utility function to classify the polarity of a tweet
    using textblob.
    '''
    analysis = TextBlob(data)
    if analysis.sentiment.polarity > 0:
        return 1
    elif analysis.sentiment.polarity == 0:
        return 0
    else:
        return -1
    
from textblob import TextBlob
for index, row in df.iterrows():
    print(row['text'], analize_sentiment(row['text']))
    if index >=20:
        break
    
    emoticons
    abreviationsn
    remove numbers
"""
