package client

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"strings"
	"sync"
	"time"

	"github.com/junghoonkye/smartstore-cli/internal/domain"
	"github.com/junghoonkye/smartstore-cli/internal/session"
)

const defaultAPIBaseURL = "https://sell.smartstore.naver.com"

// minRequestInterval enforces a minimum gap between requests to avoid
// being rate-limited by the server.
const minRequestInterval = 200 * time.Millisecond

// SessionRefresher can refresh an expired session and return a new one.
type SessionRefresher interface {
	RefreshSession(ctx context.Context) (*session.Session, error)
}

type Config struct {
	HTTPClient       *http.Client
	APIBaseURL       string
	Session          *session.Session
	SessionStore     session.Store
	SessionRefresher SessionRefresher
}

type Client struct {
	httpClient       *http.Client
	apiBaseURL       string
	session          *session.Session
	sessionStore     session.Store
	sessionRefresher SessionRefresher

	mu              sync.Mutex
	lastCall        time.Time
	sessionInitDone bool
}

func New(cfg Config) *Client {
	httpClient := cfg.HTTPClient
	if httpClient == nil {
		httpClient = &http.Client{Timeout: 15 * time.Second}
	}

	apiBaseURL := strings.TrimRight(cfg.APIBaseURL, "/")
	if apiBaseURL == "" {
		apiBaseURL = defaultAPIBaseURL
	}

	return &Client{
		httpClient:       httpClient,
		apiBaseURL:       apiBaseURL,
		session:          cfg.Session,
		sessionStore:     cfg.SessionStore,
		sessionRefresher: cfg.SessionRefresher,
	}
}

func (c *Client) requireSession() error {
	if c.session == nil {
		return ErrNoSession
	}
	return nil
}

func (c *Client) applySession(req *http.Request) {
	if c.session == nil {
		return
	}

	for name, value := range c.session.Cookies {
		// Strip surrounding quotes that some cookies contain (e.g. CBI_CHK).
		// Go's net/http rejects values with '"' per RFC 6265.
		value = strings.Trim(value, `"`)
		req.AddCookie(&http.Cookie{Name: name, Value: value})
	}

	for name, value := range c.session.Headers {
		req.Header.Set(name, value)
	}
}

// rateLimit enforces a minimum interval between consecutive HTTP requests.
func (c *Client) rateLimit() {
	c.mu.Lock()
	defer c.mu.Unlock()

	now := time.Now()
	elapsed := now.Sub(c.lastCall)
	if elapsed < minRequestInterval {
		time.Sleep(minRequestInterval - elapsed)
	}
	c.lastCall = time.Now()
}

func (c *Client) getJSON(ctx context.Context, url string, target any) error {
	err := c.doGetJSON(ctx, url, target)
	if err != nil && IsAuthError(err) {
		// Try session init first (if not already done).
		if !c.sessionInitDone {
			if initErr := c.initSession(ctx); initErr == nil {
				return c.doGetJSON(ctx, url, target)
			}
		}
		// Fall back to full session refresh.
		if c.sessionRefresher != nil {
			if refreshErr := c.refreshSession(ctx); refreshErr == nil {
				return c.doGetJSON(ctx, url, target)
			}
		}
	}
	return err
}

func (c *Client) doGetJSON(ctx context.Context, url string, target any) error {
	if err := c.requireSession(); err != nil {
		return err
	}

	c.rateLimit()

	req, err := http.NewRequestWithContext(ctx, http.MethodGet, url, nil)
	if err != nil {
		return err
	}
	req.Header.Set("Accept", "application/json")
	c.applySession(req)

	resp, err := c.httpClient.Do(req)
	if err != nil {
		return err
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return err
	}

	if resp.StatusCode < 200 || resp.StatusCode >= 300 {
		return newStatusError(resp.StatusCode, string(body))
	}

	c.updateCookiesFromResponse(resp)
	c.touchSession(ctx)

	if target != nil {
		if err := json.Unmarshal(body, target); err != nil {
			return fmt.Errorf("failed to parse response: %w", err)
		}
	}

	return nil
}

func (c *Client) postJSON(ctx context.Context, url string, payload any, target any) error {
	err := c.doPostJSON(ctx, url, payload, target)
	if err != nil && IsAuthError(err) {
		// Try session init first (if not already done).
		if !c.sessionInitDone {
			if initErr := c.initSession(ctx); initErr == nil {
				return c.doPostJSON(ctx, url, payload, target)
			}
		}
		// Fall back to full session refresh.
		if c.sessionRefresher != nil {
			if refreshErr := c.refreshSession(ctx); refreshErr == nil {
				return c.doPostJSON(ctx, url, payload, target)
			}
		}
	}
	return err
}

