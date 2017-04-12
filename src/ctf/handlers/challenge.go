package handlers

import (
	"ctf/config"
	"ctf/model"
	"ctf/utils"
	"encoding/json"
	"errors"
	"fmt"
	"github.com/gorilla/mux"
	"io/ioutil"
	"log"
	"net/http"
	"os"
	"regexp"
	"strconv"
	"time"
)

// exists returns whether the given file or directory exists or not
func exists(path string) (bool, error) {
	_, err := os.Stat(path)
	if err == nil {
		return true, nil
	}
	if os.IsNotExist(err) {
		return false, nil
	}
	return true, err
}

func getChallengeInfos(w http.ResponseWriter, r *http.Request) (challengeName string,
	challengeFolderPath string, challenge model.Challenge, err error) {
	vars := mux.Vars(r)
	challengeName = vars["challengeName"]

	regexChallName := regexp.MustCompile(`^[\w-]+$`)
	if !regexChallName.MatchString(challengeName) {
		w.WriteHeader(http.StatusNotFound)
		utils.SendResponseJSON(w, utils.NotFoundErrorMessage)
		err = errors.New("Challenge name not valid.")
		return
	}

	challengeFolderPath = config.BasePath + config.Conf.ChallengeFolder + challengeName + ".dir/"
	exists, err := exists(challengeFolderPath)
	if !exists || err != nil {
		w.WriteHeader(http.StatusNotFound)
		utils.SendResponseJSON(w, utils.NotFoundErrorMessage)
		if err == nil {
			err = errors.New("File Not Found.")
		} else {
			log.Printf("Cannot find folder : %v\n", err)
		}
		return
	}

	challengeJSON := challengeFolderPath + challengeName + ".json"
	challengeRaw, err := ioutil.ReadFile(challengeJSON)
	if err != nil {
		w.WriteHeader(http.StatusInternalServerError)
		utils.SendResponseJSON(w, utils.InternalErrorMessage)
		log.Printf("File error: %v\n", err)
		return
	}

	err = json.Unmarshal(challengeRaw, &challenge)
	if err != nil {
		w.WriteHeader(http.StatusInternalServerError)
		utils.SendResponseJSON(w, utils.InternalErrorMessage)
		log.Printf("File error: %v\n", err)
		return
	}
	return
}

func ChallengeShow(w http.ResponseWriter, r *http.Request) {
	challengeName, challengeFolderPath, challenge, err := getChallengeInfos(w, r)
	if err != nil {
		return
	}

	for index, language := range challenge.Languages {
		challengeFilePath := challengeFolderPath + challengeName + language.Extension
		challengeContent, err := ioutil.ReadFile(challengeFilePath)
		if err != nil {
			w.WriteHeader(http.StatusInternalServerError)
			utils.SendResponseJSON(w, utils.InternalErrorMessage)
			log.Printf("File error: %v\n", err)
			return
		}
		challenge.Languages[index].FileContent = string(challengeContent[:])
	}

	challenge.ResolvedConclusion = ""

	w.WriteHeader(http.StatusOK)
	utils.SendResponseJSON(w, challenge)
}

