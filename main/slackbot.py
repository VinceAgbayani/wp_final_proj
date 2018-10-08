import os
import time
import datetime as dt
import re
from slackclient import SlackClient
from twitter import *
import schedule
import tokens as tk

# instantiate Slack client
slack_client = SlackClient(tk.slack_auth)
twitter = Twitter(auth = OAuth(tk.auth1, tk.auth2, tk.auth3, tk.auth4))
results = twitter.trends.place(_id = 1)
# starterbot's user ID in Slack: value is assigned after the bot starts up
starterbot_id = None

# constants
RTM_READ_DELAY = 1 # 1 second delay between reading from RTM
EXAMPLE_COMMAND = "do"
MENTION_REGEX = "^<@(|[WU].+?)>(.*)"


def trends(channel,message):
    msg=""
    count = 0
    slack_client.api_call(
        "chat.postMessage",
        channel="#general",
        text="Trends as of %s"%(dt.datetime.now()))  

    for i in results:
        for x in i["trends"]:
            count+=1
            if(count<11):   
                msg+=(x['name']+"\n")  

    if message=="trends":
        slack_client.api_call(
            "chat.postMessage",
            channel=channel,
            text=msg)

def daily_update():
    msg=""
    count = 0
    slack_client.api_call(
        "chat.postMessage",
        channel="#general",
        text="Trends as of %s"%(dt.datetime.now()))    
    for i in results:
        for x in i["trends"]:
            count+=1
            if(count<11):   
                msg+=(x['name']+"\n")  

    slack_client.api_call(
        "chat.postMessage",
        channel="#general",
        text=msg)


def parse_bot_commands(slack_events):
    """
        Parses a list of events coming from the Slack RTM API to find bot commands.
        If a bot command is found, this function returns a tuple of command and channel.
        If its not found, then this function returns None, None.
    """
    for event in slack_events:
        if event["type"] == "message" and not "subtype" in event:
            user_id, message = parse_direct_mention(event["text"])
            if user_id == starterbot_id:
                return message, event["channel"]
    return None, None

def parse_direct_mention(message_text):
    """
        Finds a direct mention (a mention that is at the beginning) in message text
        and returns the user ID which was mentioned. If there is no direct mention, returns None
    """
    matches = re.search(MENTION_REGEX, message_text)
    # the first group contains the username, the second group contains the remaining message
    return (matches.group(1), matches.group(2).strip()) if matches else (None, None)

def handle_command(command, channel):

    response = None

    if command.startswith(EXAMPLE_COMMAND):
        response = "Sure...write some more code then I can do that!"

    # Sends the response back to the channel
    slack_client.api_call(
        "chat.postMessage",
        channel='#general',
        text=response
    )

if __name__ == "__main__":
    if slack_client.rtm_connect(with_team_state=False):
        schedule.every().day.at("00:00").do(daily_update)
        print("Starter Bot connected and running!")
        # Read bot's user ID by calling Web API method `auth.test`
        starterbot_id = slack_client.api_call("auth.test")["user_id"]
        while True:
            command, channel = parse_bot_commands(slack_client.rtm_read())
            schedule.run_pending()
            if command:
                trends(channel,command)
            time.sleep(1)
    else:
        print("Connection failed. Exception traceback printed above.")