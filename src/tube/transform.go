package main

import (
	"strconv"
	"strings"
)

// ConvertFromPtFormat transforms a time duration string in the ISO_8601 format
// to a numeric representation in seconds, minutes, or hours.
//
// Parameters:
//   - pt: a string representing the time duration in the ISO_8601 format (e.g., "PT1H30M")
//   - targetFormat: a string indicating the desired output format ("seconds", "minutes", or "hours")
//
// Returns:
//   - A float64 value representing the time duration in the specified format.
func ConvertFromPtFormat(pt string, targetFormat string) float64 {
	if pt[0:2] == "PT" {
		pt = strings.Replace(pt, "PT", "", 1)
		mDivider := strings.Split(pt, "M")
		minutes, _ := strconv.Atoi(mDivider[0])
		seconds, _ := strconv.Atoi(strings.Split(mDivider[1], "S")[0])

		if targetFormat == "seconds" {
			return float64((60 * minutes) + seconds)
		} else if targetFormat == "minutes" {
			return float64(minutes) + (float64(seconds) / 60)
		} else if targetFormat == "hours" {
			return (float64(minutes) + (float64(seconds) / 60)) / 60
		}
	}
	panic("The input string is not in ISO_8601 format..!")
}
