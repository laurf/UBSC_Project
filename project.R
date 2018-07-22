install.packages(c("devtools", "rjson", "bit64", "httr", "textclean"))
library(devtools)
library(textclean)

#LOADING TWEETS
df <- read.csv("/Users/laura/Documents/GitHub/TweetScraper/tweets_limpios_hastacasefolding.csv", encoding = "UTF-8")
df1 = df[1:50,]

df2 = df

catch.error = function(x){
  # let us create a missing value for test purpose
  y = NA
  # Try to catch that error (NA) we just created
  catch_error = tryCatch(tolower(x), error=function(e) e)
  # if not an error
  if (!inherits(catch_error, "error"))
    y = tolower(x)
  # check result if error exists, otherwise the function works fine.
  return(y)
}

cleanTweets<- function(tweet){  # Clean the tweet for sentiment analysis
  # remove html links, which are not required for sentiment analysis
  tweet = gsub("(f|ht)(tp)(s?)(://)(.*)[.|/](.*)", " ", tweet)
  # First we will remove retweet entities from the stored tweets (text)
  tweet = gsub("(RT|via)((?:\\b\\W*@\\w+)+)", " ", tweet)
  # Then remove all "@people"
  tweet = gsub("@\\w+", " ", tweet)
  # We remove contractions
  tweet = replace_contraction(tweet, ignore.case = TRUE)
  # We replace Emojis
  tweet = replace_emoji(tweet)
  # We replace Emoticons
  tweet = replace_emoticon(tweet)
  # We replace internet slang
  tweet = replace_internet_slang (tweet)
  # We remove ordinals
  tweet = replace_ordinal(tweet, remove = TRUE)
  # We replace symbols
  tweet = replace_symbol(tweet)
  # We replace word elongation
  tweet = replace_word_elongation(tweet)
  # We remove numbers, we need only text for analytics
  tweet = gsub("[[:digit:]]", " ", tweet)
  # We remove unnecessary spaces (white spaces, tabs etc)
  tweet = gsub("[ \t]{2,}", " ", tweet)
  tweet = gsub("^\\s+|\\s+$", "", tweet)
  # Then remove all the punctuation
  #tweet = gsub("[[:punct:]]", " ", tweet)
  # Next we'll convert all the word in lower case. This makes uniform pattern.
  tweet = catch.error(tweet)
  head(tweet)
  tweet
}

cleanTweetsAndRemoveNAs<- function(Tweets) {
  TweetsCleaned = sapply(Tweets, cleanTweets)
  # Remove the "NA" tweets from this tweet list
  TweetsCleaned = TweetsCleaned[!is.na(TweetsCleaned)]
  names(TweetsCleaned) = NULL
  # Remove the repetitive tweets from this tweet list
  TweetsCleaned = unique(TweetsCleaned)
  TweetsCleaned
}

chosen <- sample(unique(df$text), 10000)
 
tweetsCleaned <- cleanTweetsAndRemoveNAs(chosen)

head(tweetsCleaned,50)
head(df1,15)



install.packages("Rstem", repos = "http://www.omegahat.net/R", type="source")
library(Rstem)
install.packages("Rstem", repos = "http://www.omegahat.net/R")
require(devtools)
install_url("http://cran.r-project.org/src/contrib/Archive/sentiment/sentiment_0.2.tar.gz")
require(sentiment)
ls("package:sentiment")
library(sentiment)

emotionClassification = classify_emotion(tweetsCleaned, algorithm="bayes", prior=1.0)

temotion = temotionClassification[,7]
temotion[is.na(temotion)] = "unknown"
head(emotion,20)

polarityClassification = classify_polarity(tweetsCleaned, algorithm="bayes")

tpolarity = tpolarityClassification[,4]
sentimentDF = data.frame(text=tweetsCleaned, emotion=temotion, polarity=tpolarity, stringsAsFactors=FALSE)
sentimentDF = within(sentimentDF, emotion <- factor(emotion, levels=names(sort(table(emotion), decreasing=TRUE))))

plotSentiments1<- function (sentiment_dataframe,title) { 
  library(ggplot2)
  ggplot(sentiment_dataframe, aes(x=emotion)) + geom_bar(aes(y=..count.., fill=emotion)) +
    scale_fill_brewer(palette="Dark2") +
    ggtitle(title) + 
    theme(legend.position='right') + ylab('Number of Tweets') + xlab('Emotion Categories')}
