package main

import (
	"github.com/junghoonkye/smartstore-cli/internal/doctor"
	"github.com/junghoonkye/smartstore-cli/internal/output"
	"github.com/spf13/cobra"
)

func newDoctorCmd(opts *rootOptions) *cobra.Command {
	return &cobra.Command{
		Use:   "doctor",
		Short: "Check whether storectl is ready on this machine",
		RunE: func(cmd *cobra.Command, _ []string) error {
			app, err := newAppContext(opts)
			if err != nil {
				return err
			}
			configStatus, err := app.configService.Status(cmd.Context())
			if err != nil {
				return err
			}

			report, err := doctor.NewService(
				app.paths,
				configStatus,
				app.loginConfig,
				app.authService,
			).Run(cmd.Context())
			if err != nil {
				return err
			}

			return output.WriteDoctorReport(cmd.OutOrStdout(), app.format, report)
		},
	}
}
