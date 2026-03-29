package main

import (
	"encoding/json"
	"fmt"
	"runtime"

	"github.com/junghoonkye/smartstore-cli/internal/output"
	"github.com/junghoonkye/smartstore-cli/internal/version"
	"github.com/spf13/cobra"
)

func newVersionCmd(opts *rootOptions) *cobra.Command {
	return &cobra.Command{
		Use:   "version",
		Short: "Show storectl version information",
		RunE: func(cmd *cobra.Command, _ []string) error {
			info := version.Current()

			switch output.Format(opts.outputFormat) {
			case output.FormatJSON:
				encoder := json.NewEncoder(cmd.OutOrStdout())
				encoder.SetIndent("", "  ")
				return encoder.Encode(map[string]any{
					"version": info.Version,
					"commit":  info.Commit,
					"date":    info.Date,
					"os":      runtime.GOOS,
					"arch":    runtime.GOARCH,
				})
			case output.FormatCSV:
				return fmt.Errorf("csv output is not supported for version")
			default:
				_, err := fmt.Fprintf(
					cmd.OutOrStdout(),
					"storectl %s\ncommit: %s\ndate: %s\nos/arch: %s/%s\n",
					info.Version,
					info.Commit,
					valueOrDefault(info.Date, "n/a"),
					runtime.GOOS,
					runtime.GOARCH,
				)
				return err
			}
		},
	}
}

func valueOrDefault(value, fallback string) string {
	if value == "" {
		return fallback
	}
	return value
}
