package main

import (
	"encoding/json"
	"fmt"
	"log"
	"os"
	"path/filepath"
	"time"

	"github.com/gpsyrou/tube-virality/internal/transformer/dataretriever"
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

	metaData := make(map[string]map[string]string)

	// get metadata for each video id
	for _, videoId := range videoIds {
		// DISSCUSSION: should we create object each url or create one object and change url each time?
		videoUrl := fmt.Sprintf("https://www.youtube.com/watch?v=%s", videoId)
		dataRetriever := dataretriever.NewDataRetriever(videoUrl)

		metaData[videoId] = dataRetriever.FetchMetadata()
		fmt.Printf("Metadata for video %s is handled\n", videoId)
	}

	// write to json file
	beWriteJsonData, err := json.MarshalIndent(metaData, "", "    ")
	if err != nil {
		log.Fatal(err)
	}

	// create metadata file with suffix of current date in yyymmdd format
	filename := fmt.Sprintf("video_metadata_%s.json", time.Now().Format("20060102"))
	filePath := filepath.Join(dir, filename)

	err = utils.SaveJSONToFile(filePath, beWriteJsonData)
	if err != nil {
		log.Fatal(err)
		return
	}

	fmt.Printf("Metadata is saved to %s\n", filename)
}
