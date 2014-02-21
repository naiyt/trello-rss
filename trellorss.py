"""
trello-rss - A Python module for creating an RSS feed for your Trello boards.
Written by Nate Collings

Required: 

sarumont's py-trello Trello API Wrapper:
https://github.com/sarumont/py-trello

PyRSS2Gen:
https://pypi.python.org/pypi/PyRSS2Gen

A Trello API Key and token for the boards to view:
https://trello.com/1/appKey/generate
https://trello.com/docs/gettingstarted/index.html#getting-a-token-from-a-user

"""

import datetime
import config
import PyRSS2Gen
from recent import Recent
import xml.dom.minidom

class Channel:
    """Used to create the RSS channel object"""
    def __init__(self, title, link, description):
        self.title = title
        self.link = link
        self.description = description

class Item:
    """
    Containes the info for a specific RSS item. Creates a PyRSS2Gen object and
    stores it in self.item.

    """

    def __init__(self, title, link, description, date):
        self.title = title
        self.link = link
        self.description = description
        self.date = date
        self.item = self.create_item()

    def create_item(self):
        """Creates the RSSItem object"""
        return PyRSS2Gen.RSSItem(
            title=self.title,
            link=self.link,
            description=self.description,
            guid=self.link,
            pubDate=self.date)
        

class RSSObj:
    """
    Takes your channel info and a list of items, and creates the actual
    RSS XML using PyRSS2Gen. By default it will list all items EVER, but you
    can restrict them by specifying the num parameter.

    """
    
    def __init__(self, channel, items, num=-1):
        self.channel = channel
        self.items = items
        self.total_items = num
        self.rss = self.create_rss()

    def create_rss(self):
        """
        Sorts the list according to date, then creates the actual
        RSS object that can be  used to output your feed.
    
        """

        sorted_items = sorted(self.items, key=lambda date: date.pubDate, reverse=True)
        if self.total_items != -1:
            sorted_items = sorted_items[:self.total_items] # Restrict number of items
        rss_obj = PyRSS2Gen.RSS2(
            title=self.channel.title,
            link=self.channel.link,
            description=self.channel.description,
            lastBuildDate=datetime.datetime.now(),
            items=sorted_items)
        rss_obj = xml.dom.minidom.parseString(rss_obj.to_xml()) # Prettify
        return rss_obj.toprettyxml()


DEFAULT_TITLE = 'My Trello RSS Feed'
DEFAULT_LINK = 'http://trello.com'
DEFAULT_DESC = 'Trello RSS Feed'

