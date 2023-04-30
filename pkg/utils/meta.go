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
func GetUniqueTrendingVideoIds() ([]string, error) {
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

	rows = rows[1:] // skip the header row

	// Simply extract the unique video IDs, and keep them order
	uniqueIDs := make([]string, 0, 128)
	for _, row := range rows {
		uniqueIDs = append(uniqueIDs, row[1])
	}

	return uniqueIDs, nil
}
