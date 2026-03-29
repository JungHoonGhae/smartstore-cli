package client

import (
	"context"

	"github.com/junghoonkye/smartstore-cli/internal/domain"
)

// GetSettlementDashboard returns the settlement dashboard from
// GET /api/v1/sellers/dashboards/pay/settlement.
func (c *Client) GetSettlementDashboard(ctx context.Context) (domain.SettlementDashboard, error) {
	url := c.apiBaseURL + "/api/v1/sellers/dashboards/pay/settlement"

	var dashboard domain.SettlementDashboard
	if err := c.getJSON(ctx, url, &dashboard); err != nil {
		return domain.SettlementDashboard{}, err
	}

	return dashboard, nil
}
