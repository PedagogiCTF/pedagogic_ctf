package main

import (
	"ctf/config"
	"ctf/handlers"
	"ctf/router"
	"fmt"
	"log"
	"net/http"
)

func main() {
	log.SetFlags(log.LstdFlags | log.Lshortfile)

	config.InitConfig()

	handlers.InitDB(
		"postgres",
		fmt.Sprintf("host=%s user=%s dbname=pedagogic_ctf sslmode=disable password=%s",
			config.Conf.DBHost, config.Conf.DBUser, config.Conf.DBPass))
	handlers.Migrate()

	log.Fatal(http.ListenAndServe("0.0.0.0:8080", router.NewRouter()))
}
