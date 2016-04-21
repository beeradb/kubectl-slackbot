# KubeCTL Slackbot

KubeCTL Slackbot is a bot based on [slackbot](https://github.com/lins05/slackbot) which allows you to run kubectl commands in slack.

## Install

To install on a running kubernetes cluster just create a slack API token and update the "SLACKBOT_API_TOKEN" environment var in the kubectl-deployment.yaml file. Once completed, just run the following:

```
kubectl create -f kubectl-deployment.yaml
```

Once running, invite the bot into a slack room and run commands as you normally would via kubectl.

## Coming soon

Currently this is alpha quality code which probably shouldn't be used for anything too serious. Future plans include the following

* Moving the SLACKBOT_API_TOKEN to a proper kubernetes secret
* Only allow whitelisted users to run kubectl commands
* More sane error handling (i.e. don't allow users to use -f flag for logs, and other stuff)
* Better handling of large outputs. I.e. only print the last N lines, or post it as a snippet.

