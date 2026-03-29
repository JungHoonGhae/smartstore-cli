package output

import (
	"fmt"
	"strings"
)

type Format string

const (
	FormatTable Format = "table"
	FormatJSON  Format = "json"
	FormatCSV   Format = "csv"
)

func ParseFormat(value string) (Format, error) {
	format := Format(strings.ToLower(strings.TrimSpace(value)))

	switch format {
	case FormatTable, FormatJSON, FormatCSV:
		return format, nil
	default:
		return "", fmt.Errorf("unsupported output format %q; expected one of: table, json, csv", value)
	}
}
