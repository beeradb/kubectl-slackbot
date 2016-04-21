#-*- coding: utf-8 -*-
from slackbot.bot import Bot
from slackbot.bot import listen_to
import subprocess
import os

def main():
    bot = Bot()
    bot.run()


@listen_to('kubectl (.*)')
def kubectl(message, kube_command):
    # slack converts double dashes into an emdash
    # so convert back before running.
    kube_command = kube_command.decode("utf-8").replace(u"\u2014", "--").encode("utf-8")
    print kube_command
    result = kubectl(kube_command)
    message.reply(result)


def kubectl(command):
    """
    Run a kubect command and attempt to parse the results as json.
    :param command: the command to run
    :param json: Whether or not to output results in json.
    :param env: The environment to use.
    :return: dict if parsed as json, raw output if not. Raises
             subprocess.calledProcessError on command fail.
    """
    env = os.environ.copy()

    with open('/var/run/secrets/kubernetes.io/serviceaccount/token') as sa_token:
        token = sa_token.read()

    cmd = "/bin/kubectl {cmd} --token={token} --server={url} --insecure-skip-tls-verify=true".format(cmd=command, token=token, url=kube_api_url())


    # This will throw subprocess.CalledProcessError if the command fails.
    # Code that calls run_command should be in a try/except to handle the failure case.
    result = subprocess.check_output(shlex.split(cmd), env=env, stderr=subprocess.STDOUT)

    return result


def kube_api_url():
    """
    Returns the kubernetes API url
    """
    return "https://{hostname}:{port}".format(
        hostname=os.environ['KUBERNETES_SERVICE_HOST'],
        port=os.environ['KUBERNETES_SERVICE_PORT']
    )

if __name__ == "__main__":
    main()

