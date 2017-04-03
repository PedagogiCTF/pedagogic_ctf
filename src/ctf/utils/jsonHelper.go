package utils

import (
	"encoding/json"
	"io"
	"io/ioutil"
	"log"
	"net/http"
)

type Message struct {
	Message string `json:"message"`
}

func SendResponseJSON(w http.ResponseWriter, object interface{}) {
	if err := json.NewEncoder(w).Encode(object); err != nil {
		w.WriteHeader(http.StatusInternalServerError)
		json.NewEncoder(w).Encode(InternalErrorMessage)
		log.Println(err)
	}
}

func LoadJSONFromRequest(w http.ResponseWriter, r *http.Request, body *[]byte) (err error) {
	response := BadRequestMessage
	(*body), err = ioutil.ReadAll(io.LimitReader(r.Body, 200000))
	if err != nil {
		log.Println(err)
		w.WriteHeader(http.StatusBadRequest)
		SendResponseJSON(w, response)
		return
	}
	err = r.Body.Close()
	if err != nil {
		log.Println(err)
		w.WriteHeader(http.StatusBadRequest)
		SendResponseJSON(w, response)
		return
	}
	return
}
