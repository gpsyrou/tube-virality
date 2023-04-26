package main

import (
	"encoding/json"
	"fmt"
	"log"
	"path/filepath"
	"sync"
	"time"

	"github.com/gpsyrou/tube-virality/internal/transformer/dataretriever"
	"github.com/gpsyrou/tube-virality/pkg/utils"
)

func main() {
	// TODO: here should only put entry point code
	metaDir := "assets/metadata/video"

	err := utils.CreateDirIfNotExist(metaDir)
	if err != nil {
		log.Fatal(err)
		return
	}

	videoIDs, err := utils.GetUniqueTrendingVideoIds()
	if err != nil {
		log.Fatal(err)
		return
	}

	metaData := make(map[string]map[string]string)
	// get metadata for each video id
	var wg sync.WaitGroup

	for _, videoID := range videoIDs {
		wg.Add(1)

		go func(id string) {
			// DISSCUSSION: should we create object each url or create one object and change url each time?
			videoURL := fmt.Sprintf("https://www.youtube.com/watch?v=%s", id)
			dataRetriever := dataretriever.NewDataRetriever(videoURL)

			metaData[id] = dataRetriever.FetchMetadata()

			wg.Done()
			fmt.Printf("Metadata for video %s is handled\n", id)
		}(videoID)
	}

	wg.Wait()

	// write to json file
	beWriteJSONData, err := json.MarshalIndent(metaData, "", "    ")
	if err != nil {
		log.Fatal(err)
	}

	filename := fmt.Sprintf("video_metadata_%s.json", time.Now().Format("20060102"))
	filePath := filepath.Join(metaDir, filename)

	err = utils.SaveJSONToFile(filePath, beWriteJSONData)
	if err != nil {
		log.Fatal(err)
		return
	}

	fmt.Printf("Metadata is saved to %s\n", filename)
}
