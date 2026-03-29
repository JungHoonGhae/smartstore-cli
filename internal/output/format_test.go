package output

import (
	"testing"
)

func TestParseFormat_Valid(t *testing.T) {
	tests := []struct {
		input string
		want  Format
	}{
		{"table", FormatTable},
		{"json", FormatJSON},
		{"csv", FormatCSV},
		{"TABLE", FormatTable},
		{"Json", FormatJSON},
		{"  csv  ", FormatCSV},
	}

	for _, tt := range tests {
		t.Run(tt.input, func(t *testing.T) {
			got, err := ParseFormat(tt.input)
			if err != nil {
				t.Fatalf("ParseFormat(%q) returned error: %v", tt.input, err)
			}
			if got != tt.want {
				t.Errorf("ParseFormat(%q) = %q, want %q", tt.input, got, tt.want)
			}
		})
	}
}

func TestParseFormat_Invalid(t *testing.T) {
	_, err := ParseFormat("xml")
	if err == nil {
		t.Error("expected error for invalid format, got nil")
	}
}
