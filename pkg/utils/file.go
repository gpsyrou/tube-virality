package utils

import (
	"fmt"
	"os"
)

func SaveJSONToFile(filepath string, data []byte) error {
	jsonFile, err := os.OpenFile(filepath, os.O_WRONLY|os.O_CREATE, 0644)
	if err != nil {
		return fmt.Errorf("error opening file: %s", err)
	}
	defer jsonFile.Close()

	_, err = jsonFile.Seek(0, 0)
	if err != nil {
		return fmt.Errorf("error seeking file: %s", err)
	}

	_, err = jsonFile.Write(data)
	if err != nil {
		return fmt.Errorf("error writing to file: %s", err)
	}

	err = jsonFile.Truncate(int64(len(data)))

	if err != nil {
		return fmt.Errorf("error truncating file: %s", err)
	}

	return nil
}
