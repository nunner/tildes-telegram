import conf as cfg
import tildee
import telegram
import re
import pickle
import time

def clean(raw_html):
    return re.sub(r"<.*?>|b'|\\n|\s{2,}|\\|'$", "", raw_html)

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

def post(board):
    topics = client.fetch_topic_listing("~" + board)

    for topic in topics:
        if topic.num_votes > cfg.settings["limit"] and topic.id36 not in post_list:
            post_link = "https://tild.es/" + str(topic.id36);
            button_list = []

            text = "<b>" + topic.title + "</b>\n\n"

            if topic.link:
                text += "<b>Link:</b> " + topic.link + "\n"
                text += "<b>Comments:</b> " + post_link + "\n\n"

                button_list = [
                        telegram.InlineKeyboardButton(text="Link", url=topic.link),
                        telegram.InlineKeyboardButton(text=str(topic.num_comments) + " Comments", url=post_link)]
            else:
                text += "<b>Link:</b> " + post_link + "\n\n"
                text += clean(topic.content_html)

                button_list = [
                        telegram.InlineKeyboardButton(text=str(topic.num_comments) + " Comments", url=post_link)]

            reply_markup = telegram.InlineKeyboardMarkup(build_menu(button_list, n_cols = 2))
            try:
                bot.sendMessage(chat_id=cfg.settings["bot"]["channel"],
                    text=text,
                    parse_mode=telegram.ParseMode.HTML,
                    reply_markup=reply_markup)
            except Exception:
                pass
            time.sleep(4)
            post_list.append(topic.id36)

post_list = pickle.load(open("posts.p", "rb")) 

client = tildee.TildesClient(username = cfg.settings["user"]["name"], password=cfg.settings["user"]["pass"])
bot = telegram.Bot(token=cfg.settings["bot"]["token"])

for board in cfg.settings["boards"]:
    post(board)

pickle.dump(post_list, open("posts.p", "wb"))
print("I'm here")
