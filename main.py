import tweepy
import datetime
import os
import yaml
from random import choice
from time import sleep, time
from github import Github
import threading


def get_infos():
    if os.path.exists('key.yaml'):
        with open('key.yaml', 'r') as f:
            config = yaml.load(f, Loader=yaml.FullLoader)
            return config
    else:
        return os.environ.get('consumer_key'), os.environ.get('consumer_secret'), os.environ.get(
            'access_token'), os.environ.get('access_token_secret'), os.environ.get('github_id'), os.environ.get(
            'github_secret')


conf = get_infos()
auth = tweepy.OAuthHandler(conf['consumer_key'], conf['consumer_secret'])
auth.set_access_token(conf['access_token'], conf['access_token_secret'])
api = tweepy.API(auth)
user = Github(login_or_token='token', password=conf['github_secret'])

msg_list = [s for s in open('messages.txt', encoding='utf-8-sig').read().split('\n') if s != '']


def tweet(msg):
    api.update_status(msg)


def today():
    t = datetime.datetime.today()
    t_d = datetime.datetime(t.year, t.month, t.day)
    return t_d


def get_today_commits():
    for event in user.get_user(conf['github_id']).get_events():
        if event.created_at > today():
            if event.type in ['PushEvent', 'PullRequestEvent', 'IssueEvent']:
                yield event
        else:
            break


def handle(usr_name):
    if len(list(get_today_commits())) == 20:
        try:
            tweet(usr_name + ' ' + choice(msg_list))
        except tweepy.error.TweepError:
            print('Tweet duplicated')
            pass
        print('Tweet sent!')


def send_log(user_id, men):
    api.update_status('@' + men + ' total ' + str(len(list(get_today_commits()))) + 'committed today',
                      in_reply_to_status_id=user_id)


def run_auto():
    while True:
        if datetime.datetime.today().hour > 1:
            handle('@dev_kiha')
            sleep(86400)
        else:
            sleep(100)


class MentionListener(tweepy.StreamListener):
    def on_status(self, status):
        print(status.text)
        send_log(status.id, status.user.screen_name)


if __name__ == '__main__':
    lastId = -1
    tweet('Start Running Bot! ..At ' + str(time()) + '!')
    th = threading.Thread(target=run_auto)
    th.start()
    listener = MentionListener()
    stream = tweepy.Stream(auth=api.auth, listener=listener)
    stream.filter(track=['dailycommit_bot'])
