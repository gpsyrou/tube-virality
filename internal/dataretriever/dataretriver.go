package dataretriever

import (
	"log"

	"github.com/PuerkitoBio/goquery"
)

type tubeVideoMetaDataRetriever struct {
	videoUrl   string
	videoBsoup *goquery.Document
}

func NewVideoMetaDataRetriever(videoUrl string) *tubeVideoMetaDataRetriever {
	videoBsoup, err := goquery.NewDocument(videoUrl)
	if err != nil {
		log.Fatal(err)
	}

	return &tubeVideoMetaDataRetriever{
		videoUrl:   videoUrl,
		videoBsoup: videoBsoup,
	}
}

func (t *tubeVideoMetaDataRetriever) MetaContentTags() *goquery.Selection {
	return t.videoBsoup.Find("meta")
}
