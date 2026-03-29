package output

import (
	"bytes"
	"encoding/json"
	"strings"
	"testing"

	"github.com/junghoonkye/smartstore-cli/internal/domain"
)

func TestWriteOrderDashboard_Table(t *testing.T) {
	var buf bytes.Buffer
	d := domain.OrderDeliveryDashboard{
		PaymentWaitCases:        2,
		NewOrderCases:           5,
		TodayDispatchCases:      3,
		DeliveringCases:         1,
		DeliveredCases:          10,
		PurchaseCompletionCases: 7,
	}

	if err := WriteOrderDashboard(&buf, FormatTable, d); err != nil {
		t.Fatalf("WriteOrderDashboard returned error: %v", err)
	}

	got := buf.String()
	// total = 2+5+3+0+0+0+1+10+0+0+7 = 28
	if !strings.Contains(got, "total: 28") {
		t.Errorf("expected 'total: 28' in output, got %q", got)
	}
	if !strings.Contains(got, "Payment Wait:") {
		t.Errorf("expected 'Payment Wait:' label in output, got %q", got)
	}
	if !strings.Contains(got, "New Order:") {
		t.Errorf("expected 'New Order:' label in output, got %q", got)
	}
}

func TestWriteOrderDashboard_JSON(t *testing.T) {
	var buf bytes.Buffer
	d := domain.OrderDeliveryDashboard{
		PaymentWaitCases: 2,
		NewOrderCases:    5,
	}

	if err := WriteOrderDashboard(&buf, FormatJSON, d); err != nil {
		t.Fatalf("WriteOrderDashboard returned error: %v", err)
	}

	var decoded domain.OrderDeliveryDashboard
	if err := json.Unmarshal(buf.Bytes(), &decoded); err != nil {
		t.Fatalf("failed to decode JSON output: %v", err)
	}

	if decoded.PaymentWaitCases != 2 {
		t.Errorf("PaymentWaitCases: got %d, want %d", decoded.PaymentWaitCases, 2)
	}
	if decoded.NewOrderCases != 5 {
		t.Errorf("NewOrderCases: got %d, want %d", decoded.NewOrderCases, 5)
	}
}
