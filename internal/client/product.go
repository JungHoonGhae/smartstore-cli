package client

import (
	"context"
	"fmt"

	"github.com/junghoonkye/smartstore-cli/internal/domain"
)

// ListProducts searches products via POST /api/products/list/search.
func (c *Client) ListProducts(ctx context.Context, page, size int) (domain.ProductSearchResponse, error) {
	url := c.apiBaseURL + "/api/products/list/search"

	body := map[string]any{
		"searchKeywordType": "CHANNEL_PRODUCT_NO",
		"searchKeyword":     "",
		"searchOrderType":   "REG_DATE",
		"page":              page,
		"pageSize":          size,
	}

	var result domain.ProductSearchResponse
	if err := c.postJSON(ctx, url, body, &result); err != nil {
		return domain.ProductSearchResponse{}, err
	}

	return result, nil
}

// GetProduct retrieves a single product by searching with CHANNEL_PRODUCT_NO.
// There is no direct product detail endpoint, so we use the search API with
// the product number as keyword.
func (c *Client) GetProduct(ctx context.Context, id string) (domain.ProductSearchItem, error) {
	url := c.apiBaseURL + "/api/products/list/search"

	body := map[string]any{
		"searchKeywordType": "CHANNEL_PRODUCT_NO",
		"searchKeyword":     id,
		"searchOrderType":   "REG_DATE",
		"page":              1,
		"pageSize":          1,
	}

	var result domain.ProductSearchResponse
	if err := c.postJSON(ctx, url, body, &result); err != nil {
		return domain.ProductSearchItem{}, err
	}

	if len(result.Content) == 0 {
		return domain.ProductSearchItem{}, fmt.Errorf("product %s not found", id)
	}

	return result.Content[0], nil
}

// GetProductDashboard returns product dashboard counts from
// GET /api/v1/sellers/dashboards/channel/products.
func (c *Client) GetProductDashboard(ctx context.Context) (domain.ProductDashboard, error) {
	url := c.apiBaseURL + "/api/v1/sellers/dashboards/channel/products"

	var dashboard domain.ProductDashboard
	if err := c.getJSON(ctx, url, &dashboard); err != nil {
		return domain.ProductDashboard{}, err
	}

	return dashboard, nil
}
