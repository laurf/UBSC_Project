# -*- coding: utf-8 -*-

import pandas as pd
import re

#LOADING DATA FROM CSV FILE
cols = ['datetime','text']
df = pd.read_csv("./tweetslimpios.csv", skiprows = 1, names = cols)
# above line will be different depending on where you saved your data, and your file name
df.head()

#REMOVING @-mentions, HTML tags #REPLACING ’´ WITH ' - done   
df['text'] = df['text'].replace({r'<[^>]+>': ''}, regex=True) # remove HTML tags
df['text'] = df['text'].replace({r'(?:@[\w_]+)': ''}, regex=True) # remove @mentions
df['text'] = df['text'].replace({'’': '\''}, regex=True) # replace ’ with '
df['text'] = df['text'].replace({'´': '\''}, regex=True) # replace ´ with '

#CASE-FOLDING FOR CASE INSENSITIVE MATCHING - done
for index, row in df.iterrows():
    #df.at[index, 'text'] = row['text'].casefold() Python3
    df.at[index, 'text'] = row['text'].lower() #Python2
    
#CORRECTING SPELLING - done - only works in Python 2 and needs the enchant, aspell and pyenchant
from replacers import SpellingReplacer
replacer = SpellingReplacer()
for index, row in df.iterrows():
    df.at[index, 'text'] = replacer.replace(row['text'])

#TRANSFORMING CONTRACTIONS - done
from replacers import RegexpReplacer
replacer = RegexpReplacer()
for index, row in df.iterrows():
    df.at[index, 'text'] = replacer.replace(row['text'])

#REMOVING REPEATING CHARACTERS - want to run it after I remove URLs
from replacers import RepeatReplacer
replacer = RepeatReplacer()
for index, row in df.iterrows():
    df.at[index, 'text'] = replacer.replace(row['text'])
    
#______________________OTHER CODE_______________________
  
#SPLITTING INTO TWO DATAFRAMES
split_date = pd.datetime(2017, 6, 1)
df_pre = df.loc[df['datetime'] < split_date]
df_post = df.loc[df['datetime'] >= split_date]
  
#COUNTING THE FREQUENCY OF THE WORDS
words_pre = df_pre.text.str.split(expand=True).stack().value_counts()
words_post = df_post.text.str.split(expand=True).stack().value_counts()

#GETTING THE TWEET FREQUENCY BY DATES
df['datetime'] = pd.to_datetime(df['datetime']) #Changing the column datetime from string to datetime format
tweet_frequency = df['datetime'].dt.date.value_counts()

# Export to csv
df.to_csv("tweetslimpios.csv", index=False)
tweet_frequency.to_csv("tweet_frequency.csv")
words_pre.to_csv("word_frequency_pre.csv")
words_post.to_csv("word_frequency_post.csv")


#________________________________________________WORKING ON_____________________________________

#REMOVING EXTRA WHITE SPACES - no funciona por ahora
for index, row in df.iterrows():
    df.at[index, 'text'] = re.sub(' +',' ',row['text'])

#REMOVING URLs- no funciona por ahora
for index, row in df.iterrows():
    df.at[index, 'text'] = row['text'].replace({r'http[s]?://(?:[a-z]|[0-9]|[$-_@.&amp;+]|[!*\(\),]|(?:%[0-9a-f][0-9a-f]))+': ''}, regex=True)

#REMOVING EMOTICONS?- no funciona por ahora
df['text'] = df['text'].replace({r"""(?:[:=;] # Eyes[oO\-]? # Nose (optional)[D\)\]\(\]/\\OpP] # Mouth)""": ''}, regex=True) # remove emoticons NOPE

#REMOVING HASHTAGS? - será mejor borrar sólo es símbolo? Si lo hacemos como abajo borra el símbolo y la palabra, no seeeeee
df['text'] = df['text'].replace({r"(?:\#+[\w_]+[\w\'_\-]*[\w_]+)": ''}, regex=True) # remove hash-tags