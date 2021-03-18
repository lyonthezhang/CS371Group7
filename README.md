# CS 371 Group 7: 20 Questions Bot

---

Welcome to our 20 Questions Bot (cities edition)! This bot will find the US city that you are thinking of. It will run an initial query of Wikidata to scrape a broad list of American cities. Then, it will narrow this list by asking you yes/no questions and adding to the query string based on the answers given to it. In 20 questions or less, it will tell you what it thinks the city you are thinking of is.

---

# Usage

First clone the repo:
`git clone https://github.com/lyonthezhang/CS371Group7.git`

cd into the repo and install requirements:
`pip install -r requirements.txt`

Run the bot, which is just a python script, from the terminal:
`python3 questionsbot.py`

The bot will ask questions now. Please answer in the terminal with a lowercase 'y' for yes and 'n' for no.

Notes:
- The bot may sometimes fail with HTTP Error 429: Too Many Requests. This is outside of our control, so please run the bot again.
- If the bot fails to return the proper result, it may be because of the limiting size of our query. This was done for performance purposes, as larger query sizes were infeasible to demonstrate. To fix this, please open constants.py and change the value SAMPLE_SIZE to the desired value. Warning: The default value is 10 and queries too large may slow the bot to a crawl.
