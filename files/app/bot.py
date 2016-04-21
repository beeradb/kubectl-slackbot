#-*- coding: utf-8 -*-
import subprocess
import os
import shlex
import time
from slackclient import SlackClient


def main():
    token = "faketoken"# found at https://api.slack.com/web#authentication
    sc = SlackClient(token)
    if sc.rtm_connect():
        while True:
            message = sc.rtm_read()
            if message:
                print message[0]['type']
                if message[0]['type'] is 'message':
                    print "yay2"

            time.sleep(1)
    else:
        print "Connection Failed, invalid token?"

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
        print "running command {cmd}".format(cmd=cmd)
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

