package main

import (
	"github.com/junghoonkye/smartstore-cli/internal/output"
	"github.com/spf13/cobra"
)

func newSettlementCmd(opts *rootOptions) *cobra.Command {
	cmd := &cobra.Command{
		Use:   "settlement",
		Short: "View settlement data",
	}

	listCmd := &cobra.Command{
		Use:   "list",
		Short: "Show settlement dashboard",
		RunE: func(cmd *cobra.Command, _ []string) error {
			app, err := newAppContext(opts)
			if err != nil {
				return err
			}

			dashboard, err := app.client.GetSettlementDashboard(cmd.Context())
			if err != nil {
				return userFacingCommandError(err)
			}

			return output.WriteSettlementDashboard(cmd.OutOrStdout(), app.format, dashboard)
		},
	}
	// Keep the flag for backward compatibility but the dashboard API returns current state.
	listCmd.Flags().String("month", "", "Month in YYYY-MM format (not used with dashboard API)")

	cmd.AddCommand(listCmd)

	return cmd
}
