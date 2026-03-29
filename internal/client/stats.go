package client

import (
	"context"

	"github.com/junghoonkye/smartstore-cli/internal/domain"
)

// GetSalesSummary returns the sales summary full chart from
// GET /api/v1/sellers/dashboards/account/sales-summary-full-chart?isRefresh=true.
func (c *Client) GetSalesSummary(ctx context.Context) (domain.SalesSummary, error) {
	url := c.apiBaseURL + "/api/v1/sellers/dashboards/account/sales-summary-full-chart?isRefresh=true"

	var summary domain.SalesSummary
	if err := c.getJSON(ctx, url, &summary); err != nil {
		return domain.SalesSummary{}, err
	}

	return summary, nil
}
