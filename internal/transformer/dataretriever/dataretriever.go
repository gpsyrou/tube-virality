package dataretriever

import (
	"log"

	"github.com/PuerkitoBio/goquery"
)

type IDataRetriever interface {
	FetchMetadata() map[string]string
}

type dataRetriever struct {
	url   string
	bsoup *goquery.Document
}

func NewDataRetriever(videoUrl string) IDataRetriever {
	videoBsoup, err := goquery.NewDocument(videoUrl)
	if err != nil {
		log.Fatal(err)
	}

	return &dataRetriever{
		url:   videoUrl,
		bsoup: videoBsoup,
	}
}

func (t *dataRetriever) getMetaContentTags() *goquery.Selection {
	return t.bsoup.Find("meta")
}

func (t *dataRetriever) FetchMetadata() map[string]string {
	metaTags := t.getMetaContentTags()
	metaData := make(map[string]string)

	metaTags.Each(func(i int, s *goquery.Selection) {
		itemProp := s.AttrOr("itemprop", "")
		metaContent := s.AttrOr("content", "")
		if itemProp != "" && metaContent != "" {
			metaData[itemProp] = metaContent
		}
	})

	return metaData
}
