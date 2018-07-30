package main

import (
	"ctf/config"
	"ctf/handlers"
	"ctf/router"
	"log"
	"net/http"
	"flag"
)

func main() {
	cfgFlg := flag.String("config", "config.json", "The path to the configuration file")
	flag.Parse()

	log.SetFlags(log.LstdFlags | log.Lshortfile)

	config.InitConfig(*cfgFlg)

	handlers.InitDB("postgres", config.Conf.DataSourceName)
	handlers.Migrate()

	log.Fatal(http.ListenAndServe(config.Conf.ListenOn, router.NewRouter()))
}
