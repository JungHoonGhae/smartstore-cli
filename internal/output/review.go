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

func WriteReviewDashboard(w io.Writer, format Format, d domain.ReviewDashboard) error {
	switch format {
	case FormatJSON:
		encoder := json.NewEncoder(w)
		encoder.SetIndent("", "  ")
		return encoder.Encode(d)
	case FormatCSV:
		_, err := fmt.Fprintf(
			w,
			"review_count,review_avg_score,manager_comment_count\n%d,%s,%d\n",
			d.ReviewCount, formatFloat(d.ReviewAvgScore), d.ManagerCommentCount,
		)
		return err
	case FormatTable:
		_, err := fmt.Fprintf(
			w,
			"Review Dashboard\n\n"+
				"  Total Reviews:      %d\n"+
				"  Average Score:      %s\n"+
				"  Manager Comments:   %d\n",
			d.ReviewCount, formatFloat(d.ReviewAvgScore), d.ManagerCommentCount,
		)
		return err
	default:
		return fmt.Errorf("unsupported format: %s", format)
	}
}

func WriteReviews(w io.Writer, format Format, resp domain.ReviewSearchResponse) error {
	switch format {
	case FormatJSON:
		encoder := json.NewEncoder(w)
		encoder.SetIndent("", "  ")
		return encoder.Encode(resp)
	case FormatCSV:
		writer := csv.NewWriter(w)
		defer writer.Flush()

		if err := writer.Write([]string{
			"id", "product_name", "score", "content", "buyer_id", "created_date",
		}); err != nil {
			return err
		}

		for _, r := range resp.Contents {
			if err := writer.Write([]string{
				r.ReviewID,
				r.ProductName,
				strconv.Itoa(r.Score),
				r.Content,
				r.BuyerID,
				r.CreatedDate,
			}); err != nil {
				return err
			}
		}
		return nil
	case FormatTable:
		if len(resp.Contents) == 0 {
			_, err := fmt.Fprintf(w, "No reviews found. (page %d/%d, total: %d)\n",
				resp.Page, resp.TotalPages, resp.TotalElements)
			return err
		}

		_, _ = fmt.Fprintf(w, "Reviews (page %d/%d, total: %d)\n\n",
			resp.Page, resp.TotalPages, resp.TotalElements)

		header := fmt.Sprintf("%-14s  %-24s  %5s  %-10s  %-30s  %s",
			"ID", "PRODUCT", "SCORE", "BUYER", "CONTENT", "DATE")
		if _, err := fmt.Fprintln(w, header); err != nil {
			return err
		}
		if _, err := fmt.Fprintln(w, strings.Repeat("-", len(header))); err != nil {
			return err
		}

		for _, r := range resp.Contents {
			product := truncate(r.ProductName, 24)
			content := truncate(r.Content, 30)
			if _, err := fmt.Fprintf(
				w,
				"%-14s  %-24s  %5d  %-10s  %-30s  %s\n",
				r.ReviewID, product, r.Score, r.BuyerID, content, r.CreatedDate,
			); err != nil {
				return err
			}
		}
		return nil
	default:
		return fmt.Errorf("unsupported format: %s", format)
	}
}
