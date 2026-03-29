package output

import (
	"encoding/csv"
	"encoding/json"
	"fmt"
	"io"
	"sort"
	"strconv"
	"strings"

	"github.com/junghoonkye/smartstore-cli/internal/domain"
)

// notificationListView combines counts and recent activities for output.
type notificationListView struct {
	Counts     domain.NotificationCounts    `json:"counts"`
	Activities []domain.NotificationActivity `json:"activities"`
}

// WriteNotifications renders notification counts and recent activities.
func WriteNotifications(w io.Writer, format Format, counts domain.NotificationCounts, activities []domain.NotificationActivity) error {
	view := notificationListView{Counts: counts, Activities: activities}

	switch format {
	case FormatJSON:
		encoder := json.NewEncoder(w)
		encoder.SetIndent("", "  ")
		return encoder.Encode(view)
	case FormatCSV:
		writer := csv.NewWriter(w)
		defer writer.Flush()

		// Write counts section.
		if err := writer.Write([]string{"section", "category", "count", "title", "contents", "date"}); err != nil {
			return err
		}

		categories := sortedKeys(counts)
		for _, cat := range categories {
			if err := writer.Write([]string{
				"count", cat, strconv.Itoa(counts[cat]), "", "", "",
			}); err != nil {
				return err
			}
		}

		// Write activities section.
		for _, a := range activities {
			if err := writer.Write([]string{
				"activity", a.Category, "", a.Title, a.Contents, a.CreatedAt,
			}); err != nil {
				return err
			}
		}
		return nil
	case FormatTable:
		// Counts.
		_, _ = fmt.Fprintln(w, "Notification Counts")
		_, _ = fmt.Fprintln(w)

		categories := sortedKeys(counts)
		hasNonZero := false
		for _, cat := range categories {
			cnt := counts[cat]
			if cnt > 0 {
				_, _ = fmt.Fprintf(w, "  %-30s  %d\n", cat, cnt)
				hasNonZero = true
			}
		}
		if !hasNonZero {
			_, _ = fmt.Fprintln(w, "  No pending notifications.")
		}

		// Activities.
		_, _ = fmt.Fprintln(w)
		_, _ = fmt.Fprintln(w, "Recent Activities")
		_, _ = fmt.Fprintln(w)

		if len(activities) == 0 {
			_, err := fmt.Fprintln(w, "  No recent activities.")
			return err
		}

		header := fmt.Sprintf("%-20s  %-30s  %s",
			"CATEGORY", "TITLE", "DATE")
		if _, err := fmt.Fprintln(w, header); err != nil {
			return err
		}
		if _, err := fmt.Fprintln(w, strings.Repeat("-", len(header))); err != nil {
			return err
		}

		for _, a := range activities {
			title := truncate(a.Title, 30)
			if _, err := fmt.Fprintf(w, "%-20s  %-30s  %s\n",
				a.Category, title, a.CreatedAt,
			); err != nil {
				return err
			}
		}
		return nil
	default:
		return fmt.Errorf("unsupported format: %s", format)
	}
}

// sortedKeys returns the keys of a map sorted alphabetically.
func sortedKeys(m domain.NotificationCounts) []string {
	keys := make([]string, 0, len(m))
	for k := range m {
		keys = append(keys, k)
	}
	sort.Strings(keys)
	return keys
}
