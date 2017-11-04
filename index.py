import os
import logging
import tweepy
from flask import Flask, session, redirect, render_template, request, url_for

CONSUMER_KEY = os.environ['CONSUMER_KEY']
CONSUMER_SECRET = os.environ['CONSUMER_SECRET']
CALLBACK_URL = 'http://localhost:5000/callback'

app = Flask(__name__)
app.secret_key = os.environ['SECRET_KEY']

@app.route('/')
def index():
  if is_logged_in():
    profile = get_profile()
  else:
    profile = False
  return render_template('index.html', profile=profile)

@app.route('/auth')
def auth():
  auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET, CALLBACK_URL)

  try:
    redirect_url = auth.get_authorization_url()
    # 認証後に必要なrequest_tokenをsessionに保存
    session['request_token'] = auth.request_token
  except tweepy.TweepError as e:
    logging.error(str(e))

  return redirect(redirect_url)

@app.route('/logout')
def logout():
  session.pop('access_token', None)
  session.pop('access_secret', None)
  return redirect(url_for('index'))

@app.route('/callback')
def callback():
  token = session.pop('request_token', None)
  verifier = request.args.get('oauth_verifier')
  if token is None or verifier is None:
    return redirect(url_for('index'))
  auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET, CALLBACK_URL)
  auth.request_token = token
  try:
    auth.get_access_token(verifier)
    session['access_token'] = auth.access_token
    session['access_secret'] = auth.access_token_secret
  except tweepy.TweepError as e:
    logging.error(str(e))
  return redirect(url_for('index'))

def is_logged_in():
  token = session.get('access_token')
  secret = session.get('access_secret')
  if token is not None and secret is not None:
    return True
  else:
    return False

def get_profile():
  token = session.get('access_token')
  secret = session.get('access_secret')
  auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
  auth.set_access_token(token, secret)
  api = tweepy.API(auth)
  return api.me()

if __name__ == '__main__':
  app.run(debug=True)