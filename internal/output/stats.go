package output

import (
	"encoding/json"
	"fmt"
	"io"
	"strconv"

	"github.com/junghoonkye/smartstore-cli/internal/domain"
)

func WriteSalesSummary(w io.Writer, format Format, s domain.SalesSummary) error {
	switch format {
	case FormatJSON:
		encoder := json.NewEncoder(w)
		encoder.SetIndent("", "  ")
		return encoder.Encode(s)
	case FormatCSV:
		_, err := fmt.Fprintf(
			w,
			"base_date,account_id,pv_daily,pv_weekly,pv_monthly,orders_daily,orders_weekly,orders_monthly,pay_daily,pay_weekly,pay_monthly\n%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n",
			s.BaseDate, s.AccountID,
			strconv.Itoa(s.PVCount.Daily), strconv.Itoa(s.PVCount.Weekly), strconv.Itoa(s.PVCount.Monthly),
			strconv.Itoa(s.OrderCount.Daily), strconv.Itoa(s.OrderCount.Weekly), strconv.Itoa(s.OrderCount.Monthly),
			strconv.Itoa(s.PayAmount.Daily), strconv.Itoa(s.PayAmount.Weekly), strconv.Itoa(s.PayAmount.Monthly),
		)
		return err
	case FormatTable:
		_, err := fmt.Fprintf(
			w,
			"Sales Summary (base date: %s)\nAccount: %s\n\n"+
				"Page Views:\n  Daily: %d (prev: %d)\n  Weekly: %d (prev: %d)\n  Monthly: %d (prev: %d)\n\n"+
				"Orders:\n  Daily: %d (prev: %d)\n  Weekly: %d (prev: %d)\n  Monthly: %d (prev: %d)\n\n"+
				"Pay Amount:\n  Daily: %d (prev: %d)\n  Weekly: %d (prev: %d)\n  Monthly: %d (prev: %d)\n",
			s.BaseDate, s.AccountID,
			s.PVCount.Daily, s.PVCount.DailyPrev,
			s.PVCount.Weekly, s.PVCount.WeeklyPrev,
			s.PVCount.Monthly, s.PVCount.MonthlyPrev,
			s.OrderCount.Daily, s.OrderCount.DailyPrev,
			s.OrderCount.Weekly, s.OrderCount.WeeklyPrev,
			s.OrderCount.Monthly, s.OrderCount.MonthlyPrev,
			s.PayAmount.Daily, s.PayAmount.DailyPrev,
			s.PayAmount.Weekly, s.PayAmount.WeeklyPrev,
			s.PayAmount.Monthly, s.PayAmount.MonthlyPrev,
		)
		return err
	default:
		return fmt.Errorf("unsupported format: %s", format)
	}
}
