package auth

import (
	"context"
	"errors"
	"fmt"
	"os"
	"path/filepath"
	"time"

	"github.com/junghoonkye/smartstore-cli/internal/session"
)

type LoginConfig struct {
	PythonBin        string
	HelperDir        string
	StorageStatePath string
}

type Options struct {
	LoginConfig LoginConfig
	Runner      LoginRunner
	Validator   SessionValidator
}

type Service struct {
	store       session.Store
	sessionFile string
	loginConfig LoginConfig
	runner      LoginRunner
	validator   SessionValidator
}

type Status struct {
	Active          bool       `json:"active"`
	Expired         bool       `json:"expired"`
	Provider        string     `json:"provider,omitempty"`
	CookieCount     int        `json:"cookie_count,omitempty"`
	StorageKeys     int        `json:"storage_keys,omitempty"`
	RetrievedAt     *time.Time `json:"retrieved_at,omitempty"`
	ExpiresAt       *time.Time `json:"expires_at,omitempty"`
	LastUsedAt      *time.Time `json:"last_used_at,omitempty"`
	SessionFile     string     `json:"session_file"`
	Validated       bool       `json:"validated"`
	Valid           bool       `json:"valid"`
	ValidationError string     `json:"validation_error,omitempty"`
	CheckedAt       *time.Time `json:"checked_at,omitempty"`
}

type SessionValidator interface {
	ValidateSession(context.Context) error
}

func DefaultLoginConfig(cacheDir string) LoginConfig {
	pythonBin := os.Getenv("STORECTL_AUTH_HELPER_PYTHON")
	if pythonBin == "" {
		pythonBin = "python3"
	}

	helperDir := os.Getenv("STORECTL_AUTH_HELPER_DIR")
	if helperDir == "" {
		helperDir = resolveDefaultHelperDir()
	}

	storageStatePath := os.Getenv("STORECTL_AUTH_STORAGE_STATE")
	if storageStatePath == "" {
		storageStatePath = filepath.Join(cacheDir, "auth", "playwright-storage-state.json")
	}

	return LoginConfig{
		PythonBin:        pythonBin,
		HelperDir:        helperDir,
		StorageStatePath: storageStatePath,
	}
}

func resolveDefaultHelperDir() string {
	candidates := []string{"auth-helper"}

	if exePath, err := os.Executable(); err == nil {
		exeDir := filepath.Dir(exePath)
		candidates = append(candidates,
			filepath.Join(exeDir, "auth-helper"),
			filepath.Join(exeDir, "..", "libexec", "auth-helper"),
			filepath.Join(exeDir, "..", "share", "storectl", "auth-helper"),
		)
	}

	for _, candidate := range candidates {
		if candidate == "" {
			continue
		}
		if info, err := os.Stat(candidate); err == nil && info.IsDir() {
			return candidate
		}
	}

	return candidates[0]
}

func NewService(store session.Store, sessionFile string, opts Options) *Service {
	runner := opts.Runner
	if runner == nil {
		runner = PythonLoginRunner{}
	}

	return &Service{
		store:       store,
		sessionFile: sessionFile,
		loginConfig: opts.LoginConfig,
		runner:      runner,
		validator:   opts.Validator,
	}
}

// SetValidator sets the session validator (resolves circular dependency with client).
func (s *Service) SetValidator(v SessionValidator) {
	s.validator = v
}

func (s *Service) Login(ctx context.Context) (*session.Session, error) {
	result, err := s.runner.Login(ctx, s.loginConfig)
	if err != nil {
		return nil, err
	}

	return s.ImportPlaywrightState(ctx, result.StorageStatePath)
}

func (s *Service) Status(ctx context.Context) (Status, error) {
	sess, err := s.store.Load(ctx)
	if err != nil {
		if errors.Is(err, session.ErrNoSession) {
			return Status{
				Active:      false,
				Expired:     false,
				SessionFile: s.sessionFile,
			}, nil
		}

		return Status{}, err
	}

	status := Status{
		Active:      true,
		Expired:     sess.IsExpired(time.Now()),
		Provider:    sess.Provider,
		CookieCount: len(sess.Cookies),
		StorageKeys: len(sess.Storage),
		RetrievedAt: &sess.RetrievedAt,
		ExpiresAt:   sess.ExpiresAt,
		LastUsedAt:  sess.LastUsedAt,
		SessionFile: s.sessionFile,
	}

	if s.validator != nil {
		checkedAt := time.Now().UTC()
		status.Validated = true
		status.CheckedAt = &checkedAt
		if err := s.validator.ValidateSession(ctx); err != nil {
			status.Valid = false
			status.ValidationError = err.Error()
			return status, nil
		}
		status.Valid = true
	}

	return status, nil
}

// Refresh attempts to refresh the session using existing NID cookies
// via a headless Playwright run. This implements client.SessionRefresher.
func (s *Service) Refresh(ctx context.Context) (*session.Session, error) {
	result, err := s.runner.Refresh(ctx, s.loginConfig)
	if err != nil {
		return nil, fmt.Errorf("session refresh failed: %w", err)
	}

	return s.ImportPlaywrightState(ctx, result.StorageStatePath)
}

// RefreshSession implements client.SessionRefresher.
func (s *Service) RefreshSession(ctx context.Context) (*session.Session, error) {
	return s.Refresh(ctx)
}

func (s *Service) Logout(ctx context.Context) (bool, error) {
	if _, err := s.store.Load(ctx); err != nil {
		if errors.Is(err, session.ErrNoSession) {
			return false, nil
		}

		return false, err
	}

	if err := s.store.Clear(ctx); err != nil {
		return false, err
	}

	return true, nil
}
