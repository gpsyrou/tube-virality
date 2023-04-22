package dataretriever

import (
	"log"

	"github.com/PuerkitoBio/goquery"
)

type TubeVideoMetaDataRetriever struct {
	videoUrl   string
	videoBsoup *goquery.Document
}

func NewVideoMetaDataRetriever(videoUrl string) *TubeVideoMetaDataRetriever {
	videoBsoup, err := goquery.NewDocument(videoUrl)
	if err != nil {
		log.Fatal(err)
	}

	return &TubeVideoMetaDataRetriever{
		videoUrl:   videoUrl,
		videoBsoup: videoBsoup,
	}
}

func (t *TubeVideoMetaDataRetriever) MetaContentTags() *goquery.Selection {
	return t.videoBsoup.Find("meta")
}
