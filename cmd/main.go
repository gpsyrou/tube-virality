package main

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"log"
	"os"
	"path/filepath"
	"time"

	"github.com/PuerkitoBio/goquery"
	"github.com/gpsyrou/tube-virality/internal/dataretriever"
	"github.com/gpsyrou/tube-virality/pkg/utils"
)

func main() {
	// TODO: here should only put entry point code

	// Retrieving a list of the unique video ids from the trending list
	uniqueIds, err := utils.GetUniqueTreningVideoIds()
	if err != nil {
		// Handle the error
		fmt.Println(err)
		return
	}

	// Create the videoIds variable as a slice of strings
	videoIds := make([]string, len(uniqueIds))
	copy(videoIds, uniqueIds)

	// Create directory for metadata file if it does not exist
	dir := "assets/metadata/video"
	if _, err := os.Stat(dir); os.IsNotExist(err) {
		if err := os.MkdirAll(dir, 0755); err != nil {
			log.Fatal(err)
		}
	}

	// create metadata file with suffix of current date in yyymmdd format
	filename := fmt.Sprintf("video_metadata_%s.json", time.Now().Format("20060102"))
	filepath := filepath.Join(dir, filename)

	jsonFile, err := os.OpenFile(filepath, os.O_RDWR|os.O_CREATE, 0644)
	if err != nil {
		log.Fatal(err)
	}
	defer jsonFile.Close()

	jsonData, err := ioutil.ReadAll(jsonFile)
	if err != nil {
		log.Fatal(err)
	}

	metaData := make(map[string]map[string]string)
	if len(jsonData) > 0 {
		err = json.Unmarshal(jsonData, &metaData)
		if err != nil {
			log.Fatal(err)
		}
	}

	for _, videoId := range videoIds {
		if _, ok := metaData[videoId]; ok {
			// Video metadata already exists, skip
			fmt.Printf("Skipping video %s, metadata already exists in %s\n", videoId, filename)
			continue
		}

		videoUrl := fmt.Sprintf("https://www.youtube.com/watch?v=%s", videoId)
		dataRetriever := dataretriever.NewVideoMetaDataRetriever(videoUrl)

		metaTags := dataRetriever.MetaContentTags()

		metaData[videoId] = make(map[string]string)
		metaTags.Each(func(i int, s *goquery.Selection) {
			itemProp := s.AttrOr("itemprop", "")
			metaContent := s.AttrOr("content", "")
			if itemProp != "" && metaContent != "" {
				metaData[videoId][itemProp] = metaContent
			}
		})

		jsonData, err := json.MarshalIndent(metaData, "", "    ")
		if err != nil {
			log.Fatal(err)
		}

		_, err = jsonFile.Seek(0, 0)
		if err != nil {
			log.Fatal(err)
		}

		_, err = jsonFile.Write(jsonData)
		if err != nil {
			log.Fatal(err)
		}

		err = jsonFile.Truncate(int64(len(jsonData)))
		if err != nil {
			log.Fatal(err)
		}

		fmt.Printf("Metadata for video %s saved to %s\n", videoId, filename)
	}
}
