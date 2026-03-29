package output

import (
	"encoding/json"
	"fmt"
	"io"
	"strconv"

	"github.com/junghoonkye/smartstore-cli/internal/domain"
)

// WriteSellerInfo renders seller information.
func WriteSellerInfo(w io.Writer, format Format, info domain.SellerInfo) error {
	switch format {
	case FormatJSON:
		encoder := json.NewEncoder(w)
		encoder.SetIndent("", "  ")
		return encoder.Encode(info)
	case FormatCSV:
		_, err := fmt.Fprintf(
			w,
			"channel_id,channel_name,channel_url,full_url,type,channel_status,seller_status,account_id,represent_name,represent_type,bank_name,account_holder,tel\n%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n",
			strconv.FormatInt(info.ChannelID, 10),
			info.ChannelName,
			info.ChannelURL,
			info.FullURL,
			info.ChannelType,
			info.ChannelStatus,
			info.SellerStatus,
			info.Account.AccountID,
			info.Represent.RepresentName,
			info.Represent.RepresentType,
			info.Pay.BankName,
			info.Pay.AccountHolder,
			info.ContactInfo.TelNo.FormattedNumber,
		)
		return err
	case FormatTable:
		_, err := fmt.Fprintf(
			w,
			"Seller Info\n\n"+
				"  Channel ID:      %d\n"+
				"  Channel Name:    %s\n"+
				"  Channel URL:     %s\n"+
				"  Full URL:        %s\n"+
				"  Type:            %s\n"+
				"  Channel Status:  %s\n"+
				"  Seller Status:   %s\n"+
				"  Account ID:      %s\n"+
				"  Representative:  %s (%s)\n"+
				"  Bank:            %s (%s)\n"+
				"  Tel:             %s\n",
			info.ChannelID,
			info.ChannelName,
			info.ChannelURL,
			info.FullURL,
			info.ChannelType,
			info.ChannelStatus,
			info.SellerStatus,
			info.Account.AccountID,
			info.Represent.RepresentName, info.Represent.RepresentType,
			info.Pay.BankName, info.Pay.AccountHolder,
			info.ContactInfo.TelNo.FormattedNumber,
		)
		return err
	default:
		return fmt.Errorf("unsupported format: %s", format)
	}
}

// sellerGradeView combines SellerGrade and Penalties for output.
type sellerGradeView struct {
	Grade     domain.SellerGrade `json:"grade"`
	Penalties domain.Penalties   `json:"penalties"`
}

// WriteSellerGrade renders seller grade and penalty information.
func WriteSellerGrade(w io.Writer, format Format, grade domain.SellerGrade, penalties domain.Penalties) error {
	view := sellerGradeView{Grade: grade, Penalties: penalties}

	switch format {
	case FormatJSON:
		encoder := json.NewEncoder(w)
		encoder.SetIndent("", "  ")
		return encoder.Encode(view)
	case FormatCSV:
		_, err := fmt.Fprintf(
			w,
			"action_grade,good_service,applied_ym,penalty_score,penalty_ratio,restraint_step,penalty_applied\n%s,%t,%s,%d,%s,%s,%s\n",
			grade.ActionGrade,
			grade.GoodServiceYN,
			grade.AppliedYM,
			penalties.OccurredScoreTotal,
			formatFloat(penalties.OccurredScoreRatio),
			penalties.RestraintStepString,
			penalties.AppliedYmd,
		)
		return err
	case FormatTable:
		_, err := fmt.Fprintf(
			w,
			"Seller Grade\n\n"+
				"  Grade:           %s\n"+
				"  Good Service:    %t\n"+
				"  Applied:         %s\n"+
				"\nPenalties\n\n"+
				"  Score Total:     %d\n"+
				"  Score Ratio:     %s\n"+
				"  Restraint:       %s\n"+
				"  Applied:         %s\n",
			grade.ActionGrade,
			grade.GoodServiceYN,
			grade.AppliedYM,
			penalties.OccurredScoreTotal,
			formatFloat(penalties.OccurredScoreRatio),
			penalties.RestraintStepString,
			penalties.AppliedYmd,
		)
		return err
	default:
		return fmt.Errorf("unsupported format: %s", format)
	}
}
