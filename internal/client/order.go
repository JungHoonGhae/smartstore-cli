package client

import (
	"context"
	"fmt"
	"time"

	"github.com/junghoonkye/smartstore-cli/internal/domain"
)

// GetOrderDashboard returns the order/delivery dashboard from
// GET /api/v1/sellers/dashboards/pay/order-delivery.
func (c *Client) GetOrderDashboard(ctx context.Context) (domain.OrderDeliveryDashboard, error) {
	url := c.apiBaseURL + "/api/v1/sellers/dashboards/pay/order-delivery"

	var dashboard domain.OrderDeliveryDashboard
	if err := c.getJSON(ctx, url, &dashboard); err != nil {
		return domain.OrderDeliveryDashboard{}, err
	}

	return dashboard, nil
}

// ListOrders queries the GraphQL endpoint for order status.
// merchantNo is the pay.id from SellerInfo.
func (c *Client) ListOrders(ctx context.Context, merchantNo string, page, size int) (domain.OrderStatusResult, error) {
	url := c.apiBaseURL + "/o/v3/graphql"

	now := time.Now()
	to := time.Date(now.Year(), now.Month(), now.Day(), 23, 59, 59, 0, now.Location())
	from := to.AddDate(0, 0, -7)

	body := map[string]any{
		"operationName": "orderStatus_ForOrderStatus",
		"variables": map[string]any{
			"input": map[string]any{
				"merchantNo":             merchantNo,
				"serviceType":            "MP",
				"rangeType":              "PAY_COMPLETED",
				"dateRange_from":         fmt.Sprintf("%d", from.UnixMilli()),
				"dateRange_to":           fmt.Sprintf("%d", to.UnixMilli()),
				"paging_page":            page,
				"paging_size":            size,
				"sort_type":              nil,
				"sort_direction":         nil,
				"sellerOrderSearchTypes": []string{"NORMAL_ORDER", "GIFTING", "TODAY_DISPATCH", "PRE_ORDER", "SUBSCRIPTION", "RENTAL", "ARRIVAL_GUARANTEE"},
			},
		},
		"query": "query orderStatus_ForOrderStatus($input: OrderStatusInput!) { orderStatus_ForOrderStatus(input: $input) { elements { productOrderNo orderNo orderDateTime productOrderStatus productName orderQuantity orderMemberName receiverName claimStatus } pagination { size totalElements page totalPages } } }",
	}

	var resp domain.OrderListResponse
	if err := c.postJSON(ctx, url, body, &resp); err != nil {
		return domain.OrderStatusResult{}, err
	}

	return resp.Data.OrderStatus, nil
}
