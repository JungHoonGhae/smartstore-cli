package client

import (
	"context"

	"github.com/junghoonkye/smartstore-cli/internal/domain"
)

// GetInquiryDashboard returns the inquiry dashboard from
// GET /api/v1/sellers/dashboards/inquiries.
func (c *Client) GetInquiryDashboard(ctx context.Context) (domain.InquiryDashboard, error) {
	url := c.apiBaseURL + "/api/v1/sellers/dashboards/inquiries"

	var dashboard domain.InquiryDashboard
	if err := c.getJSON(ctx, url, &dashboard); err != nil {
		return domain.InquiryDashboard{}, err
	}

	return dashboard, nil
}
