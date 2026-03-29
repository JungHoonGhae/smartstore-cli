package client

import (
	"context"
	"fmt"

	"github.com/junghoonkye/smartstore-cli/internal/domain"
)

// GetNotificationCounts returns notification counts by category from
// GET /api/seller/notification/user-activities/counts.
func (c *Client) GetNotificationCounts(ctx context.Context) (domain.NotificationCounts, error) {
	url := c.apiBaseURL + "/api/seller/notification/user-activities/counts"

	var counts domain.NotificationCounts
	if err := c.getJSON(ctx, url, &counts); err != nil {
		return nil, err
	}

	return counts, nil
}

// GetNotificationActivities returns recent notification activities from
// GET /api/seller/notification/user-activities?count={count}.
func (c *Client) GetNotificationActivities(ctx context.Context, count int) ([]domain.NotificationActivity, error) {
	url := fmt.Sprintf("%s/api/seller/notification/user-activities?count=%d", c.apiBaseURL, count)

	var activities []domain.NotificationActivity
	if err := c.getJSON(ctx, url, &activities); err != nil {
		return nil, err
	}

	return activities, nil
}
