package main

import (
	"fmt"
	"testing"

	"github.com/gpsyrou/tube-virality/src/tube/transform"
)

func TestConvertFromPtFormat(t *testing.T) {
	testCases := []struct {
		input         string
		targetFormat  string
		expectedValue float64
	}{
		{"PT1M30S", "seconds", 90},
		{"PT1M30S", "minutes", 1.5},
		{"PT1M30S", "hours", 0.025},
	}

	for _, tc := range testCases {
		output := transform.ConvertFromPtFormat(tc.input, tc.targetFormat)
		fmt.Println(output)
		if output != tc.expectedValue {
			t.Errorf("ConvertFromPtFormat(%v, %v) = %v; want %v", tc.input, tc.targetFormat, output, tc.expectedValue)
		}
	}
}
