import json

from sqlalchemy import Column, ForeignKey, BigInteger, String, Text, DateTime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import exists
from sqlalchemy.ext.declarative import declarative_base

import config

engine = create_engine(config.CONNECT_STRING, echo=True)

Session = sessionmaker(bind=engine)
sess = Session()

Base = declarative_base()


class Tweet(Base):
    __tablename__ = 'tweets'

    id = Column(BigInteger, primary_key=True)
    user = Column(BigInteger, ForeignKey("users.id", ondelete='CASCADE'), nullable=False)
    tweet_data = Column(Text(convert_unicode=True))
    text = Column(String(length=500, convert_unicode=True))
    date = Column(DateTime)
    in_reply_to_id = Column(BigInteger)
    retweet_id = Column(BigInteger)

    @classmethod
    def save_tweet(klass, ref_tweet):
        user = sess.query(User).filter_by(id=ref_tweet.user.id).first()
        # TODO this does not update existing users, which can change
        if not user:
            user = User(
                id=ref_tweet.user.id,
                screen_name=ref_tweet.user.screen_name,
                name=ref_tweet.user.name,
                profile_image=ref_tweet.user.profile_image_url_https
            )
            sess.add(user)
            sess.commit()

        tweet = sess.query(Tweet).filter_by(id=ref_tweet.id).first()
        if not tweet:
            tweet = klass(
                id=ref_tweet.id,
                user=user.id,
                tweet_data=json.dumps(ref_tweet._json),
                text=ref_tweet.text,
                date=ref_tweet.created_at
            )
            tweet.in_reply_to_id = ref_tweet.in_reply_to_status_id
            if hasattr(ref_tweet, 'retweeted_status'):
                tweet.retweet_id = ref_tweet.retweeted_status.id
            sess.add(tweet)
            sess.commit()

        for u_mention in ref_tweet.entities['user_mentions']:
            mentioned_user = sess.query(User).filter_by(id=u_mention['id']).first()
            if not mentioned_user:
                # TODO refactor into function
                mentioned_user = User(
                    id=u_mention['id'],
                    screen_name=u_mention['screen_name'],
                    name=u_mention['name']
                )
                sess.add(mentioned_user)
                sess.commit()

            mention = Mention(
                tweet=tweet.id,
                user=user.id,
                user_mentioned=mentioned_user.id
            )
            sess.add(mention)
            sess.commit()


class User(Base):
    __tablename__ = 'users'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    screen_name = Column(String(length=200, convert_unicode=True))
    name = Column(String(length=500, convert_unicode=True))
    profile_image = Column(String(length=2000, convert_unicode=True))


class Mention(Base):
    __tablename__ = 'mentions'

    id = Column(BigInteger, primary_key=True)
    tweet = Column(BigInteger, ForeignKey("tweets.id", ondelete='CASCADE'), nullable=True)
    user = Column(BigInteger, ForeignKey("users.id", ondelete='CASCADE'), nullable=True)
    user_mentioned = Column(BigInteger, ForeignKey("users.id", ondelete='CASCADE'), nullable=True)
