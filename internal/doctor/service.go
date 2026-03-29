package doctor

import (
	"context"
	"os"
	"os/exec"
	"runtime"

	"github.com/junghoonkye/smartstore-cli/internal/auth"
	"github.com/junghoonkye/smartstore-cli/internal/config"
	"github.com/junghoonkye/smartstore-cli/internal/version"
)

type Check struct {
	Name    string `json:"name"`
	Status  string `json:"status"`
	Message string `json:"message,omitempty"`
}

type AuthReport struct {
	PythonBin string  `json:"python_bin"`
	HelperDir string  `json:"helper_dir"`
	Checks    []Check `json:"checks"`
}

type Report struct {
	Version    string        `json:"version"`
	GoVersion  string        `json:"go_version"`
	OS         string        `json:"os"`
	Arch       string        `json:"arch"`
	ConfigFile string        `json:"config_file"`
	Config     config.Status `json:"config"`
	Auth       AuthReport    `json:"auth"`
	Checks     []Check       `json:"checks"`
}

type Service struct {
	paths       config.Paths
	configStat  config.Status
	loginConfig auth.LoginConfig
	authService *auth.Service
}

func NewService(
	paths config.Paths,
	configStat config.Status,
	loginConfig auth.LoginConfig,
	authService *auth.Service,
) *Service {
	return &Service{
		paths:       paths,
		configStat:  configStat,
		loginConfig: loginConfig,
		authService: authService,
	}
}

func (s *Service) Run(ctx context.Context) (Report, error) {
	info := version.Current()

	checks := []Check{
		s.checkDir("config_dir", s.paths.ConfigDir),
		s.checkDir("cache_dir", s.paths.CacheDir),
		s.checkFile("config_file", s.paths.ConfigFile),
		s.checkFile("session_file", s.paths.SessionFile),
	}

	authReport := s.runAuthChecks(ctx)

	return Report{
		Version:    info.Version,
		GoVersion:  runtime.Version(),
		OS:         runtime.GOOS,
		Arch:       runtime.GOARCH,
		ConfigFile: s.paths.ConfigFile,
		Config:     s.configStat,
		Auth:       authReport,
		Checks:     checks,
	}, nil
}

func (s *Service) RunAuth(ctx context.Context) (AuthReport, error) {
	return s.runAuthChecks(ctx), nil
}

func (s *Service) runAuthChecks(ctx context.Context) AuthReport {
	checks := []Check{
		s.checkPythonBinary(),
		s.checkHelperDir(),
		s.checkPythonModule(),
		s.checkChromium(),
	}

	if s.authService != nil {
		status, err := s.authService.Status(ctx)
		if err != nil {
			checks = append(checks, Check{
				Name:    "session_valid",
				Status:  "error",
				Message: err.Error(),
			})
		} else if status.Active {
			if status.Validated && status.Valid {
				checks = append(checks, Check{
					Name:   "session_valid",
					Status: "ok",
				})
			} else if status.Validated && !status.Valid {
				checks = append(checks, Check{
					Name:    "session_valid",
					Status:  "warning",
					Message: status.ValidationError,
				})
			} else {
				checks = append(checks, Check{
					Name:    "session_valid",
					Status:  "ok",
					Message: "session present but not validated",
				})
			}
		} else {
			checks = append(checks, Check{
				Name:    "session_valid",
				Status:  "warning",
				Message: "no active session",
			})
		}
	}

	return AuthReport{
		PythonBin: s.loginConfig.PythonBin,
		HelperDir: s.loginConfig.HelperDir,
		Checks:    checks,
	}
}

func (s *Service) checkDir(name, path string) Check {
	info, err := os.Stat(path)
	if err != nil {
		if os.IsNotExist(err) {
			return Check{Name: name, Status: "warning", Message: "does not exist: " + path}
		}
		return Check{Name: name, Status: "error", Message: err.Error()}
	}
	if !info.IsDir() {
		return Check{Name: name, Status: "error", Message: "not a directory: " + path}
	}
	return Check{Name: name, Status: "ok"}
}

func (s *Service) checkFile(name, path string) Check {
	_, err := os.Stat(path)
	if err != nil {
		if os.IsNotExist(err) {
			return Check{Name: name, Status: "warning", Message: "does not exist: " + path}
		}
		return Check{Name: name, Status: "error", Message: err.Error()}
	}
	return Check{Name: name, Status: "ok"}
}

func (s *Service) checkPythonBinary() Check {
	_, err := exec.LookPath(s.loginConfig.PythonBin)
	if err != nil {
		return Check{
			Name:    "python_binary",
			Status:  "error",
			Message: s.loginConfig.PythonBin + " not found in PATH",
		}
	}
	return Check{Name: "python_binary", Status: "ok"}
}

func (s *Service) checkHelperDir() Check {
	return s.checkDir("auth_helper_dir", s.loginConfig.HelperDir)
}

func (s *Service) checkPythonModule() Check {
	cmd := exec.Command(s.loginConfig.PythonBin, "-c", "import storectl_auth_helper")
	cmd.Dir = s.loginConfig.HelperDir
	if err := cmd.Run(); err != nil {
		return Check{
			Name:    "playwright_module",
			Status:  "warning",
			Message: "storectl_auth_helper not importable; run: pip install -e auth-helper/",
		}
	}
	return Check{Name: "playwright_module", Status: "ok"}
}

func (s *Service) checkChromium() Check {
	cmd := exec.Command(s.loginConfig.PythonBin, "-c", "from playwright.sync_api import sync_playwright; p=sync_playwright().start(); p.chromium; p.stop()")
	if err := cmd.Run(); err != nil {
		return Check{
			Name:    "chromium_installed",
			Status:  "warning",
			Message: "playwright chromium not installed; run: playwright install chromium",
		}
	}
	return Check{Name: "chromium_installed", Status: "ok"}
}
