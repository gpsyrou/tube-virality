package utils

import (
	"encoding/csv"
	"os"
	"path/filepath"
)

// GetUniqueTreningVideoIds returns a list of unique video IDs for the trending videos
// metadata CSV file.
//
// The function reads the CSV file located at "data/metadata/trending/trending_videos_metadata.csv",
// extracts the second column (which contains the video IDs), and returns a slice of strings
// containing only the unique video IDs.
//
// Returns:
//   - A slice of strings representing the unique video IDs in the CSV file.
func GetUniqueTreningVideoIds() ([]string, error) {
	// Get the current working directory
	dir, err := os.Getwd()
	if err != nil {
		return nil, err
	}

	// Join the current working directory with the relative path to the CSV file
	filename := filepath.Join(dir, "assets/metadata/trending/trending_videos_metadata.csv")

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
