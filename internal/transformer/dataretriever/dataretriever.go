package dataretriever

import (
	"log"

	"github.com/PuerkitoBio/goquery"
)

type dataRetriever struct {
	url   string
	bsoup *goquery.Document
}

// TODO: should use interface to make it testable and someday we can change to use other library
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
