package main

import (
	"fmt"

	"github.com/junghoonkye/smartstore-cli/internal/output"
	"github.com/spf13/cobra"
)

func newOrderCmd(opts *rootOptions) *cobra.Command {
	cmd := &cobra.Command{
		Use:   "order",
		Short: "Read order data",
	}

	listCmd := &cobra.Command{
		Use:   "list",
		Short: "Show order/delivery dashboard (use --detail for order list)",
		RunE: func(cmd *cobra.Command, _ []string) error {
			app, err := newAppContext(opts)
			if err != nil {
				return err
			}

			detail, _ := cmd.Flags().GetBool("detail")
			if detail {
				// GraphQL order list
				info, err := app.client.GetSellerInfo(cmd.Context())
				if err != nil {
					return userFacingCommandError(err)
				}
				merchantNo := fmt.Sprintf("%d", info.Pay.ID)

				page, _ := cmd.Flags().GetInt("page")
				size, _ := cmd.Flags().GetInt("size")

				result, err := app.client.ListOrders(cmd.Context(), merchantNo, page, size)
				if err != nil {
					return userFacingCommandError(err)
				}

				return output.WriteOrderList(cmd.OutOrStdout(), app.format, result)
			}

			// Default: dashboard summary
			d, err := app.client.GetOrderDashboard(cmd.Context())
			if err != nil {
				return userFacingCommandError(err)
			}
			return output.WriteOrderDashboard(cmd.OutOrStdout(), app.format, d)
		},
	}
	listCmd.Flags().Bool("detail", false, "Show detailed order list (GraphQL)")
	listCmd.Flags().Int("page", 1, "Page number (with --detail)")
	listCmd.Flags().Int("size", 20, "Page size (with --detail)")

	cmd.AddCommand(listCmd)

	return cmd
}