plotSentiments1(sentimentDF, 'Sentiment Analysis of Tweets on World Cup')

plotSentiments2 <- function (sentiment_dataframe,title) { 
  library(ggplot2)
  ggplot(sentiment_dataframe, aes(x=polarity)) +
    geom_bar(aes(y=..count.., fill=polarity)) +
    scale_fill_brewer(palette="RdGy") +
    ggtitle(title) + 
    theme(legend.position='right') + ylab('Number of Tweets') + xlab('Polarity Categories')
}
plotSentiments2(sentimentDF, 'Polarity Analysis of Tweets on World Cup')

install.packages(c("wordcloud"))
library(wordcloud)

removeCustomeWords <- function (TweetsCleaned) { 
  for(i in 1:length(TweetsCleaned)){ 
    TweetsCleaned[i] <- tryCatch({ 
      TweetsCleaned[i] = removeWords(TweetsCleaned[i], c(stopwords("english"), "care", "guys", "can", "dis", "didn", "guy" ,"booked", "plz")) 
      TweetsCleaned[i] 
    }, error=function(cond) { 
      TweetsCleaned[i] 
    }, warning=function(cond) { 
      TweetsCleaned[i] 
    })} 
  return(TweetsCleaned)}
getWordCloud <- function (sentiment_dataframe, TweetsCleaned, Emotion) { 
  emos = levels(factor(sentiment_dataframe$emotion)) 
  n_emos = length(emos) 
  emo.docs = rep("", n_emos) 
  TweetsCleaned = removeCustomeWords(TweetsCleaned) 
  for (i in 1:n_emos){ 
    emo.docs[i] = paste(TweetsCleaned[Emotion == emos[i]], collapse=" ")   } 
  corpus = Corpus(VectorSource(emo.docs)) 
  tdm = TermDocumentMatrix(corpus) 
  tdm = as.matrix(tdm) 
  colnames(tdm) = emos 
  require(wordcloud) 
  suppressWarnings(comparison.cloud(tdm, colors = brewer.pal(n_emos, "Dark2"), scale = c(3,.5), random.order = FALSE, title.size = 1.5))}
getWordCloud(sentimentDF, tweetsCleaned, temotion)

getWordCloud2 <- function (sentiment_dataframe, TweetsCleaned, Emotion) { 
  emos = levels(factor(sentiment_dataframe$polarity)) 
  n_emos = length(emos) 
  emo.docs = rep("", n_emos) 
  TweetsCleaned = removeCustomeWords(TweetsCleaned) 
  for (i in 1:n_emos){ 
    emo.docs[i] = paste(TweetsCleaned[Emotion == emos[i]], collapse=" ")   } 
  corpus = Corpus(VectorSource(emo.docs)) 
  tdm = TermDocumentMatrix(corpus) 
  tdm = as.matrix(tdm) 
  colnames(tdm) = emos 
  require(wordcloud) 
  suppressWarnings(comparison.cloud(tdm, colors = brewer.pal(n_emos, "Dark2"), scale = c(3,.5), random.order = FALSE, title.size = 1.5))}
getWordCloud2(sentimentDF, tweetsCleaned, tpolarity)

install.packages("RSentiment")
library(RSentiment)

WorldCupTweetsSent = calculate_sentiment(tweetsCleaned)
WorldCupEmotionS = WorldCupTweetsSent[,2]
head(WorldCupEmotionS,20)

WorldCupTweetsClassPol = classify_polarity(WorldCupTweetsCleaned, algorithm="bayes")

WorldCupPol = WorldCupTweetsClassPol[,4]


WorldCupSentimentDataFrame = data.frame(text= WorldCupTweetsCleaned, emotion= WorldCupEmotion, polarity= WorldCupPol, stringsAsFactors=FALSE)
WorldCupSentimentDataFrame = within(WorldCupSentimentDataFrame, emotion <- factor(emotion, levels=names(sort(table(emotion), decreasing=TRUE))))

getWordCloud(WorldCupSentimentDataFrame, WorldCupTweetsCleaned, WorldCupPol)
