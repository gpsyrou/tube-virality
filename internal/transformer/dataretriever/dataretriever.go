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
