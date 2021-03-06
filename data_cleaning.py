# -*- coding: utf-8 -*-

import pandas as pd
import re
import glob
import json
#from replacers import SpellingReplacer
#from replacers import RegexpReplacer
#from replacers import RepeatReplacer
from nltk.corpus import stopwords

#LOADING DATA FROM JSON FILES
def load_json(path):
    files = glob.glob(path)
    dictlist = []
    for file in files:
        json_string = open(file, 'r').read()
        json_dict = json.loads(json_string)
        dictlist.append(json_dict)
    df = pd.DataFrame(dictlist)
    return df

df = load_json('./Data/tweet/*')

def drop_excess(df):
    df = df.replace({'\n': ' '}, regex=True) # remove linebreaks in the dataframe
    df = df.replace({'\t': ' '}, regex=True) # remove tabs in the dataframe
    df = df.replace({'\r': ' '}, regex=True) # remove carriage return in the dataframe
    df = df.drop(['nbr_retweet','url', 'nbr_favorite', 'nbr_reply', 'is_reply', 'user_id','is_retweet', 'usernameTweet', 'ID', 'has_media', 'medias'],axis=1)
    return df

df = drop_excess(df)
df.to_csv("tweets_dates.csv", index=False)

#LOADING DATA FROM CSV FILE
def load_data_csv(path):
    cols = ['datetime','text']
    df = pd.read_csv(path, skiprows = 1, names = cols)
    # above line will be different depending on where you saved your data, and your file name
    df.head()
    return df

df = load_data_csv("./tweets_limpios_hastacasefolding.csv")

#REMOVING @-mentions, HTML tags #REPLACING ’´ WITH '
def cleaning_data(df):
    df['text'] = df['text'].replace({r'<[^>]+>': ''}, regex=True) # remove HTML tags
    df['text'] = df['text'].replace({r'(?:@[\w_]+)': ''}, regex=True) # remove @mentions
    df['text'] = df['text'].replace({'’': '\''}, regex=True) # replace ’ with '
    df['text'] = df['text'].replace({'´': '\''}, regex=True) # replace ´ with '
    return df

df = cleaning_data(df)

#CASE-FOLDING FOR CASE INSENSITIVE MATCHING
def case_folding(df):
    for index, row in df.iterrows():
        df.at[index, 'text'] = row['text'].casefold() #Python3
        #df.at[index, 'text'] = row['text'].lower() #Python2
    return df

df = case_folding(df)

#REMOVING URLs
def removing_urls(df):
    for index, row in df.iterrows():
        s = re.sub(r'https?:// ?[^ ]+', '', row['text'])
        s = re.sub(r'(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'".,<>?«»“”‘’]))', '', s)
        s = re.sub(r'([\w_]/[\w_]+)','', s)
        s = re.sub(r'([a-z0-9.\-]+/+)','', s)
        s = re.sub(r'([a-z0-9.\-]+.com+)','', s)
        df.at[index, 'text'] = re.sub(r'([a-z0-9.\-]+.html+)','', s)
    return df

df = removing_urls(df)

#CORRECTING SPELLING - we will do it with R
def spelling_corr(df):
    replacer = SpellingReplacer()
    for index, row in df.iterrows():
        df.at[index, 'text'] = replacer.replace(row['text'])
    return df

#STEMMING
def stemming(df):
    from nltk.stem import PorterStemmer
    from nltk.tokenize import RegexpTokenizer
    stemmer = PorterStemmer()
    for index, row in df.iterrows():
        tokenizer = RegexpTokenizer('\s+', gaps=True)
        words = tokenizer.tokenize(row['text'])
        for w in words:
            print('word: {}'.format(w))
            ste = stemmer.stem(w)
            print('stem: {}'.format(ste))
            if ste != w:
                print(row['text'])
                df.at[index, 'text'] = re.sub(w,ste, row['text'])
                print(row['text'])
        if index > 10:
            break
    return df

#REMOVING PUNCTUATIONS, NUMBERS, HASHES - in R

#TRANSFORMING EMOJIS AND EMOTICONS INTO WORDS - in R

#REMOVING STOPWORDS
def removing_stopwords(df):
    to_remove = ['no', 'nor', 'not', 'don', "don't", 'ain', 'aren', "aren't", 'couldn', "couldn't", 'didn', "didn't", 'doesn', "doesn't", 'hadn', "hadn't", 'hasn', "hasn't", 'haven', "haven't", 'isn', "isn't"]
    new_stopwords = set(stopwords.words('english')).difference(to_remove)
    for w in new_stopwords:
        print(r'\b{0}\b'.format(w))
        df['text'] = df['text'].replace({r'\b{0}\b'.format(w): ''}, regex=True)
    return df

removing_stopwords(df)

#TRANSFORMING CONTRACTIONS - in R
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
    df.to_csv("tweets_limpios_hastacasefolding.csv", index=False)

#export_csv(df)

#________________________________________________WORKING ON_____________________________________



#REMOVING EMOTICONS?- no funciona por ahora
df['text'] = df['text'].replace({r"""(?:[:=;] # Eyes[oO\-]? # Nose (optional)[D\)\]\(\]/\\OpP] # Mouth)""": ''}, regex=True) # remove emoticons NOPE

#REMOVING HASHTAGS? - será mejor borrar sólo es símbolo? Si lo hacemos como abajo borra el símbolo y la palabra, no seeeeee
df['text'] = df['text'].replace({r"(?:\#+[\w_]+[\w\'_\-]*[\w_]+)": ''}, regex=True) # remove hash-tags


#SENTIMENT____________________________________________________________________

def sent_pattern(df):
    from pattern.en import sentiment, polarity, subjectivity, positive
    for index, row in df.iterrows():
        print(row['text'], sentiment(row['text']))
        if index >=20:
            break

sent_pattern(df)
   
def sent_textblob(df):
    from textblob import TextBlob
    for index, row in df.iterrows():
        x = TextBlob(row['text'])
        print(x)
        print(x.sentiment)
        if index >=20:
            break
    
sent_textblob(df)    

"""
    emoticons
    abreviationsn
    remove numbers
"""