class TrelloRSS:
    def __init__(self, key, token=None, channel_title=None, rss_channel_link=None, description=None):
        self.key = key
        if token is None:
            self.public_only = True
        else:
            self.public_only = False
        self.channel_title = DEFAULT_TITLE if channel_title is None else channel_title
        self.rss_channel_link = DEFAULT_LINK if rss_channel_link is None else rss_channel_link
        self.description = DEFAULT_DESC if description is None else description
        self.token = token
        self.all_items = config.all_item_types
        self.description = description
        self.channel_obj = Channel(self.channel_title,self.rss_channel_link,self.description)

    def get_all(self,num=15, items=None):
        """Returns an RSS object with specified info for all boards associated with their token"""
        if self.public_only:
            print "Notice: This TrelloRSS object can only view public boards. Pass in a token to read private ones."
            return None
        else:
            if items is None:
                items = self.all_items.keys()
            self._get_items(num,items,all_private=True)           
                
            return self.rss

    def get_only(self,items,num=15):
        if self.public_only:
            print "Notice: This TrelloRSS object can only view public boards. Pass in a token to read private ones."
            return None
        else:
            self._get_items(num,items)
            return self.rss

    def get_from(self, board_id ,public_board=False, items=None, num=15):
        if items is None:
            items = self.all_items
        self._get_items(num, items, board_id, public_board)

    def _get_items(self, num, items=None, board_id=None, public_board=False, all_private=False):
        """ Creates a Recent object, and gets recent actions for 'items' (default is all) """

        if items is None:
            items = self.all_items
        
        if self.token and public_board is False:
            my_updates = Recent(
                self.key,
                self.token,
                all_private=all_private,
                board_id=board_id
            )
        else:
            my_updates = Recent(
                self.key,
                board_id=board_id,
                public_board=public_board
            )

        # TODO - be more restrictive. Fetchs ALL actions for all items, which we sort through later.
        # Kind of icky.
        all_items = my_updates.fetch_items(items)

        item_objs = []
        for item in all_items:
            for entity in item:
                if 'memberCreator' not in entity:
                    entity = entity['actions']
                    for sub in entity:                  
                        curr_item = self._create_item(sub,item,my_updates)
                        item_objs.append(curr_item)
                else:
                    curr_item = self._create_item(entity,item,my_updates)
                    item_objs.append(curr_item)
        item_objs = [x for x in item_objs if x is not None]
        rss = RSSObj(self.channel_obj, item_objs, num).rss
        self.rss = rss

    def _create_item(self,item_info,items,updates_obj):
        """ TODO: Refactor this method so it isn't so terrible. Seriously, just look at it. Gross. """

        name = item_info['memberCreator']['fullName']
        board = item_info['data']['board']['name']
        board_id = item_info['data']['board']['id']
        date = updates_obj.create_date(item_info['date'])

        card = None
        comment = None
        list_name = None
        title = ""
        description = ""
        url = ""
        
        # Recent should have ONLY passed back the items we chose,
        # So we don't need to worry about checking to see if we
        # actually need these or not here.
        if item_info['type'] == 'commentCard':
            card = item_info['data']['card']['name']
            try:
                card_id = item_info['data']['card']['idShort']
            except KeyError:
                card_id = item_info['data']['card']['id']
            comment = item_info['data']['text']
            title = "%s commented on '%s' in %s" % (name, card, board)
            description = comment
            # Card urls can be accessed at trello.com/boardid/cardid
            url = self._create_trello_url('card', board_id, card_id)
        elif item_info['type'] == 'createCard':
            card = item_info['data']['card']['name']
            try:
                card_id = item_info['data']['card']['idShort']
            except KeyError:
                card_id = item_info['data']['card']['id']
            title = "%s created a new card '%s' in %s" % (name, card, board)
            url = self._create_trello_url('card', board_id, card_id)
        elif item_info['type'] == 'createBoard':
            title = "%s created a new board - %s" % (name, board)
            url = self._create_trello_url('board', board_id)
        elif item_info['type'] == 'createList':
            list_name = item_info['data']['list']['name']
            title = "%s created a new list -- %s in %s" % (name, list_name, board)
            url = self._create_trello_url('board', board_id)
        elif item_info['type'] == 'addChecklistToCard':
            card = item_info['data']['card']['name']
            try:
                card_id = item_info['data']['card']['idShort']
            except KeyError:
                # There seems to be an issue with short ID's on some calls
                card_id = item_info['data']['card']['id']
            checklist_name = item_info['data']['checklist']['name']
            title = "%s created a new checklist '%s' in %s" % (name,  checklist_name, card)
            url = self._create_trello_url('card', board_id, card_id)
        elif item_info['type'] == 'updateCard' and 'listBefore' in item_info['data'] and 'listAfter' in item_info['data']:
            list_before = item_info['data']['listBefore']['name']
            list_after = item_info['data']['listAfter']['name']
            card = item_info['data']['card']['name']
            try:
                card_id = item_info['data']['card']['idShort']
            except KeyError:
                card_id = item_info['data']['card']['id']
            url = self._create_trello_url('card', board_id, card_id)
            title = "%s moved '%s' from '%s' to '%s'" % (name, card, list_before, list_after)
        elif item_info['type'] == 'updateCheckItemStateOnCard':
            card = item_info['data']['card']['name']
            try:
                card_id = item_info['data']['card']['idShort']
            except KeyError:
                card_id = item_info['data']['card']['id']
            try:
                checklist_name = item_info['data']['checklist']['name']
            except:
                # Some calls don't seem to have the checklist name oddly enough
                checklist_name = '??'
            checked = False
            if item_info['data']['checkItem']['state'] == 'complete':
                checked = True
            check_item_name = item_info['data']['checkItem']['name']
            title = ''
            if checked:
                title = "%s completed %s in the %s checklist on %s" % (name, check_item_name,
                        checklist_name, card)
            else:
                title = "%s unchecked %s in the %s checklist on %s" % (name, check_item_name,
                        checklist_name, card)
            url = self._create_trello_url('card', board_id, card_id)

        else:
            return None

        return Item(title, url, description, date).item

    def _create_trello_url(self,url_type, board_id, card_id=None):
        if card_id is None:
            return "https://trello.com/%s/%s" % (url_type, board_id)
        else:
            return "https://trello.com/%s/%s/%s" % (url_type, board_id, card_id)

