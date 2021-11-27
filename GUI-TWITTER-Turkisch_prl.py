from tkinter import *
import numpy as np
import tweepy
import pandas as pd
from textblob import TextBlob
from wordcloud import WordCloud
from matplotlib import pyplot as plt
import re

root = Tk()
root.title('Twitter Sentimental Analysis by Piril')  # Başlık

# ================GUI Boyutlandırma Başlangıcı =================#
width = 600
hight = 400

root.geometry(f"{width}x{hight}")
root.minsize(width, hight)  # minimum boyut
root.maxsize(width, hight)  # maximum boyut
# ================GUI Boyutlandırma Bitiş===================#

# ================Banner/Çerçeve Başlangıç =================#
banner = Frame(root, padx=15, pady=14, bg="green")
banner.pack()

heding = Label(banner, text="Twitter Sentimental Analiz", font="comicsansms 20 bold")
heding.pack()

# ================Banner/Çerçeve Bitiş ===================#

# ================Kullanıcı Giriş Bölümü ===================#
input_frame = Frame(root, padx=0, pady=30)
input_frame.pack(anchor="w")

input_frame1 = Frame(root, padx=0, pady=0, bg="yellow")
input_frame1.pack()

username = Label(input_frame, text="UserID'yi giriniz (@ karakterini ekleyiniz)  :- ", justify=LEFT, font="comicsansms 10 bold", padx=30)
username.grid(row=2, column=1)

user_value = StringVar()
hash_value = StringVar()

userinput = Entry(input_frame, textvariable=user_value)
userinput.grid(row=2, column=2)

blank2 = Label(input_frame, text="veya")
blank2.grid(row=3, column=2)

hashtag = Label(input_frame, text=" Hashtag'i giriniz (# karakterini ekleyiniz) :- ", font="comicsansms 10 bold", padx=30)
hashtag.grid(row=4, column=1)

hashinput = Entry(input_frame, textvariable=hash_value)
hashinput.grid(row=4, column=2)
# ================Kullanıcı Giriş Bölümü Sonu ===================#

# ================Sentiment/Duygu Analizi Başlangıç ===================#.
f1 = Frame(root, padx=15, pady=14)
f1.pack()

f2 = Frame(root, padx=15, pady=14)
f2.pack(anchor="w")
error = Label(f1, text="En az bir seçeneği doldurmanız gerekli", fg="red")
error2 = Label(f1, text="Her iki giriş de geçerli değil", fg="red")

# ================Sentiment/Duygu Analizi Sonu===================#

po = Label(f2, text="Pozitif:-", padx=15)
na = Label(f2, text="Negatif:-", pady=5, padx=15)
nt = Label(f2, text="Nötr:-", padx=15)


