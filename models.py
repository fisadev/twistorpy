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


class Twit(Base):
    __tablename__ = 'twits'

    id = Column(BigInteger, primary_key=True)
    user = Column(BigInteger, ForeignKey("users.id", ondelete='CASCADE'), nullable=False)
    twit_data = Column(Text(convert_unicode=True))
    text = Column(String(length=500, convert_unicode=True))
    date = Column(DateTime)
    in_reply_to_id = Column(BigInteger)
    retwit_id = Column(BigInteger)

    @classmethod
    def save_twit(klass, ref_twit):
        user = sess.query(User).filter_by(id=ref_twit.user.id).first()
        # TODO this does not update existing users, which can change
        if not user:
            user = User(
                id=ref_twit.user.id,
                screen_name=ref_twit.user.screen_name,
                name=ref_twit.user.name,
                profile_image=ref_twit.user.profile_image_url_https
            )
            sess.add(user)
            sess.commit()

        twit = sess.query(Twit).filter_by(id=ref_twit.id).first()
        if not twit:
            twit = klass(
                id=ref_twit.id,
                user=user.id,
                twit_data=json.dumps(ref_twit._json),
                text=ref_twit.text,
                date=ref_twit.created_at
            )
            twit.in_reply_to_id = ref_twit.in_reply_to_status_id
            if hasattr(ref_twit, 'retweeted_status'):
                twit.retwit_id = ref_twit.retweeted_status.id
            sess.add(twit)
            sess.commit()

        for u_mention in ref_twit.entities['user_mentions']:
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
                twit=twit.id,
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
    twit = Column(BigInteger, ForeignKey("twits.id", ondelete='CASCADE'), nullable=True)
    user = Column(BigInteger, ForeignKey("users.id", ondelete='CASCADE'), nullable=True)
    user_mentioned = Column(BigInteger, ForeignKey("users.id", ondelete='CASCADE'), nullable=True)
