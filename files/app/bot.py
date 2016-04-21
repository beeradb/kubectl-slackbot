from slackbot.bot import Bot
from slackbot.bot import listen_to
import re


def main():
    bot = Bot()
    bot.run()


@listen_to('kubectl (.*)')
def kubectl(message, something):
    message.reply('Here is {}'.format(something))


if __name__ == "__main__":
    main()