def click():
    user_name = user_value.get()
    hash_name = hash_value.get()

    # ============================twitter API keys===========================
    consumerKey = ""
    consumerSecret = ""
    accessToken = ""
    accessTokenSecret = ""

    # ============================twitter API keys ===========================

    authenticate = tweepy.OAuthHandler(consumerKey, consumerSecret)
    authenticate.set_access_token(accessToken, accessTokenSecret)
    api = tweepy.API(authenticate, wait_on_rate_limit=True)

    if user_name == "" and hash_name == "":
        error.grid()
    elif hash_name == "":
        error.grid_remove()
        global number
        if number > 1:
            po.grid_remove()
            na.grid_remove()
            nt.grid_remove()

        post = api.user_timeline(screen_name=user_name, count=500, lang="en", tweet_mode="extended")
        twitter = pd.DataFrame([tweet.full_text for tweet in post], columns=['Tweets'])

        def cleanTxt(text):
            text = re.sub('@[A-Za-z0–9]+', '', text)  #  "@" kaldırılması
            text = re.sub('#', '', text)  # Hash tag '#' kaldırılması
            text = re.sub('RT[\s]+', '', text)  # RT kaldırılması
            text = re.sub('https?:\/\/\S+', '', text)  # hyperlink kaldırılması
            return text

        twitter['Tweets'] = twitter['Tweets'].apply(cleanTxt)

        def getSubjectivity(text):
            return TextBlob(text).sentiment.subjectivity

        def getPolarity(text):
            return TextBlob(text).sentiment.polarity

        twitter['Subjectivity'] = twitter['Tweets'].apply(getSubjectivity)
        twitter['Polarity'] = twitter['Tweets'].apply(getPolarity)

        def getAnalysis(score):
            if score < 0:
                return 'Negative'
            elif score == 0:
                return 'Neutral'
            else:
                return 'Positive'

        twitter['Analysis'] = twitter['Polarity'].apply(getAnalysis)
        positive = twitter.loc[twitter['Analysis'].str.contains('Positive')]
        negative = twitter.loc[twitter['Analysis'].str.contains('Negative')]
        neutral = twitter.loc[twitter['Analysis'].str.contains('Neutral')]

        positive_per = round((positive.shape[0] / twitter.shape[0]) * 100, 1)
        negative_per = round((negative.shape[0] / twitter.shape[0]) * 100, 1)
        neutral_per = round((neutral.shape[0] / twitter.shape[0]) * 100, 1)

        po = Label(f2, text=f"Pozitif:- {positive_per}%", padx=15).grid(row=1, column=2)
        na = Label(f2, text=f"Negatif:- {negative_per}%", pady=5, padx=15).grid(row=2, column=2)
        nt = Label(f2, text=f"Nötr:- {neutral_per}%", padx=15).grid(row=3, column=2)

        labels = 'Pozitif', 'Negatif', 'Nötr'
        sizes = [positive_per, negative_per, neutral_per]
        explode = (0, 0.1, 0)  # only "explode" the 2nd slice (i.e. 'Hogs')

        fig1, ax1 = plt.subplots()
        ax1.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%',
                shadow=True, startangle=90)
        ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

        plt.show()


        number += 1

    elif user_name == "":
        error.grid_remove()
        if number > 1:
            po.grid_remove()
            na.grid_remove()
            nt.grid_remove()

        msgs = []
        msg = []
        for tweet in tweepy.Cursor(api.search, q=hash_name).items(500):
            msg = [tweet.text]
            msg = tuple(msg)
            msgs.append(msg)

        def cleanTxt(text):
            text = re.sub('@[A-Za-z0–9]+', '', text)  # "@" kaldırılması
            text = re.sub('#', '', text)  # Hash tag '#' kaldırılması
            text = re.sub('RT[\s]+', '', text)  # RT kaldırılması
            text = re.sub('https?:\/\/\S+', '', text)  # hyperlink kaldırılması
            return text

        df = pd.DataFrame(msgs)
        df['Tweets'] = df[0].apply(cleanTxt)
        df.drop(0, axis=1, inplace=True)

        def getSubjectivity(text):
            return TextBlob(text).sentiment.subjectivity

        def getPolarity(text):
            return TextBlob(text).sentiment.polarity

        df['Subjectivity'] = df['Tweets'].apply(getSubjectivity)
        df['Polarity'] = df['Tweets'].apply(getPolarity)

        def getAnalysis(score):
            if score < 0:
                return 'Negative'
            elif score == 0:
                return 'Neutral'
            else:
                return 'Positive'

        df['Analysis'] = df['Polarity'].apply(getAnalysis)
        positive = df.loc[df['Analysis'].str.contains('Positive')]
        negative = df.loc[df['Analysis'].str.contains('Negative')]
        neutral = df.loc[df['Analysis'].str.contains('Neutral')]

        positive_per = round((positive.shape[0] / df.shape[0]) * 100, 1)
        negative_per = round((negative.shape[0] / df.shape[0]) * 100, 1)
        neutral_per = round((neutral.shape[0] / df.shape[0]) * 100, 1)

        po = Label(f2, text=f"Pozitif:- {positive_per}%", padx=15).grid(row=1, column=2)
        na = Label(f2, text=f"Negatif:- {negative_per}%", pady=5, padx=15).grid(row=2, column=2)
        nt = Label(f2, text=f"Nötr:- {neutral_per}%", padx=15).grid(row=3, column=2)

        labels = 'Pozitif', 'Negatif', 'Nötr'
        sizes = [positive_per, negative_per, neutral_per]
        explode = (0.1, 0.1, 0.1)

        fig1, ax1 = plt.subplots()
        ax1.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%',
                shadow=True, startangle=90)
        ax1.axis('equal')  # Eşit en boy oranı, pastanın bir daire olarak çizilmesini sağlar.

        plt.show()

        number += 1
    else:
        error2.grid()


number = 0
button = Button(input_frame1, text="Analize Başla", command=click, fg="blue", height=1, width=15)
button.grid(row=1, column=1)

root.mainloop()
