#-*- coding: utf-8 -*-
import subprocess
import os
import shlex
import time
from slackclient import SlackClient


def main():
    token = os.environ.get('SLACK_API_TOKEN')# found at https://api.slack.com/web#authentication
    sc = SlackClient(token)
    if sc.rtm_connect():
        Dispatcher(sc)
    else:
        print("Connection Failed, invalid token?")

class Dispatcher:
    def __init__(self, sc):
        self.identifier = self.get_current_user_identifier(sc)
        self.sc = sc
        self.read()

    def read(self):
        while True:
            message = self.sc.rtm_read()
            if message and message[0]['type'] == 'message':
                   self.process_message(message[0])

            time.sleep(1)


    def process_message(self, message):
        if message['text'].startswith(self.identifier):
            cmd = message['text'].replace(self.identifier, '')
            output = "```{out}```".format(out=kubectl(cmd))
            self.sc.rtm_send_message(message['channel'], output)
            print(message)

    def get_current_user_identifier(self, sc):
        for user in sc.server.users:
            if user.name == sc.server.username:
                return '<@{user_id}>'.format(user_id=user.id)

        raise LookupError('Could not find bot user id')


def kubectl(command):
    """
    Run a kubect command and attempt to parse the results as json.
    :param command: the command to run
    """
    env = os.environ.copy()

    with open('/var/run/secrets/kubernetes.io/serviceaccount/token') as sa_token:
        token = sa_token.read()

    cmd = "/bin/kubectl {cmd} --token={token} --server={url} --insecure-skip-tls-verify=true".format(cmd=command, token=token, url=kube_api_url())


    # This will throw subprocess.CalledProcessError if the command fails.
    # Code that calls run_command should be in a try/except to handle the failure case.
    try:
        print("running command {cmd}".format(cmd=cmd))
        result = subprocess.check_output(cmd, env=env, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        return e.output

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

