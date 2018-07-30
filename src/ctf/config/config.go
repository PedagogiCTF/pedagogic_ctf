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
	IsProduction    bool
	BasePath        string
	ListenOn        string
	DataSourceName  string
}

func InitConfig(configPath string) {
	file, err := os.Open(configPath)
	if err != nil {
		log.Println(err)
	}
	decoder := json.NewDecoder(file)
	if err = decoder.Decode(&Conf); err != nil {
		panic(err)
	}
}
