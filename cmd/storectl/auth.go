package main

import (
	"encoding/json"
	"fmt"
	"io"

	"github.com/junghoonkye/smartstore-cli/internal/auth"
	"github.com/junghoonkye/smartstore-cli/internal/doctor"
	"github.com/junghoonkye/smartstore-cli/internal/output"
	"github.com/junghoonkye/smartstore-cli/internal/session"
	"github.com/spf13/cobra"
)

func newAuthCmd(opts *rootOptions) *cobra.Command {
	cmd := &cobra.Command{
		Use:   "auth",
		Short: "Manage Naver Smart Store session state",
	}

	cmd.AddCommand(
		&cobra.Command{
			Use:   "login",
			Short: "Start browser-assisted login",
			RunE: func(cmd *cobra.Command, _ []string) error {
				app, err := newAppContext(opts)
				if err != nil {
					return err
				}

				sess, err := app.authService.Login(cmd.Context())
				if err != nil {
					return err
				}

				return writeImportResult(cmd.OutOrStdout(), app.format, app.paths.SessionFile, sess)
			},
		},
		&cobra.Command{
			Use:   "import-playwright-state <path>",
			Short: "Import Playwright storage state into storectl session storage",
			Args:  cobra.ExactArgs(1),
			RunE: func(cmd *cobra.Command, args []string) error {
				app, err := newAppContext(opts)
				if err != nil {
					return err
				}

				sess, err := app.authService.ImportPlaywrightState(cmd.Context(), args[0])
				if err != nil {
					return err
				}

				return writeImportResult(cmd.OutOrStdout(), app.format, app.paths.SessionFile, sess)
			},
		},
		&cobra.Command{
			Use:   "status",
			Short: "Inspect the stored session state",
			RunE: func(cmd *cobra.Command, _ []string) error {
				app, err := newAppContext(opts)
				if err != nil {
					return err
				}

				status, err := app.authService.Status(cmd.Context())
				if err != nil {
					return err
				}

				return writeAuthStatus(cmd.OutOrStdout(), app.format, status)
			},
		},
		&cobra.Command{
			Use:   "logout",
			Short: "Clear the stored session state",
			RunE: func(cmd *cobra.Command, _ []string) error {
				app, err := newAppContext(opts)
				if err != nil {
					return err
				}

				cleared, err := app.authService.Logout(cmd.Context())
				if err != nil {
					return err
				}

				return writeLogoutResult(cmd.OutOrStdout(), app.format, app.paths.SessionFile, cleared)
			},
		},
		&cobra.Command{
			Use:   "refresh",
			Short: "Refresh the session using existing NID cookies (headless)",
			RunE: func(cmd *cobra.Command, _ []string) error {
				app, err := newAppContext(opts)
				if err != nil {
					return err
				}

				sess, err := app.authService.Refresh(cmd.Context())
				if err != nil {
					return fmt.Errorf("session refresh failed: %w\nRun `storectl auth login` for manual login", err)
				}

				return writeImportResult(cmd.OutOrStdout(), app.format, app.paths.SessionFile, sess)
			},
		},
		&cobra.Command{
			Use:   "doctor",
			Short: "Check whether auth login prerequisites are ready",
			RunE: func(cmd *cobra.Command, _ []string) error {
				app, err := newAppContext(opts)
				if err != nil {
					return err
				}
				configStatus, err := app.configService.Status(cmd.Context())
				if err != nil {
					return err
				}

				report, err := doctor.NewService(
					app.paths,
					configStatus,
					app.loginConfig,
					app.authService,
				).RunAuth(cmd.Context())
				if err != nil {
					return err
				}

				return output.WriteAuthDoctorReport(cmd.OutOrStdout(), app.format, report)
			},
		},
	)

	return cmd
}

func writeAuthStatus(w io.Writer, format output.Format, status auth.Status) error {
	switch format {
	case output.FormatJSON:
		encoder := json.NewEncoder(w)
		encoder.SetIndent("", "  ")
		return encoder.Encode(status)
	case output.FormatCSV:
		return fmt.Errorf("csv output is not supported for auth status")
	case output.FormatTable:
		if !status.Active {
			_, err := fmt.Fprintf(w, "No active session\nSession file: %s\n", status.SessionFile)
			return err
		}

		state := "active"
		if status.Expired {
			state = "expired"
		}

		liveCheck := "not checked"
		if status.Validated {
			liveCheck = "valid"
			if !status.Valid {
				liveCheck = "invalid"
			}
		}

		_, err := fmt.Fprintf(
			w,
			"Session: %s\nProvider: %s\nLive Check: %s\nRetrieved At: %s\nSession File: %s\n",
			state,
			status.Provider,
			liveCheck,
			status.RetrievedAt.Format("2006-01-02 15:04:05Z07:00"),
			status.SessionFile,
		)
		if err != nil {
			return err
		}
		if status.LastUsedAt != nil {
			if _, err := fmt.Fprintf(w, "Last Used At: %s\n", status.LastUsedAt.Format("2006-01-02 15:04:05Z07:00")); err != nil {
				return err
			}
		}
		if status.Validated && status.CheckedAt != nil {
			if _, err := fmt.Fprintf(w, "Checked At: %s\n", status.CheckedAt.Format("2006-01-02 15:04:05Z07:00")); err != nil {
				return err
			}
		}
		if status.ValidationError != "" {
			_, err = fmt.Fprintf(w, "Validation Error: %s\n", status.ValidationError)
		}
		return err
	default:
		return fmt.Errorf("unsupported format: %s", format)
	}
}

func writeImportResult(w io.Writer, format output.Format, sessionFile string, sess *session.Session) error {
	payload := map[string]any{
		"provider":     sess.Provider,
		"cookie_count": len(sess.Cookies),
		"storage_keys": len(sess.Storage),
		"session_file": sessionFile,
		"retrieved_at": sess.RetrievedAt,
	}

	switch format {
	case output.FormatJSON:
		encoder := json.NewEncoder(w)
		encoder.SetIndent("", "  ")
		return encoder.Encode(payload)
	case output.FormatCSV:
		return fmt.Errorf("csv output is not supported for auth import")
	case output.FormatTable:
		_, err := fmt.Fprintf(
			w,
			"Imported session\nProvider: %s\nCookies: %d\nStorage Keys: %d\nSession File: %s\n",
			sess.Provider,
			len(sess.Cookies),
			len(sess.Storage),
			sessionFile,
		)
		return err
	default:
		return fmt.Errorf("unsupported format: %s", format)
	}
}

func writeLogoutResult(w io.Writer, format output.Format, sessionFile string, cleared bool) error {
	payload := map[string]any{
		"cleared":      cleared,
		"session_file": sessionFile,
	}

	switch format {
	case output.FormatJSON:
		encoder := json.NewEncoder(w)
		encoder.SetIndent("", "  ")
		return encoder.Encode(payload)
	case output.FormatCSV:
		return fmt.Errorf("csv output is not supported for auth logout")
	case output.FormatTable:
		if cleared {
			_, err := fmt.Fprintf(w, "Cleared session file: %s\n", sessionFile)
			return err
		}

		_, err := fmt.Fprintf(w, "No stored session found at: %s\n", sessionFile)
		return err
	default:
		return fmt.Errorf("unsupported format: %s", format)
	}
}
