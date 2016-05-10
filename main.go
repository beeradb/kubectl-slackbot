package main

import (
	"fmt"
	"io/ioutil"
	"os"
	"os/exec"
	"reflect"
	"strings"

	"github.com/mattn/go-shellwords"
	"github.com/nlopes/slack"
	"gopkg.in/yaml.v2"
)

type WhiteList struct {
	Users []string
}

func main() {
	api := slack.New(os.Getenv("SLACK_API_TOKEN"))
	rtm := api.NewRTM()

	whiteList := GetWhiteList()
	go rtm.ManageConnection()

	fmt.Println(reflect.TypeOf(api))
	var UserID string
Loop:
	for {
		select {
		case msg := <-rtm.IncomingEvents:
			switch ev := msg.Data.(type) {
			case *slack.HelloEvent:
				// Ignore hello

			case *slack.ConnectedEvent:
				UserID = ev.Info.User.ID

			case *slack.MessageEvent:
				username := fmt.Sprintf("<@%s>", UserID)
				fmt.Println(ev.User)
				if strings.Contains(ev.Text, username) {
					if CheckWhitelist(ev.User, whiteList, api) {
						ProcessMessage(ev, username, rtm, api)
					}
				}
			case *slack.InvalidAuthEvent:
				fmt.Printf("Invalid credentials")
				break Loop

			default:

			}
		}
	}
}

func ProcessMessage(ev *slack.MessageEvent, username string, rtm *slack.RTM, api *slack.Client) {
	command := strings.Trim(strings.TrimPrefix(ev.Text, username), " ")
	command = strings.Replace(command, "—", "--", -1)

	if command[0:1] == ":" {
		command = command[1:]
	}

	fmt.Println(command)
	result := kubectl(command)
	fmt.Println("len is ", strings.Count(result, "\n"))

	if strings.Count(result, "\n") > 80 {
		fmt.Println("Sending file")
		File(result, ev.Channel, api)
	} else {
		fmt.Println("Sending message")
		Message(result, ev.Channel, rtm)
	}
}

func GetWhiteList() WhiteList {
	var whiteList WhiteList
	buf, err := ioutil.ReadFile(os.Getenv("SLACK_WHITELIST_CONFIG"))

	if err != nil {
		return whiteList
	}

	yaml.Unmarshal(buf, &whiteList)
	fmt.Println(whiteList)
	return whiteList
}

func CheckWhitelist(userId string, whiteList WhiteList, api *slack.Client) bool {

	user, err := api.GetUserInfo(userId)
	if err != nil {
		fmt.Println("User not found.")
		// If there is no user then it certainly isn't whitelisted.
		return false
	}

	if len(whiteList.Users) == 0 {
		fmt.Println("No whitelist available.")
		// If no whitelist exists, then allow everything.
		return true
	}

	for _, name := range whiteList.Users {
		if name == user.Name {
			fmt.Println("found match")
			return true
		}
	}

	fmt.Println("Whitelist could not be matched for user: ", user.Name)
	return false
}

// Send a message to a slack channel using the real time messaging api.
func Message(result string, channel string, rtm *slack.RTM) {
	rtm.SendMessage(rtm.NewOutgoingMessage(fmt.Sprintf("```%s```", result), channel))
}

// Attach a result string as a file to a slack channel.
func File(result string, channel string, api *slack.Client) {
	params := slack.FileUploadParameters{
		Title:    "Kubectl result",
		Filetype: "shell",
		File:     "sh",
		Channels: []string{channel},
		Content:  result,
	}

	file, err := api.UploadFile(params)
	if err != nil {
		fmt.Printf("%s\n", err)
		return
	}
	fmt.Printf("Name: %s, URL: %s\n", file.Name, file.URL)
}

// Run an arbitrary string as a kubectl command.
func kubectl(command string) string {
	buf, err := ioutil.ReadFile("/var/run/secrets/kubernetes.io/serviceaccount/token")
	if err != nil {
		panic(err)
	}
	token := string(buf)

	caPath := "/var/run/secrets/kubernetes.io/serviceaccount/ca.crt"
	server := kube_api_url()
	shellCommand := fmt.Sprintf("%s --token=%s --server=%s --certificate-authority=%s", command, token, server, caPath)
	p := shellwords.NewParser()
	p.ParseBacktick = true
	args, err := p.Parse(shellCommand)

	if err != nil {
		return fmt.Sprintf("There was an error parsing your command")
	}

	cmdOut, err := exec.Command("/bin/kubectl", args...).Output()
	if err != nil {
		return fmt.Sprintf("There was an error running the kubectl command: ", err)
	}

	return string(cmdOut)
}

// Format the kubernetes API URL.
func kube_api_url() string {
	return fmt.Sprintf(
		"https://%s:%s",
		os.Getenv("KUBERNETES_SERVICE_HOST"),
		os.Getenv("KUBERNETES_SERVICE_PORT"),
	)
}
