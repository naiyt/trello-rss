# trello-rss

Trello is a great app, but unfortunately doesn't currently have any RSS feed features. If they decided to add it in the future, all the better. However, based on [this] (https://trello.com/card/rss-feeds/4d5ea62fd76aa1136000000c/898), it doesn't seem like a high priority (if they plan on it at all). That card has 114 votes, but was archived and hasn't been updated in months.

I decided to throw together some quick Python over the weekend to create an RSS feed for your Trello account. I personally find this useful, as I have a lot of Trello boards, but I don't always have Trello in an open browser window. This is particularly useful if you've got multiple group boards you are participating in, and would like to get a quick glance at what's happened over the past day or so, over all your boards.

## Dependencies

- Uses [sarumont's py-trello] (https://github.com/sarumont/py-trello/) API wrapper. However, I've made a few modifications, so please use [my fork of it] (https://github.com/naiyt/py-trello).
- [PyRSS2Gen] (https://pypi.python.org/pypi/PyRSS2Gen) is used to create the actual RSS object.
- Python 2.x. No Python 3 support right now.
- A [Trello API Key] (https://trello.com/1/appKey/generate) and [authentication token] (https://trello.com/docs/gettingstarted/index.html#getting-a-token-from-a-user).

## API Key and Auth Token

You need an API Key to use the Trello API, and an auth token to let this app read your Trello boards. Get a key [here] (https://trello.com/1/appKey/generate) and instructions on getting a token [here] (https://trello.com/docs/gettingstarted/index.html#getting-a-token-from-a-user).

## Installation instructions

Until I get some packaging setup, the easiest thing for now is to just place this project, py-trello, and PyRSS2Gen in the same directory.

After doing so, open up `config.py` and enter your API key and auth token.

## Usage

Usage is pretty basic right now:

    python trello-rss.py <output file> <number of items>

It will output however many items you specify (sorted by newest) to your output file as RSS2. Currently it just retrieves `new cards`, `new boards`, `new lists`, and `new comments`. More features will be added, including the ability to choose what boards to give you a feed for, and expanded options for update types.

Once you get the resultant xml file, you can throw it up on your favorite hosting service and feed that into whatever RSS feed reader you personally love (as long as that's not Google Reader). You'll probably just want to setup a cron job to run trello-rss.py every 30 minutes or whatever.

## Overview

trello-rss.py creates a Recent object (from recent.py), and then uses Recent.fetch_item() to return items for each item type specified. (e.g., cards, boards, comments.) The items returned are JSON objects with the needed info to create the RSS. That info is extracted, and then an RSSObj object is created, with a list of the items we got from the Trello API. We then call RSSObj.create_rss(), which returns a PyGENRSS2 object, which we use to output our finalized XML.

The Recent class uses py-trello's TrelloClient class to retrieve info on all of your boards from the Trello API, filtered by the action we're looking for at the time (e.g., created cards, boards). The JSON objects returned by py-trello are passed to trello-rss.py to create and output the RSS.

## Security

This should be obvious, but figured I should at least mention it. If you've got important confidential info on your Trello board, this module currently will just read it all (if you give it the appropriate token, that is). If you then throw that feed onto some website, all that info is now publicly accessible (in theory). In the future I'll add support for only including specific boards in the feeds, but just keep that in mind for now.

## TODO

- Add tests
- Allow the user to specify which boards to provide feeds for
- Allow the user to create seperate feeds for each board
- Public board support
- Support for all other [possible actions] (https://trello.com/docs/api/board/index.html#get-1-boards-board-id)
- Allow the user to specify which of those to include in their feed

If you want to help out, I think the best help right now would be with supporting further actions, and allowing the user to specify which boards to follow. If that interests you, jump on in and then send off a pull request.
