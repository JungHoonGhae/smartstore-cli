package output

import (
	"encoding/json"
	"fmt"
	"io"
	"strings"

	"github.com/junghoonkye/smartstore-cli/internal/domain"
)

func WriteInquiryDashboard(w io.Writer, format Format, d domain.InquiryDashboard) error {
	switch format {
	case FormatJSON:
		encoder := json.NewEncoder(w)
		encoder.SetIndent("", "  ")
		return encoder.Encode(d)
	case FormatCSV:
		_, err := fmt.Fprintf(
			w,
			"product_inquiry_count,customer_inquiry_count,talktalk_inquiry_count\n%s,%s,%s\n",
			d.ProductInquiryCount, d.CustomerInquiryCount, d.TalktalkInquiryCount,
		)
		return err
	case FormatTable:
		if _, err := fmt.Fprintf(
			w,
			"Inquiry Dashboard\n\n"+
				"  Product Inquiries:  %s\n"+
				"  Customer Inquiries: %s\n"+
				"  TalkTalk Inquiries: %s\n",
			d.ProductInquiryCount, d.CustomerInquiryCount, d.TalktalkInquiryCount,
		); err != nil {
			return err
		}

		if len(d.ProductInquiries) > 0 {
			if _, err := fmt.Fprintln(w, "\nRecent Product Inquiries:"); err != nil {
				return err
			}
			header := fmt.Sprintf("  %-40s  %s", "TITLE", "DATE")
			if _, err := fmt.Fprintln(w, header); err != nil {
				return err
			}
			if _, err := fmt.Fprintf(w, "  %s\n", strings.Repeat("-", len(header)-2)); err != nil {
				return err
			}
			for _, inq := range d.ProductInquiries {
				title := truncate(inq.Title, 40)
				if _, err := fmt.Fprintf(w, "  %-40s  %s\n", title, inq.CreatedAt); err != nil {
					return err
				}
			}
		}

		if len(d.CustomerInquiries) > 0 {
			if _, err := fmt.Fprintln(w, "\nRecent Customer Inquiries:"); err != nil {
				return err
			}
			header := fmt.Sprintf("  %-40s  %s", "TITLE", "DATE")
			if _, err := fmt.Fprintln(w, header); err != nil {
				return err
			}
			if _, err := fmt.Fprintf(w, "  %s\n", strings.Repeat("-", len(header)-2)); err != nil {
				return err
			}
			for _, inq := range d.CustomerInquiries {
				title := truncate(inq.Title, 40)
				if _, err := fmt.Fprintf(w, "  %-40s  %s\n", title, inq.CreatedAt); err != nil {
					return err
				}
			}
		}

		return nil
	default:
		return fmt.Errorf("unsupported format: %s", format)
	}
}
