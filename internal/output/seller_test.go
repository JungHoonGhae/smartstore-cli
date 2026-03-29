package output

import (
	"bytes"
	"strings"
	"testing"

	"github.com/junghoonkye/smartstore-cli/internal/domain"
)

func TestWriteSellerInfo_Table(t *testing.T) {
	var buf bytes.Buffer
	info := domain.SellerInfo{
		ChannelID:     100,
		ChannelName:   "TestStore",
		ChannelURL:    "teststore",
		FullURL:       "https://smartstore.naver.com/teststore",
		ChannelType:   "STOREFARM",
		ChannelStatus: "OPEN",
		SellerStatus:  "ACTIVE",
	}
	info.Account.AccountID = "seller123"
	info.Represent.RepresentName = "Kim"
	info.Represent.RepresentType = "INDIVIDUAL"
	info.Pay.BankName = "KB"
	info.Pay.AccountHolder = "Kim"
	info.ContactInfo.TelNo.FormattedNumber = "010-1234-5678"

	if err := WriteSellerInfo(&buf, FormatTable, info); err != nil {
		t.Fatalf("WriteSellerInfo returned error: %v", err)
	}

	got := buf.String()
	checks := []string{
		"Channel ID:      100",
		"Channel Name:    TestStore",
		"Account ID:      seller123",
		"Tel:             010-1234-5678",
	}
	for _, want := range checks {
		if !strings.Contains(got, want) {
			t.Errorf("expected %q in output, got %q", want, got)
		}
	}
}

func TestWriteSellerGrade_Table(t *testing.T) {
	var buf bytes.Buffer
	grade := domain.SellerGrade{
		ActionGrade:   "POWER",
		GoodServiceYN: true,
		AppliedYM:     "2026-03",
	}
	penalties := domain.Penalties{
		OccurredScoreTotal:  5,
		OccurredScoreRatio:  2.5,
		RestraintStepString: "NONE",
		AppliedYmd:          "2026-03-01",
	}

	if err := WriteSellerGrade(&buf, FormatTable, grade, penalties); err != nil {
		t.Fatalf("WriteSellerGrade returned error: %v", err)
	}

	got := buf.String()
	checks := []string{
		"Grade:           POWER",
		"Good Service:    true",
		"Score Total:     5",
		"Score Ratio:     2.5",
		"Restraint:       NONE",
	}
	for _, want := range checks {
		if !strings.Contains(got, want) {
			t.Errorf("expected %q in output, got %q", want, got)
		}
	}
}
