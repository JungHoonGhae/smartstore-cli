package output

import (
	"bytes"
	"encoding/json"
	"strings"
	"testing"

	"github.com/junghoonkye/smartstore-cli/internal/domain"
)

func TestWriteProducts_EmptyTable(t *testing.T) {
	var buf bytes.Buffer
	resp := domain.ProductSearchResponse{}

	if err := WriteProducts(&buf, FormatTable, resp); err != nil {
		t.Fatalf("WriteProducts returned error: %v", err)
	}

	got := buf.String()
	if !strings.Contains(got, "No products found") {
		t.Errorf("expected 'No products found' in output, got %q", got)
	}
}

func TestWriteProducts_JSON(t *testing.T) {
	var buf bytes.Buffer
	resp := domain.ProductSearchResponse{
		Content: []domain.ProductSearchItem{
			{
				ChannelProductNo:     12345,
				ProductName:          "Test Product",
				SalePrice:            15000,
				StockQuantity:        10,
				ChannelProductStatus: "SALE",
				CategoryName:         "Test Category",
			},
		},
		Total: 1,
	}

	if err := WriteProducts(&buf, FormatJSON, resp); err != nil {
		t.Fatalf("WriteProducts returned error: %v", err)
	}

	var decoded domain.ProductSearchResponse
	if err := json.Unmarshal(buf.Bytes(), &decoded); err != nil {
		t.Fatalf("failed to decode JSON output: %v", err)
	}

	if len(decoded.Content) != 1 {
		t.Fatalf("expected 1 product, got %d", len(decoded.Content))
	}
	if decoded.Content[0].ProductName != "Test Product" {
		t.Errorf("ProductName: got %q, want %q", decoded.Content[0].ProductName, "Test Product")
	}
	if decoded.Total != 1 {
		t.Errorf("Total: got %d, want %d", decoded.Total, 1)
	}
}

func TestWriteProductDashboard_Table(t *testing.T) {
	var buf bytes.Buffer
	d := domain.ProductDashboard{
		OnSaleProductCount:        "42",
		OnOutOfStockProductCount:  "3",
		ModifyRequestProductCount: "1",
	}

	if err := WriteProductDashboard(&buf, FormatTable, d); err != nil {
		t.Fatalf("WriteProductDashboard returned error: %v", err)
	}

	got := buf.String()
	if !strings.Contains(got, "On Sale: 42") {
		t.Errorf("expected 'On Sale: 42' in output, got %q", got)
	}
	if !strings.Contains(got, "Out of Stock: 3") {
		t.Errorf("expected 'Out of Stock: 3' in output, got %q", got)
	}
	if !strings.Contains(got, "Modify Request: 1") {
		t.Errorf("expected 'Modify Request: 1' in output, got %q", got)
	}
}
