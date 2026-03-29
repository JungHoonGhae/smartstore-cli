package main

import (
	"github.com/junghoonkye/smartstore-cli/internal/output"
	"github.com/spf13/cobra"
)

func newSellerCmd(opts *rootOptions) *cobra.Command {
	cmd := &cobra.Command{
		Use:   "seller",
		Short: "View seller account information",
	}

	cmd.AddCommand(
		&cobra.Command{
			Use:   "info",
			Short: "Show seller channel information",
			RunE: func(cmd *cobra.Command, _ []string) error {
				app, err := newAppContext(opts)
				if err != nil {
					return err
				}

				info, err := app.client.GetSellerInfo(cmd.Context())
				if err != nil {
					return userFacingCommandError(err)
				}

				return output.WriteSellerInfo(cmd.OutOrStdout(), app.format, info)
			},
		},
		&cobra.Command{
			Use:   "grade",
			Short: "Show seller grade and penalties",
			RunE: func(cmd *cobra.Command, _ []string) error {
				app, err := newAppContext(opts)
				if err != nil {
					return err
				}

				grade, err := app.client.GetSellerGrade(cmd.Context())
				if err != nil {
					return userFacingCommandError(err)
				}

				penalties, err := app.client.GetPenalties(cmd.Context())
				if err != nil {
					return userFacingCommandError(err)
				}

				return output.WriteSellerGrade(cmd.OutOrStdout(), app.format, grade, penalties)
			},
		},
	)

	return cmd
}
