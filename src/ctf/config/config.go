package config

import (
	"encoding/json"
	"log"
	"os"
)

var Conf *Configuration

type Configuration struct {
	LocalDiskLabel  string
	ChallengeFolder string
	FlagFileName    string
	Emails          string
	IsProduction    bool
}

func InitConfig() {

	file, err := os.Open(BasePath + "src/ctf/config/config.json")
	if err != nil {
		log.Println(err)
	}
	decoder := json.NewDecoder(file)
	if err = decoder.Decode(&Conf); err != nil {
		panic(err)
	}
}

const BasePath = "/home/admin/dev/pedagogic_ctf/"
