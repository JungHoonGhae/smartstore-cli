package output

import (
	"encoding/json"
	"fmt"
	"io"

	"github.com/junghoonkye/smartstore-cli/internal/config"
)

func WriteConfigStatus(w io.Writer, format Format, status config.Status) error {
	switch format {
	case FormatJSON:
		encoder := json.NewEncoder(w)
		encoder.SetIndent("", "  ")
		return encoder.Encode(status)
	case FormatCSV:
		return fmt.Errorf("csv output is not supported for config status")
	case FormatTable:
		existsStr := "no"
		if status.Exists {
			existsStr = "yes"
		}
		_, err := fmt.Fprintf(
			w,
			"Config File: %s\nExists: %s\nSchema Version: %d\n",
			status.ConfigFile,
			existsStr,
			status.SchemaVersion,
		)
		return err
	default:
		return fmt.Errorf("unsupported format: %s", format)
	}
}
