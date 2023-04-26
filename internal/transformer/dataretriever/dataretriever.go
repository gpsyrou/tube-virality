package dataretriever

import (
	"log"

	"github.com/PuerkitoBio/goquery"
)

type dataRetriever struct {
	url   string
	bsoup *goquery.Document
}

func NewDataRetriever(videoUrl string) *dataRetriever {
	videoBsoup, err := goquery.NewDocument(videoUrl)
	if err != nil {
		log.Fatal(err)
	}

	return &dataRetriever{
		url:   videoUrl,
		bsoup: videoBsoup,
	}
}

func (t *dataRetriever) MetaContentTags() *goquery.Selection {
	return t.bsoup.Find("meta")
}
