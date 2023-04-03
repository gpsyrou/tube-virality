package main

import (
	"encoding/csv"
	"os"
	"path/filepath"
)

func GetUniqueTreningVideoIds() ([]string, error) {
	// Get the current working directory
	dir, err := os.Getwd()
	if err != nil {
		return nil, err
	}

	// Join the current working directory with the relative path to the CSV file
	filename := filepath.Join(dir, "data/metadata/trending/trending_videos_metadata.csv")

	// Open the CSV file
	file, err := os.Open(filename)
	if err != nil {
		return nil, err
	}
	defer file.Close()

	// Parse the CSV file
	reader := csv.NewReader(file)
	rows, err := reader.ReadAll()
	if err != nil {
		return nil, err
	}

	// Extract the unique video IDs
	videoIds := make(map[string]bool)
	for _, row := range rows {
		videoIds[row[1]] = true
	}

	// Convert the map of unique video IDs to a slice of strings
	uniqueIds := make([]string, 0, len(videoIds))
	for id := range videoIds {
		uniqueIds = append(uniqueIds, id)
	}

	return uniqueIds, nil
}
