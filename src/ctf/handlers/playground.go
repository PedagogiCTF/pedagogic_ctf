package handlers

import (
	"ctf/model"
	"ctf/utils"
	"encoding/json"
	"log"
	"net/http"
)

func PlaygroundExecute(w http.ResponseWriter, r *http.Request) {

	var snippet model.CorrectedScript
	var snippetRaw []byte
	err := utils.LoadJSONFromRequest(w, r, &snippetRaw)
	if err != nil {
		return
	}

	err = json.Unmarshal(snippetRaw, &snippet)
	if err != nil {
		utils.SendResponseJSON(w, utils.BadRequestMessage)
		log.Println(err)
		return
	}

	output, err := RunSnippet(snippet.ContentScript, snippet.Language)
	if err != nil {
		utils.SendResponseJSON(w, utils.InternalErrorMessage)
		return
	}

	w.WriteHeader(http.StatusOK)
	utils.SendResponseJSON(w, utils.Message{output})
}
