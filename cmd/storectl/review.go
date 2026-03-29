package main

import (
	"github.com/junghoonkye/smartstore-cli/internal/output"
	"github.com/spf13/cobra"
)

func newReviewCmd(opts *rootOptions) *cobra.Command {
	cmd := &cobra.Command{
		Use:   "review",
		Short: "View product reviews",
	}

	listCmd := &cobra.Command{
		Use:   "list",
		Short: "Search product reviews",
		RunE: func(cmd *cobra.Command, _ []string) error {
			app, err := newAppContext(opts)
			if err != nil {
				return err
			}

			page, _ := cmd.Flags().GetInt("page")
			size, _ := cmd.Flags().GetInt("size")

			reviews, err := app.client.SearchReviews(cmd.Context(), page, size)
			if err != nil {
				return userFacingCommandError(err)
			}

			return output.WriteReviews(cmd.OutOrStdout(), app.format, reviews)
		},
	}
	listCmd.Flags().Int("page", 1, "Page number")
	listCmd.Flags().Int("size", 10, "Page size")

	cmd.AddCommand(
		listCmd,
		&cobra.Command{
			Use:   "dashboard",
			Short: "Show review dashboard summary",
			RunE: func(cmd *cobra.Command, _ []string) error {
				app, err := newAppContext(opts)
				if err != nil {
					return err
				}

				dashboard, err := app.client.GetReviewDashboard(cmd.Context())
				if err != nil {
					return userFacingCommandError(err)
				}

				return output.WriteReviewDashboard(cmd.OutOrStdout(), app.format, dashboard)
			},
		},
	)

	return cmd
}
