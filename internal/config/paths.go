package config

import (
	"os"
	"path/filepath"
)

const AppName = "storectl"

type Paths struct {
	ConfigDir   string
	CacheDir    string
	ConfigFile  string
	SessionFile string
}

func DefaultPaths() (Paths, error) {
	configRoot, err := os.UserConfigDir()
	if err != nil {
		return Paths{}, err
	}

	cacheRoot, err := os.UserCacheDir()
	if err != nil {
		return Paths{}, err
	}

	configDir := filepath.Join(configRoot, AppName)

	return Paths{
		ConfigDir:   configDir,
		CacheDir:    filepath.Join(cacheRoot, AppName),
		ConfigFile:  filepath.Join(configDir, "config.json"),
		SessionFile: filepath.Join(configDir, "session.json"),
	}, nil
}