func ChallengeExecute(w http.ResponseWriter, r *http.Request) {
	challengeName, challengeFolderPath, challenge, err := getChallengeInfos(w, r)
	if err != nil {
		return
	}

	// TODO: change Challenge Model
	authenticatedChallenges := map[string]bool{
		"stored_xss": true,
	}

	registeredUser, user, _ := IsUserAuthenticated(w, r)
	if !registeredUser && authenticatedChallenges[challengeName] {
		w.WriteHeader(http.StatusForbidden)
		utils.SendResponseJSON(w, utils.Message{"You need to be logged in to execute this challenge"})
		return
	}

	var paramsRaw []byte
	var paramsJSON map[string]*json.RawMessage
	if err := utils.LoadJSONFromRequest(w, r, &paramsRaw); err != nil {
		return
	}
	_ = json.Unmarshal(paramsRaw, &paramsJSON)

	var language string
	paramJSONVal, ok := paramsJSON["language"]
	if !ok {
		w.WriteHeader(http.StatusBadRequest)
		utils.SendResponseJSON(w, utils.Message{"Missing language argument"})
		return
	}
	json.Unmarshal(*paramJSONVal, &language)

	args := make([]string, len(challenge.Parameters), len(challenge.Parameters)+1)

	for index, arg := range challenge.Parameters {
		paramJSONVal, ok := paramsJSON[arg.Name]
		if !ok {
			args[index] = ""
			continue
		}
		if err := json.Unmarshal(*paramJSONVal, &(args[index])); err != nil {
			args[index] = ""
		}
	}

	if authenticatedChallenges[challengeName] { // Inject User email
		args = append([]string{user.Email}, args...)
	}

	out, err := RunExploitation(
		challengeName,
		language,
		challengeFolderPath,
		args,
	)

	if err != nil {
		w.WriteHeader(http.StatusInternalServerError)
		encouragingMessage := fmt.Sprintf("Looks like your request failed.. Here is your error : \"%v : %s\"", err, out)
		utils.SendResponseJSON(w, utils.Message{encouragingMessage})
		log.Printf("%v : %s\n", err, string(out[:]))
		return
	}

	w.WriteHeader(http.StatusOK)
	utils.SendResponseJSON(w, utils.Message{string(out[:])})
}

// Check if the submitted "secret" is the right one
func ChallengeValidate(w http.ResponseWriter, r *http.Request) {
	challengeName, challengeFolderPath, challenge, err := getChallengeInfos(w, r)
	if err != nil {
		return
	}
	var secretRaw []byte
	var secretJSON map[string]*json.RawMessage
	if err := utils.LoadJSONFromRequest(w, r, &secretRaw); err != nil {
		return
	}
	if err := json.Unmarshal(secretRaw, &secretJSON); err != nil {
		w.WriteHeader(http.StatusBadRequest)
		utils.SendResponseJSON(w, utils.BadRequestMessage)
		log.Println(err)
		return
	}

	secret := ""
	secretJSONVal, ok := secretJSON["secret"]
	if ok {
		if err := json.Unmarshal(*secretJSONVal, &secret); err != nil {
			w.WriteHeader(http.StatusBadRequest)
			utils.SendResponseJSON(w, utils.BadRequestMessage)
			log.Println(err)
			return
		}
	}
	realSecret, err := ioutil.ReadFile(challengeFolderPath + config.Conf.FlagFileName)
	if secret != string(realSecret[:]) {
		message := "Not the good secret sorry. Be carefull with spaces when copy-pasting."
		w.WriteHeader(http.StatusNotAcceptable)
		utils.SendResponseJSON(w, utils.Message{message})
		return
	}

	registeredUser, user, err := IsUserAuthenticated(w, r)
	if err != nil {
		w.WriteHeader(http.StatusUnauthorized)
		utils.SendResponseJSON(w, utils.Message{"Your session seems expired, please logout and login again to register your points"})
		return
	}

	var message string
	message, err = updateValidatedChallenge(true, challengeName, challenge, user, registeredUser)
	if err != nil {
		w.WriteHeader(http.StatusInternalServerError)
		utils.SendResponseJSON(w, utils.InternalErrorMessage)
		return
	}

	w.WriteHeader(http.StatusOK)
	utils.SendResponseJSON(w, utils.Message{message})
}

