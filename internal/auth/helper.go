package auth

import (
	"context"
	"encoding/json"
	"fmt"
	"os/exec"
)

type LoginResult struct {
	StorageStatePath string `json:"storage_state_path"`
}

type LoginRunner interface {
	Login(ctx context.Context, cfg LoginConfig) (LoginResult, error)
	Refresh(ctx context.Context, cfg LoginConfig) (LoginResult, error)
}

type PythonLoginRunner struct{}

func (PythonLoginRunner) Login(ctx context.Context, cfg LoginConfig) (LoginResult, error) {
	return runHelper(ctx, cfg, "login")
}

func (PythonLoginRunner) Refresh(ctx context.Context, cfg LoginConfig) (LoginResult, error) {
	return runHelper(ctx, cfg, "refresh")
}

func runHelper(ctx context.Context, cfg LoginConfig, subcmd string) (LoginResult, error) {
	args := []string{
		"-m", "storectl_auth_helper",
		subcmd,
		"--storage-state", cfg.StorageStatePath,
	}

	cmd := exec.CommandContext(ctx, cfg.PythonBin, args...)
	cmd.Dir = cfg.HelperDir

	output, err := cmd.CombinedOutput()
	if err != nil {
		return LoginResult{}, fmt.Errorf("auth helper %s failed: %w\nOutput: %s", subcmd, err, string(output))
	}

	var result LoginResult
	if err := json.Unmarshal(output, &result); err != nil {
		return LoginResult{}, fmt.Errorf("failed to parse auth helper output: %w\nOutput: %s", err, string(output))
	}

	return result, nil
}
