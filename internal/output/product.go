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

func WriteProducts(w io.Writer, format Format, resp domain.ProductSearchResponse) error {
	switch format {
	case FormatJSON:
		encoder := json.NewEncoder(w)
		encoder.SetIndent("", "  ")
		return encoder.Encode(resp)
	case FormatCSV:
		writer := csv.NewWriter(w)
		defer writer.Flush()

		if err := writer.Write([]string{
			"channel_product_no", "name", "status", "sale_price", "stock_quantity", "category",
		}); err != nil {
			return err
		}

		for _, p := range resp.Content {
			if err := writer.Write([]string{
				strconv.FormatInt(p.ChannelProductNo, 10),
				p.ProductName,
				p.ChannelProductStatus,
				strconv.FormatInt(p.SalePrice, 10),
				strconv.Itoa(p.StockQuantity),
				p.CategoryName,
			}); err != nil {
				return err
			}
		}
		return nil
	case FormatTable:
		if len(resp.Content) == 0 {
			_, err := fmt.Fprintln(w, "No products found.")
			return err
		}

		if resp.Pageable.Page > 0 {
			_, _ = fmt.Fprintf(w, "Page %d (total: %d products)\n\n", resp.Pageable.Page, resp.Total)
		} else {
			_, _ = fmt.Fprintf(w, "Total: %d product(s)\n\n", resp.Total)
		}

		header := fmt.Sprintf("%-14s  %-30s  %-10s  %12s  %6s  %s",
			"PRODUCT NO", "NAME", "STATUS", "PRICE", "STOCK", "CATEGORY")
		if _, err := fmt.Fprintln(w, header); err != nil {
			return err
		}
		if _, err := fmt.Fprintln(w, strings.Repeat("-", len(header))); err != nil {
			return err
		}

		for _, p := range resp.Content {
			name := truncate(p.ProductName, 30)
			if _, err := fmt.Fprintf(
				w,
				"%-14d  %-30s  %-10s  %12d  %6d  %s\n",
				p.ChannelProductNo, name, p.ChannelProductStatus,
				p.SalePrice, p.StockQuantity, p.CategoryName,
			); err != nil {
				return err
			}
		}
		return nil
	default:
		return fmt.Errorf("unsupported format: %s", format)
	}
}

func WriteProduct(w io.Writer, format Format, p domain.ProductSearchItem) error {
	switch format {
	case FormatJSON:
		encoder := json.NewEncoder(w)
		encoder.SetIndent("", "  ")
		return encoder.Encode(p)
	case FormatCSV:
		return fmt.Errorf("csv output is not supported for single product")
	case FormatTable:
		_, err := fmt.Fprintf(
			w,
			"Product No: %d\nName: %s\nStatus: %s\nPrice: %d\nStock: %d\nCategory: %s\nRegistered: %s\nModified: %s\n",
			p.ChannelProductNo, p.ProductName, p.ChannelProductStatus,
			p.SalePrice, p.StockQuantity, p.CategoryName,
			p.RegDate, p.ModDate,
		)
		return err
	default:
		return fmt.Errorf("unsupported format: %s", format)
	}
}

func WriteProductDashboard(w io.Writer, format Format, d domain.ProductDashboard) error {
	switch format {
	case FormatJSON:
		encoder := json.NewEncoder(w)
		encoder.SetIndent("", "  ")
		return encoder.Encode(d)
	case FormatCSV:
		_, err := fmt.Fprintf(
			w,
			"on_sale,out_of_stock,modify_request\n%s,%s,%s\n",
			d.OnSaleProductCount,
			d.OnOutOfStockProductCount,
			d.ModifyRequestProductCount,
		)
		return err
	case FormatTable:
		_, err := fmt.Fprintf(
			w,
			"On Sale: %s\nOut of Stock: %s\nModify Request: %s\n",
			d.OnSaleProductCount,
			d.OnOutOfStockProductCount,
			d.ModifyRequestProductCount,
		)
		return err
	default:
		return fmt.Errorf("unsupported format: %s", format)
	}
}

func formatFloat(f float64) string {
	if f == float64(int64(f)) {
		return strconv.FormatInt(int64(f), 10)
	}
	return strconv.FormatFloat(f, 'f', -1, 64)
}

func truncate(s string, maxLen int) string {
	runes := []rune(s)
	if len(runes) <= maxLen {
		return s
	}
	return string(runes[:maxLen-2]) + ".."
}
