package main

import (
	"github.com/junghoonkye/smartstore-cli/internal/output"
	"github.com/spf13/cobra"
)

func newStatsCmd(opts *rootOptions) *cobra.Command {
	cmd := &cobra.Command{
		Use:   "stats",
		Short: "View sales statistics",
	}

	dailyCmd := &cobra.Command{
		Use:   "daily",
		Short: "Show sales summary (daily/weekly/monthly)",
		RunE: func(cmd *cobra.Command, _ []string) error {
			app, err := newAppContext(opts)
			if err != nil {
				return err
			}

			summary, err := app.client.GetSalesSummary(cmd.Context())
			if err != nil {
				return userFacingCommandError(err)
			}

			return output.WriteSalesSummary(cmd.OutOrStdout(), app.format, summary)
		},
	}
	// Keep the flag for backward compatibility but the dashboard API uses its own base date.
	dailyCmd.Flags().String("date", "", "Date in YYYY-MM-DD format (not used with dashboard API)")

	monthlyCmd := &cobra.Command{
		Use:   "monthly",
		Short: "Show sales summary (daily/weekly/monthly)",
		RunE: func(cmd *cobra.Command, _ []string) error {
			app, err := newAppContext(opts)
			if err != nil {
				return err
			}

			summary, err := app.client.GetSalesSummary(cmd.Context())
			if err != nil {
				return userFacingCommandError(err)
			}

			return output.WriteSalesSummary(cmd.OutOrStdout(), app.format, summary)
		},
	}
	// Keep the flag for backward compatibility but the dashboard API uses its own base date.
	monthlyCmd.Flags().String("month", "", "Month in YYYY-MM format (not used with dashboard API)")

	cmd.AddCommand(dailyCmd, monthlyCmd)

	return cmd
}
