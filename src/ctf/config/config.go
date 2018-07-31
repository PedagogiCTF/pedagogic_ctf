package config

import "os"

var Conf *Configuration

type Configuration struct {
	LocalDiskLabel string

	DBHost string
	DBUser string
	DBPass string
}

func InitConfig() {
	localDiskLabel, ok := os.LookupEnv("LOCAL_DISK_LABEL")
	if !ok {
		localDiskLabel = "/dev/sda"
	}

	dbHost, ok := os.LookupEnv("DB_HOST")
	if !ok {
		dbHost = "localhost"
	}

	dbUser, ok := os.LookupEnv("DB_USER")
	if !ok {
		dbUser = "root"
	}

	dbPass, ok := os.LookupEnv("DB_PASS")
	if !ok {
		dbPass = ""
	}

	Conf = &Configuration{
		LocalDiskLabel: localDiskLabel,
		DBHost:         dbHost,
		DBUser:         dbUser,
		DBPass:         dbPass,
	}
}
