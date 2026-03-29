package output

import (
	"encoding/json"
	"fmt"
	"io"

	"github.com/junghoonkye/smartstore-cli/internal/domain"
)

func WriteSettlementDashboard(w io.Writer, format Format, d domain.SettlementDashboard) error {
	switch format {
	case FormatJSON:
		encoder := json.NewEncoder(w)
		encoder.SetIndent("", "  ")
		return encoder.Encode(d)
	case FormatCSV:
		_, err := fmt.Fprintf(
			w,
			"today_amount,quick_today_amount,expected_amount,quick_expected_amount,charge_balance,next_working_day\n%s,%s,%s,%s,%s,%s\n",
			d.TodayAmount, d.QuickTodayAmount,
			d.ExpectedAmount, d.QuickExpectedAmount,
			d.ChargeBalance, d.NextWorkingDay,
		)
		return err
	case FormatTable:
		_, err := fmt.Fprintf(
			w,
			"Settlement Dashboard\n\n"+
				"  Today Amount:          %s\n"+
				"  Quick Today Amount:    %s\n"+
				"  Expected Amount:       %s\n"+
				"  Quick Expected Amount: %s\n"+
				"  Charge Balance:        %s\n"+
				"  Next Working Day:      %s\n",
			d.TodayAmount, d.QuickTodayAmount,
			d.ExpectedAmount, d.QuickExpectedAmount,
			d.ChargeBalance, d.NextWorkingDay,
		)
		return err
	default:
		return fmt.Errorf("unsupported format: %s", format)
	}
}
