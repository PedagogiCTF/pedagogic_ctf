package model

type CorrectedScript struct {
	Language      string `json:"language"` // ex : .py or .go
	ContentScript string `json:"content_script"`
}
