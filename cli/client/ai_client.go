package client

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
)

type AIClient struct {
	BaseURL string
}

func NewAIClient(baseURL string) *AIClient {
	return &AIClient{BaseURL: baseURL}
}

func (c *AIClient) Post(path string, payload interface{}) ([]byte, error) {
	body, err := json.Marshal(payload)
	if err != nil {
		return nil, fmt.Errorf("序列化请求失败: %w", err)
	}

	resp, err := http.Post(c.BaseURL+path, "application/json", bytes.NewBuffer(body))
	if err != nil {
		return nil, fmt.Errorf("请求失败: %w", err)
	}
	defer resp.Body.Close()

	data, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, fmt.Errorf("读取响应失败: %w", err)
	}

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("服务返回错误 %d: %s", resp.StatusCode, string(data))
	}

	return data, nil
}

func (c *AIClient) Get(path string) ([]byte, error) {
	resp, err := http.Get(c.BaseURL + path)
	if err != nil {
		return nil, fmt.Errorf("请求失败: %w", err)
	}
	defer resp.Body.Close()

	data, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, fmt.Errorf("读取响应失败: %w", err)
	}

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("服务返回错误 %d: %s", resp.StatusCode, string(data))
	}

	return data, nil
}

// 请求/响应结构体

type GenerateRequest struct {
	Chapter int `json:"chapter"`
	Words   int `json:"words"`
}

type GenerateResponse struct {
	Chapter     int    `json:"chapter"`
	WordsTarget int    `json:"words_target"`
	WordsActual int    `json:"words_actual"`
	Analysis    string `json:"analysis"`
	Content     string `json:"content"`
}

type PolishRequest struct {
	Chapter int    `json:"chapter"`
	Style   string `json:"style"`
}

type PolishResponse struct {
	Content string `json:"content"`
}

type AcceptRequest struct {
	Chapter int `json:"chapter"`
}

type AcceptResponse struct {
	Summary             string   `json:"summary"`
	NewForeshadowing    []string `json:"new_foreshadowing"`
	CharacterUpdates    []string `json:"character_updates"`
	UnresolvedConflicts []string `json:"unresolved_conflicts"`
	OutlineExtended     bool     `json:"outline_extended"`
}

type StatusResponse struct {
	TotalChapters int                    `json:"total_chapters"`
	HasDraft      bool                   `json:"has_draft"`
	DraftWords    int                    `json:"draft_words"`
	Preferences   map[string]interface{} `json:"preferences"`
}

type IntroResponse struct {
	Preface  string `json:"preface"`
	Prologue string `json:"prologue"`
	Synopsis string `json:"synopsis"`
}

type ExtendOutlineRequest struct {
	FromChapter int    `json:"from_chapter"`
	Count       int    `json:"count"`
	Note        string `json:"note"`
}

type ExtendOutlineResponse struct {
	Extended    bool `json:"extended"`
	FromChapter int  `json:"from_chapter"`
	Count       int  `json:"count"`
}

type RegenerateRequest struct {
	Chapter int    `json:"chapter"`
	Words   int    `json:"words"`
	Note    string `json:"note"`
}

type RegenerateResponse struct {
	Chapter     int    `json:"chapter"`
	WordsActual int    `json:"words_actual"`
	Content     string `json:"content"`
}