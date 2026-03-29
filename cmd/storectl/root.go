package main

import (
	"context"
	"errors"
	"path/filepath"

	"github.com/junghoonkye/smartstore-cli/internal/auth"
	storeclient "github.com/junghoonkye/smartstore-cli/internal/client"
	"github.com/junghoonkye/smartstore-cli/internal/config"
	"github.com/junghoonkye/smartstore-cli/internal/output"
	"github.com/junghoonkye/smartstore-cli/internal/session"
	"github.com/spf13/cobra"
)

type rootOptions struct {
	outputFormat string
	configDir    string
	sessionFile  string
}

type appContext struct {
	format        output.Format
	paths         config.Paths
	config        config.File
	configService *config.Service
	loginConfig   auth.LoginConfig
	authService   *auth.Service
	client        *storeclient.Client
}

func newRootCmd() *cobra.Command {
	opts := &rootOptions{}

	cmd := &cobra.Command{
		Use:   "storectl",
		Short: "CLI for Naver Smart Store seller data and analytics",
		Long: "storectl is the CLI binary for smartstore-cli, an unofficial Naver Smart Store " +
			"web client with browser-assisted login for seller center access.",
		SilenceUsage: true,
		PersistentPreRunE: func(cmd *cobra.Command, _ []string) error {
			_, err := output.ParseFormat(opts.outputFormat)
			return err
		},
	}

	cmd.PersistentFlags().StringVar(
		&opts.outputFormat,
		"output",
		string(output.FormatTable),
		"Output format: table, json, csv",
	)
	cmd.PersistentFlags().StringVar(
		&opts.configDir,
		"config-dir",
		"",
		"Override the config directory",
	)
	cmd.PersistentFlags().StringVar(
		&opts.sessionFile,
		"session-file",
		"",
		"Override the session file path",
	)

	cmd.AddCommand(
		newVersionCmd(opts),
		newDoctorCmd(opts),
		newConfigCmd(opts),
		newAuthCmd(opts),
		newProductCmd(opts),
		newOrderCmd(opts),
		newStatsCmd(opts),
		newSettlementCmd(opts),
		newInquiryCmd(opts),
		newReviewCmd(opts),
		newSellerCmd(opts),
		newNotificationCmd(opts),
	)

	return cmd
}

func newAppContext(opts *rootOptions) (*appContext, error) {
	format, err := output.ParseFormat(opts.outputFormat)
	if err != nil {
		return nil, err
	}

	paths, err := config.DefaultPaths()
	if err != nil {
		return nil, err
	}

	if opts.configDir != "" {
		paths.ConfigDir = opts.configDir
		paths.ConfigFile = filepath.Join(opts.configDir, "config.json")
		paths.SessionFile = filepath.Join(opts.configDir, "session.json")
	}

	if opts.sessionFile != "" {
		paths.SessionFile = opts.sessionFile
	}

	store := session.NewFileStore(paths.SessionFile)
	sess, err := store.Load(context.Background())
	if err != nil && !errors.Is(err, session.ErrNoSession) {
		return nil, err
	}

	loginConfig := auth.DefaultLoginConfig(paths.CacheDir)
	configService := config.NewService(paths.ConfigFile)
	cfg, err := configService.Load(context.Background())
	if err != nil {
		return nil, err
	}

	authSvc := auth.NewService(store, paths.SessionFile, auth.Options{
		LoginConfig: loginConfig,
	})

	client := storeclient.New(storeclient.Config{
		Session:          sess,
		SessionStore:     store,
		SessionRefresher: authSvc,
	})

	// Set validator after client creation (circular dep).
	authSvc.SetValidator(client)

	return &appContext{
		format:        format,
		paths:         paths,
		config:        cfg,
		configService: configService,
		loginConfig:   loginConfig,
		authService:   authSvc,
		client:        client,
	}, nil
}
