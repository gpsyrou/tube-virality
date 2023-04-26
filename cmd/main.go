package main

import (
	"encoding/json"
	"fmt"
	"log"
	"path/filepath"
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
	for _, videoID := range videoIDs {
		// DISSCUSSION: should we create object each url or create one object and change url each time?
		videoURL := fmt.Sprintf("https://www.youtube.com/watch?v=%s", videoID)
		dataRetriever := dataretriever.NewDataRetriever(videoURL)

		metaData[videoID] = dataRetriever.FetchMetadata()

		fmt.Printf("Metadata for video %s is handled\n", videoID)
	}

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
