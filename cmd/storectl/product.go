package main

import (
	"github.com/junghoonkye/smartstore-cli/internal/output"
	"github.com/spf13/cobra"
)

func newProductCmd(opts *rootOptions) *cobra.Command {
	cmd := &cobra.Command{
		Use:   "product",
		Short: "Read product data",
	}

	listCmd := &cobra.Command{
		Use:   "list",
		Short: "List all products",
		RunE: func(cmd *cobra.Command, _ []string) error {
			app, err := newAppContext(opts)
			if err != nil {
				return err
			}

			page, _ := cmd.Flags().GetInt("page")
			size, _ := cmd.Flags().GetInt("size")

			products, err := app.client.ListProducts(cmd.Context(), page, size)
			if err != nil {
				return userFacingCommandError(err)
			}

			return output.WriteProducts(cmd.OutOrStdout(), app.format, products)
		},
	}
	listCmd.Flags().Int("page", 1, "Page number")
	listCmd.Flags().Int("size", 50, "Page size")

	cmd.AddCommand(
		listCmd,
		&cobra.Command{
			Use:   "show <id>",
			Short: "Show details for a single product",
			Args:  cobra.ExactArgs(1),
			RunE: func(cmd *cobra.Command, args []string) error {
				app, err := newAppContext(opts)
				if err != nil {
					return err
				}

				product, err := app.client.GetProduct(cmd.Context(), args[0])
				if err != nil {
					return userFacingCommandError(err)
				}

				return output.WriteProduct(cmd.OutOrStdout(), app.format, product)
			},
		},
		&cobra.Command{
			Use:   "dashboard",
			Short: "Show product dashboard summary",
			RunE: func(cmd *cobra.Command, _ []string) error {
				app, err := newAppContext(opts)
				if err != nil {
					return err
				}

				dashboard, err := app.client.GetProductDashboard(cmd.Context())
				if err != nil {
					return userFacingCommandError(err)
				}

				return output.WriteProductDashboard(cmd.OutOrStdout(), app.format, dashboard)
			},
		},
	)

	return cmd
}
