package output

import (
	"encoding/csv"
	"encoding/json"
	"fmt"
	"io"
	"strconv"
	"strings"

	"github.com/junghoonkye/smartstore-cli/internal/domain"
)

func WriteOrderDashboard(w io.Writer, format Format, d domain.OrderDeliveryDashboard) error {
	switch format {
	case FormatJSON:
		encoder := json.NewEncoder(w)
		encoder.SetIndent("", "  ")
		return encoder.Encode(d)
	case FormatCSV:
		_, err := fmt.Fprintf(
			w,
			"payment_wait,new_order,today_dispatch,pre_order,subscription,delivery_preparing,delivering,delivered,arrival_guarantee,unaccepted_gift,purchase_completion\n%s\n",
			fmt.Sprintf("%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d",
				d.PaymentWaitCases, d.NewOrderCases, d.TodayDispatchCases,
				d.PreOrderCases, d.SubscriptionCases, d.DeliveryPreparingCases,
				d.DeliveringCases, d.DeliveredCases, d.ArrivalGuaranteeCases,
				d.UnacceptedGiftCases, d.PurchaseCompletionCases,
			),
		)
		return err
	case FormatTable:
		total := d.PaymentWaitCases + d.NewOrderCases + d.TodayDispatchCases +
			d.PreOrderCases + d.SubscriptionCases + d.DeliveryPreparingCases +
			d.DeliveringCases + d.DeliveredCases + d.ArrivalGuaranteeCases +
			d.UnacceptedGiftCases + d.PurchaseCompletionCases

		lines := []struct {
			label string
			value int
		}{
			{"Payment Wait", d.PaymentWaitCases},
			{"New Order", d.NewOrderCases},
			{"Today Dispatch", d.TodayDispatchCases},
			{"Pre-order", d.PreOrderCases},
			{"Subscription", d.SubscriptionCases},
			{"Delivery Preparing", d.DeliveryPreparingCases},
			{"Delivering", d.DeliveringCases},
			{"Delivered", d.DeliveredCases},
			{"Arrival Guarantee", d.ArrivalGuaranteeCases},
			{"Unaccepted Gift", d.UnacceptedGiftCases},
			{"Purchase Completion", d.PurchaseCompletionCases},
		}

		if _, err := fmt.Fprintf(w, "Order/Delivery Dashboard (total: %s)\n\n", strconv.Itoa(total)); err != nil {
			return err
		}
		for _, l := range lines {
			if _, err := fmt.Fprintf(w, "  %-22s %d\n", l.label+":", l.value); err != nil {
				return err
			}
		}
		return nil
	default:
		return fmt.Errorf("unsupported format: %s", format)
	}
}

// WriteOrderList renders the order list from the GraphQL response.
func WriteOrderList(w io.Writer, format Format, result domain.OrderStatusResult) error {
	switch format {
	case FormatJSON:
		encoder := json.NewEncoder(w)
		encoder.SetIndent("", "  ")
		return encoder.Encode(result)
	case FormatCSV:
		writer := csv.NewWriter(w)
		defer writer.Flush()

		if err := writer.Write([]string{
			"product_order_no", "order_no", "order_date", "status",
			"product_name", "quantity", "buyer", "receiver", "claim_status",
		}); err != nil {
			return err
		}

		for _, o := range result.Elements {
			if err := writer.Write([]string{
				o.ProductOrderNo,
				o.OrderNo,
				o.OrderDateTime,
				o.ProductOrderStatus,
				o.ProductName,
				strconv.Itoa(o.OrderQuantity),
				o.OrderMemberName,
				o.ReceiverName,
				o.ClaimStatus,
			}); err != nil {
				return err
			}
		}
		return nil
	case FormatTable:
		if len(result.Elements) == 0 {
			_, err := fmt.Fprintf(w, "No orders found. (total: %s)\n", result.Pagination.TotalElements)
			return err
		}

		_, _ = fmt.Fprintf(w, "Page %d/%d (total: %s orders)\n\n",
			result.Pagination.Page, result.Pagination.TotalPages, result.Pagination.TotalElements)

		header := fmt.Sprintf("%-18s  %-18s  %-19s  %-16s  %-30s  %4s  %-10s",
			"PRODUCT ORDER NO", "ORDER NO", "ORDER DATE", "STATUS", "PRODUCT", "QTY", "BUYER")
		if _, err := fmt.Fprintln(w, header); err != nil {
			return err
		}
		if _, err := fmt.Fprintln(w, strings.Repeat("-", len(header))); err != nil {
			return err
		}

		for _, o := range result.Elements {
			name := truncateOrder(o.ProductName, 30)
			if _, err := fmt.Fprintf(
				w,
				"%-18s  %-18s  %-19s  %-16s  %-30s  %4d  %-10s\n",
				o.ProductOrderNo, o.OrderNo, o.OrderDateTime,
				o.ProductOrderStatus, name, o.OrderQuantity, o.OrderMemberName,
			); err != nil {
				return err
			}
		}
		return nil
	default:
		return fmt.Errorf("unsupported format: %s", format)
	}
}

func truncateOrder(s string, maxLen int) string {
	runes := []rune(s)
	if len(runes) <= maxLen {
		return s
	}
	return string(runes[:maxLen-2]) + ".."
}