func (c *Client) doPostJSON(ctx context.Context, url string, payload any, target any) error {
	if err := c.requireSession(); err != nil {
		return err
	}

	c.rateLimit()

	var bodyReader io.Reader
	if payload != nil {
		data, err := json.Marshal(payload)
		if err != nil {
			return fmt.Errorf("failed to encode request body: %w", err)
		}
		bodyReader = bytes.NewReader(data)
	}

	req, err := http.NewRequestWithContext(ctx, http.MethodPost, url, bodyReader)
	if err != nil {
		return err
	}
	req.Header.Set("Accept", "application/json")
	req.Header.Set("Content-Type", "application/json")
	c.applySession(req)

	resp, err := c.httpClient.Do(req)
	if err != nil {
		return err
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return err
	}

	if resp.StatusCode < 200 || resp.StatusCode >= 300 {
		return newStatusError(resp.StatusCode, string(body))
	}

	c.updateCookiesFromResponse(resp)
	c.touchSession(ctx)

	if target != nil {
		if err := json.Unmarshal(body, target); err != nil {
			return fmt.Errorf("failed to parse response: %w", err)
		}
	}

	return nil
}

// refreshSession attempts to refresh the session via the SessionRefresher.
func (c *Client) refreshSession(ctx context.Context) error {
	newSess, err := c.sessionRefresher.RefreshSession(ctx)
	if err != nil {
		return err
	}
	c.session = newSess
	return nil
}

// updateCookiesFromResponse captures any Set-Cookie headers and updates the session.
func (c *Client) updateCookiesFromResponse(resp *http.Response) {
	if c.session == nil {
		return
	}
	cookies := resp.Cookies()
	if len(cookies) == 0 {
		return
	}
	for _, cookie := range cookies {
		c.session.Cookies[cookie.Name] = cookie.Value
	}
	// Persist updated cookies in background (best-effort).
	if c.sessionStore != nil {
		_ = c.sessionStore.Save(context.Background(), c.session)
	}
}

// touchSession updates LastUsedAt and persists (best-effort).
func (c *Client) touchSession(ctx context.Context) {
	if c.session == nil {
		return
	}
	c.session.TouchLastUsed()
	if c.sessionStore != nil {
		_ = c.sessionStore.Save(ctx, c.session)
	}
}

// initSession performs the channel selection and login init flow.
// It calls /api/login/channels, selects the first channel, posts to
// /api/login/change-channel, and then calls /api/login/init.
func (c *Client) initSession(ctx context.Context) error {
	c.sessionInitDone = true

	// Step 1: GET /api/login/channels → []LoginChannel
	channelsURL := c.apiBaseURL + "/api/login/channels"
	var channels []domain.LoginChannel
	if err := c.doGetJSON(ctx, channelsURL, &channels); err != nil {
		return err
	}
	if len(channels) == 0 {
		return fmt.Errorf("no login channels available")
	}

	ch := channels[0]

	// Step 2: POST /api/login/change-channel?roleNo={roleNo}&channelNo={channelNo}&url=/
	changeURL := fmt.Sprintf(
		"%s/api/login/change-channel?roleNo=%d&channelNo=%d&url=/",
		c.apiBaseURL, ch.RoleNo, ch.ChannelNo,
	)
	if err := c.doRawPost(ctx, changeURL); err != nil {
		return err
	}

	// Step 3: GET /api/login/init?stateName=home.dashboard&needLoginInfoForAngular=false
	initURL := c.apiBaseURL + "/api/login/init?stateName=home.dashboard&needLoginInfoForAngular=false"
	if err := c.doGetJSON(ctx, initURL, nil); err != nil {
		return err
	}

	return nil
}

// doRawPost performs a POST request that may return an empty body.
// It updates cookies from the response but does not parse a JSON body.
func (c *Client) doRawPost(ctx context.Context, url string) error {
	if err := c.requireSession(); err != nil {
		return err
	}

	c.rateLimit()

	req, err := http.NewRequestWithContext(ctx, http.MethodPost, url, nil)
	if err != nil {
		return err
	}
	req.Header.Set("Accept", "application/json")
	c.applySession(req)

	resp, err := c.httpClient.Do(req)
	if err != nil {
		return err
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return err
	}

	if resp.StatusCode < 200 || resp.StatusCode >= 300 {
		return newStatusError(resp.StatusCode, string(body))
	}

	c.updateCookiesFromResponse(resp)
	c.touchSession(ctx)

	return nil
}

func (c *Client) ValidateSession(ctx context.Context) error {
	if err := c.requireSession(); err != nil {
		return err
	}

	c.rateLimit()

	url := c.apiBaseURL + "/api/v1/sellers/auths/login/check-neoid-session"

	req, err := http.NewRequestWithContext(ctx, http.MethodGet, url, nil)
	if err != nil {
		return err
	}
	req.Header.Set("Accept", "application/json")
	c.applySession(req)

	resp, err := c.httpClient.Do(req)
	if err != nil {
		return err
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return err
	}

	if resp.StatusCode == 401 || resp.StatusCode == 403 {
		return ErrSessionExpired
	}

	if resp.StatusCode < 200 || resp.StatusCode >= 300 {
		return newStatusError(resp.StatusCode, string(body))
	}

	// Check for GW.AUTHN pattern in response body even on 200
	if strings.Contains(string(body), "GW.AUTHN") {
		return ErrSessionExpired
	}

	return nil
}
