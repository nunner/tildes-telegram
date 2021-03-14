#!/usr/bin/python3

import conf as cfg
import feedparser
import telegram
import pickle
import re
import time
import os.path as path
from bs4 import BeautifulSoup

def get_votes(summary):
    p = re.compile("<p>Votes: [0-9]*<\/p>")
    matches = p.findall(summary)
    if matches[0]:
        matches[0] = matches[0].replace("<p>Votes: ", "").replace("</p>", "")
        return int(matches[0]) 
    else:
        return 0

def get_comments(summary):
    p = re.compile("<p>Comments: [0-9]*<\/p>")
    matches = p.findall(summary)
    if matches[0]:
        matches[0] = matches[0].replace("<p>Comments: ", "").replace("</p>", "")
        return int(matches[0]) 
    else:
        return 0

def build_menu(buttons,
        n_cols,
        header_buttons=None,
        footer_buttons=None):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, [header_buttons])
    if footer_buttons:
        menu.append([footer_buttons])
    return menu

def send(text, buttons):
    reply_markup = telegram.InlineKeyboardMarkup(build_menu(buttons, n_cols = 2))
    try:
        bot.sendMessage(chat_id=cfg.settings["bot"]["channel"],
                        text=text,
                        parse_mode=telegram.ParseMode.HTML,
                        reply_markup=reply_markup)
    except Exception:
        pass

def post(topic):
    vote_count = get_votes(topic["summary"])
    comment_count = get_comments(topic["summary"])

    if vote_count > cfg.settings["limit"] and topic["id"] not in post_list:
        button_list = []

        comments = "https://tild.es/" + topic["id"].split("/")[4]
        link = topic["link"]

        text = "<b>" + topic["title"] + "</b>\n\n"

        if topic["id"] != topic["link"]:
            text += "<b>Link:</b> " + link + "\n"
            text += "<b>Comments:</b> " + comments + "\n\n"

            button_list = [
                telegram.InlineKeyboardButton(text="Link", url=link),
                telegram.InlineKeyboardButton(text=str(comment_count) + " Comments", url=comments)]
        else:
            soup = BeautifulSoup(topic["summary"], "html.parser")
            text += "<b>Link:</b> " + comments + "\n\n"
            text += soup.find("p").getText()

            button_list = [
                    telegram.InlineKeyboardButton(text=str(comment_count) + " Comments", url=comments)]

        send(text, button_list)
        post_list.append(topic["id"])

if __name__ == "__main__":
    if path.exists("posts.p"):
        post_list = pickle.load(open("posts.p", "rb")) 
    else:
        post_list = []
    
    bot = telegram.Bot(token=cfg.settings["bot"]["token"])
    
    feeds = [];
    for board in cfg.settings["boards"]:
        url = "https://tildes.net/~" + board + "/topics.atom";
        feeds.append(feedparser.parse(url))
    
    for feed in feeds:
        for topic in feed.entries:
            post(topic)
    
    pickle.dump(post_list, open("posts.p", "wb"))
