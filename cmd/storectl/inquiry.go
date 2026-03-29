package main

import (
	"github.com/junghoonkye/smartstore-cli/internal/output"
	"github.com/spf13/cobra"
)

func newInquiryCmd(opts *rootOptions) *cobra.Command {
	cmd := &cobra.Command{
		Use:   "inquiry",
		Short: "View customer inquiries",
	}

	listCmd := &cobra.Command{
		Use:   "list",
		Short: "Show inquiry dashboard",
		RunE: func(cmd *cobra.Command, _ []string) error {
			app, err := newAppContext(opts)
			if err != nil {
				return err
			}

			dashboard, err := app.client.GetInquiryDashboard(cmd.Context())
			if err != nil {
				return userFacingCommandError(err)
			}

			return output.WriteInquiryDashboard(cmd.OutOrStdout(), app.format, dashboard)
		},
	}
	// Keep the flag for backward compatibility but the dashboard API returns all counts.
	listCmd.Flags().String("status", "all", "Filter by status (not used with dashboard API)")

	cmd.AddCommand(listCmd)

	return cmd
}
