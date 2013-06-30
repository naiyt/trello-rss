"""
trello-rss - A Python module for creating an RSS feed for your Trello boards.
Written by Nate Collings
Last Update: June 30, 2013

Usage: python trello-rss.py <number of items>

Required: 

sarumont's py-trello Trello API Wrapper:
https://github.com/sarumont/py-trello

PyRSS2Gen:
https://pypi.python.org/pypi/PyRSS2Gen

recent.py - Used to actually retrieve recent updates. Included.

A Trello API Key and token for the boards to view:
https://trello.com/1/appKey/generate
https://trello.com/docs/gettingstarted/index.html#getting-a-token-from-a-user

Put the key and token in config.py

"""

import datetime
import config
import PyRSS2Gen
from trello import TrelloClient
from recent import Recent
import sys


class KeyTokenErr(Exception):
    """Used if the key and token haven't been defined"""
    pass


class Channel:
    """Used to create the RSS channel object"""
    def __init__(self, title, link, description):
        self.title = title
        self.link = link
        self.description = description

class Item:
    """
    An Item containing the info for a specific RSS item.
    Takes in the title, link, description, and date, and uses them
    to create the RSSItem with PyRSS2Gen, which is stored in
    self.item

    """

    def __init__(self, title, link, description, date):
        self.title = title
        self.link = link
        self.description = description
        self.date = date
        self.item = self.create_item()

    def create_item(self):
        """Creates the RSSItem object"""
        return PyRSS2Gen.RSSItem(title=self.title,link=self.link,description=self.description,
                guid=self.link,pubDate=self.date)
        

class RSSObj:
    """
    Takes your channel info and a list of items, and creates the actual
    RSS XML using PyRSS2Gen. By default it will list all items EVER, but you
    can restrict them by specifying num in the parameters.

    """
    
    def __init__(self, channel, items, num=-1):
        self.channel = channel
        self.items = items
        self.total_items = num
        self.rss = self.create_rss()

    def create_rss(self):
        """
        Sorts the list according to date, then creates the actual
        RSS object that can be  used to output your feed. If you don't
        specify num, it returns all news items.
    
        """

        sorted_items = sorted(self.items, key=lambda date: date.pubDate, reverse=True)
        if self.total_items != -1:
            sorted_items = sorted_items[:self.total_items]
        return PyRSS2Gen.RSS2(title=self.channel.title,link=self.channel.link,
                description=self.channel.description,lastBuildDate=datetime.datetime.now(),
                items=sorted_items)


def create_trello_url(url_type, board_id, card_id=None):
    """Should probably add this to the API module instead..."""
    if card_id is None:
        return "https://trello.com/%s/%s" % (url_type, board_id)
    else:
        return "https://trello.com/%s/%s/%s" % (url_type, board_id, card_id)


def get_items(outfile, num):
    """
    Creates a Recent object, and gets a list of new cards, boards, lists
    and comments. Creates the RSS Item objects with each, then creates the
    full RSS object and outputs it to outfile.
   
   
    TODO:
    -Add support for getting information on all other types of Trello actions.
    (Need to update the Recent module for that to.) Could get a bit messy,
    might want to rethink the loop for snagging the action info.
    -Error checking
    -Better url building

    """

    my_updates = Recent(config.api_key,config.token)
    items = ['cards', 'boards', 'lists', 'comments']
    # Retrieves ALL updates for the items listed above
    # Could possibly be more restrictive, for performance
    all_items = [my_updates.fetch_item(item) for item in items]


    item_objs = []
    for item in all_items:
        for entity in item:
            for sub in entity:
                name = sub['memberCreator']['fullName']
                board = sub['data']['board']['name']
                board_id = sub['data']['board']['id']
                date = my_updates.create_date(sub['date'])

                card = None
                comment = None
                list_name = None
                title = ""
                description = ""
                url = ""
                
                # Could probably do th is a bit cleaner
                if sub['type'] == 'commentCard':
                    card = sub['data']['card']['name']
                    card_id = sub['data']['card']['id']
                    comment = sub['data']['text']
                    title = "%s commented on '%s' in %s" % (name, card, board)
                    description = comment
                    # Card urls can be accessed at trello.com/boardid/cardid
                    url = create_trello_url('card', board_id, card_id)
                elif sub['type'] == 'createCard':
                    card = sub['data']['card']['name']
                    card_id = sub['data']['card']['id']
                    title = "%s created a new card '%s' in %s" % (name, card, board)
                    url = create_trello_url('card', board_id, card_id)
                elif sub['type'] == 'createBoard':
                    title = "%s created a new board - %s" % (name, board)
                    url = create_trello_url('board', board_id)
                elif sub['type'] == 'createList':
                    list_name = sub['data']['list']['name']
                    title = "%s created a new list -- %s in %s" % (name, list_name, board)
                    url = create_trello_url('board', board_id)

                item_objs.append(Item(title, url, description, date).item)

    my_channel = Channel(config.rss_channel_title, config.rss_channel_link, config.description)
    rss = RSSObj(my_channel, item_objs, num).rss
    rss.write_xml(open(outfile,"w"))



usage = "Usage: trello-rss.py <outfile> <number of items>"
key_token_err = "Please enter you API key and Token in config.py"
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print usage
        exit()
    else:
        if config.api_key == "" or config.token == "":
            raise KeyTokenErr(key_token_err)
        get_items(sys.argv[1], int(sys.argv[2]))