func ChallengeCorrect(w http.ResponseWriter, r *http.Request) {
	challengeName, challengeFolderPath, challenge, err := getChallengeInfos(w, r)
	if err != nil {
		return
	}

	var correction model.CorrectedScript
	var correctionRaw []byte
	err = utils.LoadJSONFromRequest(w, r, &correctionRaw)
	if err != nil {
		return
	}
	err = json.Unmarshal(correctionRaw, &correction)
	if err != nil {
		utils.SendResponseJSON(w, utils.BadRequestMessage)
		log.Println(err)
		return
	}

	out, status, err := RunCorrection(
		challengeFolderPath,
		correction.ContentScript,
		correction.Language,
	)

	if err != nil {
		if status == STATUS_TIMED_OUT {
			w.WriteHeader(http.StatusInternalServerError)
			utils.SendResponseJSON(w, utils.Message{out})
			log.Printf("%v", err)
			return
		}
		w.WriteHeader(http.StatusNotAcceptable)
		encouragingMessage := fmt.Sprintf("Looks like your script is not perfect yet. Here is your error : \"%s\"", out)
		utils.SendResponseJSON(w, utils.Message{encouragingMessage})
		log.Printf("%v", err)
		return
	}

	registeredUser, user, err := IsUserAuthenticated(w, r)
	if err != nil {
		w.WriteHeader(http.StatusUnauthorized)
		utils.SendResponseJSON(w, utils.Message{"Your session seems expired, please logout and login again to register your points"})
		return
	}

	var message string
	message, err = updateValidatedChallenge(false, challengeName, challenge, user, registeredUser)
	if err != nil {
		w.WriteHeader(http.StatusInternalServerError)
		utils.SendResponseJSON(w, utils.InternalErrorMessage)
		return
	}

	w.WriteHeader(http.StatusOK)
	utils.SendResponseJSON(w, utils.Message{message})
}

func updateValidatedChallenge(exploited bool, challengeName string, challenge model.Challenge,
	user model.User, registeredUser bool) (message string, err error) {

	if !registeredUser {
		message = fmt.Sprintf(
			"Congratz !! You did it :)\nYou did not earned any points because you're not logged in.\n%s",
			challenge.ResolvedConclusion,
		)
		return
	}

	var alreadyValidated model.ValidatedChallenge
	notFound := db.Where(
		&model.ValidatedChallenge{
			ChallengeID: challengeName,
			UserID:      strconv.Itoa(int(user.ID)),
		},
	).First(
		&alreadyValidated,
	).RecordNotFound()

	if !notFound {
		message = "Congratz !! You did it :) But you already %s this challenge, so no points this time.\n%s"
		if exploited && alreadyValidated.IsExploited {
			message = fmt.Sprintf(message, "exploited", challenge.ResolvedConclusion)
			return
		} else if !exploited && alreadyValidated.IsCorrected {
			message = fmt.Sprintf(message, "corrected", challenge.ResolvedConclusion)
			return
		}
	}

	if !notFound {
		if exploited {
			// we found the validatedChallenge object but it wasn't exploited,
			// the user just corrected the challenge, and now he exploits it
			alreadyValidated.IsExploited = true
		} else {
			// we found the validatedChallenge object but it wasn't corrected,
			// the user just exploited the challenge, and now he corrects it
			alreadyValidated.IsCorrected = true
		}
		if err = db.Save(&alreadyValidated).Error; err != nil {
			log.Printf("%v\n", err)
			return
		}
	} else {
		newValidatedChall := model.ValidatedChallenge{
			ChallengeID:   challengeName,
			UserID:        strconv.Itoa(int(user.ID)),
			IsExploited:   exploited,
			IsCorrected:   !exploited,
			DateValidated: time.Now(),
		}
		// this is a new validatedChallenge
		if err = db.Create(&newValidatedChall).Error; err != nil {
			log.Printf("%v\n", err)
			return
		}
	}
	message = "Congratz !! You did it :)\n" + challenge.ResolvedConclusion
	return
}

func GetChallenges() (challenges model.Challenges, err error) {

	challengesPath := config.BasePath + "challenges.json"

	challengesRaw, err := ioutil.ReadFile(challengesPath)
	if err != nil {
		log.Printf("File error: %v\n", err)
		return
	}

	err = json.Unmarshal(challengesRaw, &challenges)
	if err != nil {
		log.Printf("File error: %v\n", err)
		return
	}
	return challenges, err
}

func ChallengeShowAll(w http.ResponseWriter, r *http.Request) {

	challenges, err := GetChallenges()
	if err != nil {
		w.WriteHeader(http.StatusInternalServerError)
		utils.SendResponseJSON(w, utils.InternalErrorMessage)
		return
	}

	w.WriteHeader(http.StatusOK)
	utils.SendResponseJSON(w, challenges)
}
