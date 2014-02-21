"""
recent.py - Used for trello-rss to grab recent Trello updates on your account
Written by Nate Collings

TODO:
- Currently just retrieves ALL it can given a specific token. Add support for just getting
  updates for certain boards, public or otherwise. The current process just filters it out later.

"""

import config
from trello import TrelloClient
from datetime import datetime


class InvalidItem(Exception):
    """Raised when a user calls for an item that is not supported"""
    pass


class Recent:
    """
    Class used to retrieve recent Trello updates. Uses sarumont's py-trello API wrapper lightly.
    Currently I just grab the full lump of data from the board API call. 
    
    For my use of Trello this works just fine, but if you're using it really 
    heavily I could see this using up too much memory, or the resultant xml being too big or something.
    Could improve that by specifying exactly what we want with the ?filter param, or digging into using
    the lists/cards apis more directly. However, I'm currently serving over 100 rss feeds on 
    trellorss.appspot.com with this method, so it works well enough, even if it kind of bothers me.

    """

    def __init__(self, api_key, token=None, board_id=None, public_board=False, all_private=False):
        self.api_key = api_key
        self.token = token
        self.public_only = False
        if self.token is None:
            self.public_only = True
        self.trello = TrelloClient(self.api_key, self.token)
        self.boards = None # Lazy, so doesn't fetch until we ask for them
        self.board_id = board_id
        self.public_board = public_board
        self.all_private = all_private

        # A list of items currently supported. The user should pass in one of the keys below,
        # and we use the values when passing it to the Trello API.
        self.items = config.all_item_types


    def create_date(self, date):
        return datetime.strptime(date[:-5], '%Y-%m-%dT%H:%M:%S')

    def fetch_items(self, item_names):
        """ Fetch the specified recent activity for item_names """

        for item in item_names:
            if item not in self.items:
                raise InvalidItem("%s is not a supported item." % item)
        items = ','.join([self.items[item] for item in item_names])
        if self.all_private:
            return self._get_activity(items, None)
        else:
            return self._get_activity(items, self._get_boards())

    def _get_boards(self):
        """ Calls the list_boards() method if we haven't already """
        if self.board_id:
            self.boards = self.trello.get_board(self.board_id)
        elif self.boards is None:
            self.boards = self.trello.list_boards()
        return self.boards

    def _get_activity(self, action_filter, boards):
        """Given a action filter, returns those actions for boards from the Trello API"""
        actions = []
        if self.all_private:
            self.trello.info_for_all_boards(action_filter)
            actions.append(self.trello.all_info)
        else:
            if isinstance(boards, list) is False:
                boards = [boards]
            for board in boards:
                if board.closed is False:
                    board.fetch_actions(action_filter)
                    if len(board.actions) > 0:
                        actions.append(board.actions)
        return actions