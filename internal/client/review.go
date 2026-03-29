package client

import (
	"context"

	"github.com/junghoonkye/smartstore-cli/internal/domain"
)

// GetReviewDashboard returns the review dashboard from
// GET /api/v1/sellers/dashboards/reviews.
func (c *Client) GetReviewDashboard(ctx context.Context) (domain.ReviewDashboard, error) {
	url := c.apiBaseURL + "/api/v1/sellers/dashboards/reviews"

	var dashboard domain.ReviewDashboard
	if err := c.getJSON(ctx, url, &dashboard); err != nil {
		return domain.ReviewDashboard{}, err
	}

	return dashboard, nil
}

// SearchReviews searches reviews via POST /api/v3/contents/reviews/search.
func (c *Client) SearchReviews(ctx context.Context, page, pageSize int) (domain.ReviewSearchResponse, error) {
	url := c.apiBaseURL + "/api/v3/contents/reviews/search"

	body := map[string]any{
		"page":                 page,
		"pageSize":             pageSize,
		"reviewSearchSortType": "REVIEW_CREATED_DATE_DESC",
	}

	var result domain.ReviewSearchResponse
	if err := c.postJSON(ctx, url, body, &result); err != nil {
		return domain.ReviewSearchResponse{}, err
	}

	return result, nil
}
