package main

import (
	"github.com/junghoonkye/smartstore-cli/internal/output"
	"github.com/spf13/cobra"
)

func newNotificationCmd(opts *rootOptions) *cobra.Command {
	cmd := &cobra.Command{
		Use:   "notification",
		Short: "View notifications",
	}

	listCmd := &cobra.Command{
		Use:   "list",
		Short: "Show notification counts and recent activities",
		RunE: func(cmd *cobra.Command, _ []string) error {
			app, err := newAppContext(opts)
			if err != nil {
				return err
			}

			counts, err := app.client.GetNotificationCounts(cmd.Context())
			if err != nil {
				return userFacingCommandError(err)
			}

			count, _ := cmd.Flags().GetInt("count")
			activities, err := app.client.GetNotificationActivities(cmd.Context(), count)
			if err != nil {
				return userFacingCommandError(err)
			}

			return output.WriteNotifications(cmd.OutOrStdout(), app.format, counts, activities)
		},
	}
	listCmd.Flags().Int("count", 10, "Number of recent activities to show")

	cmd.AddCommand(listCmd)

	return cmd
}
