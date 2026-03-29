package output

import (
	"encoding/json"
	"fmt"
	"io"

	"github.com/junghoonkye/smartstore-cli/internal/doctor"
)

func WriteDoctorReport(w io.Writer, format Format, report doctor.Report) error {
	switch format {
	case FormatJSON:
		encoder := json.NewEncoder(w)
		encoder.SetIndent("", "  ")
		return encoder.Encode(report)
	case FormatCSV:
		return fmt.Errorf("csv output is not supported for doctor report")
	case FormatTable:
		if _, err := fmt.Fprintf(
			w,
			"storectl %s (%s/%s, %s)\n\n",
			report.Version,
			report.OS,
			report.Arch,
			report.GoVersion,
		); err != nil {
			return err
		}

		if _, err := fmt.Fprintf(w, "Config: %s (exists: %v)\n\n", report.ConfigFile, report.Config.Exists); err != nil {
			return err
		}

		if _, err := fmt.Fprintln(w, "System Checks:"); err != nil {
			return err
		}
		for _, c := range report.Checks {
			if err := writeCheck(w, c); err != nil {
				return err
			}
		}

		if _, err := fmt.Fprintln(w, "\nAuth Checks:"); err != nil {
			return err
		}
		if _, err := fmt.Fprintf(w, "  Python: %s\n  Helper: %s\n", report.Auth.PythonBin, report.Auth.HelperDir); err != nil {
			return err
		}
		for _, c := range report.Auth.Checks {
			if err := writeCheck(w, c); err != nil {
				return err
			}
		}

		return nil
	default:
		return fmt.Errorf("unsupported format: %s", format)
	}
}

func WriteAuthDoctorReport(w io.Writer, format Format, report doctor.AuthReport) error {
	switch format {
	case FormatJSON:
		encoder := json.NewEncoder(w)
		encoder.SetIndent("", "  ")
		return encoder.Encode(report)
	case FormatCSV:
		return fmt.Errorf("csv output is not supported for auth doctor report")
	case FormatTable:
		if _, err := fmt.Fprintf(w, "Python: %s\nHelper: %s\n\nChecks:\n", report.PythonBin, report.HelperDir); err != nil {
			return err
		}
		for _, c := range report.Checks {
			if err := writeCheck(w, c); err != nil {
				return err
			}
		}
		return nil
	default:
		return fmt.Errorf("unsupported format: %s", format)
	}
}

func writeCheck(w io.Writer, c doctor.Check) error {
	icon := "?"
	switch c.Status {
	case "ok":
		icon = "ok"
	case "warning":
		icon = "!!"
	case "error":
		icon = "XX"
	}

	if c.Message != "" {
		_, err := fmt.Fprintf(w, "  [%s] %s: %s\n", icon, c.Name, c.Message)
		return err
	}
	_, err := fmt.Fprintf(w, "  [%s] %s\n", icon, c.Name)
	return err
}
