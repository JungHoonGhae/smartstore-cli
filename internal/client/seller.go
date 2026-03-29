package client

import (
	"context"

	"github.com/junghoonkye/smartstore-cli/internal/domain"
)

// GetSellerInfo returns the selected channel's seller information from
// GET /api/channels?_action=selectedChannel.
func (c *Client) GetSellerInfo(ctx context.Context) (domain.SellerInfo, error) {
	url := c.apiBaseURL + "/api/channels?_action=selectedChannel"

	var info domain.SellerInfo
	if err := c.getJSON(ctx, url, &info); err != nil {
		return domain.SellerInfo{}, err
	}

	return info, nil
}

// GetSellerGrade returns the seller grade from
// GET /api/v1/sellers/dashboards/seller-grade.
func (c *Client) GetSellerGrade(ctx context.Context) (domain.SellerGrade, error) {
	url := c.apiBaseURL + "/api/v1/sellers/dashboards/seller-grade"

	var grade domain.SellerGrade
	if err := c.getJSON(ctx, url, &grade); err != nil {
		return domain.SellerGrade{}, err
	}

	return grade, nil
}

// GetPenalties returns the account penalties from
// GET /api/v1/sellers/dashboards/account/penalties.
func (c *Client) GetPenalties(ctx context.Context) (domain.Penalties, error) {
	url := c.apiBaseURL + "/api/v1/sellers/dashboards/account/penalties"

	var penalties domain.Penalties
	if err := c.getJSON(ctx, url, &penalties); err != nil {
		return domain.Penalties{}, err
	}

	return penalties, nil
}
