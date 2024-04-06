# Slido Me First

A simple voting bot for the audience interaction tool Slido (sli.do) made in Python. Vote for your question as often as you like. Modified from davidlhw/slido-me-first to deal with changes made to the api, as well as to add the ability to vote for multiple questions at once, and vote for pre-existing questions, rather than creating new ones.

## Installation

Clone the project:
```bash
git clone https://github.com/CaptainBoggle/slido-escalate.git
```

Install dependencies:
```shell
python -m pip install -r requirements.txt
```
    
This project runs on Python version >= 3.7.6.

## Usage
To use the bot, you need the following:
*   Url to the Slido event
*   Question ids to vote for
*   Number of vote to add

### Running the bot

Simply copy the following to a terminal:

```
python vote.py -u <url> -v <vote count> -q <id1> <id2> ...
```

### Getting the required data
1.  Url to the Slido event

    This will be the same url that is sent to you by the presenter.
    It should look something like `https://app.sli.do/event/6PemAD91337cTVhxCsemg/live/questions`.

2.  Question to vote for

    This will be the question you wish to add the votes to.
    Use inspect element to find the question id. It should be a number like `84261027`,
    and can be found in the html of the respective question div as `data-qid`.

> Note:
>
> There is no limit to number of votes that you can add but the time taken to execute
> will scale linearly.
    

<br>

Have fun watching your questions get noticed!
