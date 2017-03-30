package utils

import (
	"encoding/json"
	"log"
	"os"
)

type Configuration struct {
	Emails       string
	IsProduction bool
}

func GetConfig() *Configuration {
	file, err := os.Open(BasePath + "src/ctf/utils/config.json")
	if err != nil {
		log.Println(err)
	}
	decoder := json.NewDecoder(file)
	configuration := Configuration{}
	if err = decoder.Decode(&configuration); err != nil {
		log.Println(err)
	}
	return &configuration
}

const ChallengeFolder = "challs/"
const BasePath = "/home/admin/dev/pedagogic_ctf/"
const FlagFileName = "secret"
