package main

import (
	"bufio"
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"os"
	"os/exec"
	"strings"

	"github.com/charmbracelet/bubbles/textinput"
	"github.com/charmbracelet/bubbles/viewport"
	tea "github.com/charmbracelet/bubbletea"
	"github.com/charmbracelet/lipgloss"
)

// 🌌 THE AURA PALETTE
var (
	gold   = lipgloss.Color("#D4AF37")
	purple = lipgloss.Color("#8833FF")
	cyan   = lipgloss.Color("#00FFFF")
	green  = lipgloss.Color("#41CD52")
	red    = lipgloss.Color("#FF5555")
	gray   = lipgloss.Color("#404040")

	headerStyle = lipgloss.NewStyle().
			Foreground(gold).
			Bold(true).
			Padding(0, 1).
			Border(lipgloss.DoubleBorder(), false, false, true, false).
			BorderForeground(gray)

	userStyle   = lipgloss.NewStyle().Foreground(purple).Bold(true)
	auraStyle   = lipgloss.NewStyle().Foreground(cyan).Bold(true)
	footerStyle = lipgloss.NewStyle().Foreground(purple)

	settingsTitleStyle = lipgloss.NewStyle().Foreground(gold).Bold(true).Underline(true)
	selectedStyle      = lipgloss.NewStyle().Foreground(cyan).Bold(true)
	normalStyle        = lipgloss.NewStyle().Foreground(gray)
)

type state int

const (
	chatState state = iota
	settingsState
)

type model struct {
	state          state
	viewport       viewport.Model
	textInput      textinput.Model
	history        []message
	isGenerating   bool
	currentResp    string
	projectRoot    string
	width          int
	height         int
	models         []string
	selectedModel  int
	verbosity      float64
	cancelFunc     context.CancelFunc
	lastContext    []int // 🧠 Multi-turn raw token memory
	isAsahiHost    bool  // 💻 Hardware profile flag
}

type message struct {
	Role    string `json:"role"`
	Content string `json:"content"`
}

// ⚡ ENGINE.PY PARITY: Using /api/generate instead of /api/chat for raw context efficiency
type generateRequest struct {
	Model   string                 `json:"model"`
	System  string                 `json:"system"`
	Prompt  string                 `json:"prompt"`
	Context []int                  `json:"context,omitempty"`
	Options map[string]interface{} `json:"options"`
}

type generateResponse struct {
	Response string `json:"response"`
	Done     bool   `json:"done"`
	Context  []int  `json:"context,omitempty"`
}

type tagsResponse struct {
	Models []struct {
		Name string `json:"name"`
	} `json:"models"`
}

func isAsahi() bool {
	data, err := os.ReadFile("/proc/device-tree/model")
	if err == nil && strings.Contains(string(data), "Apple") {
		return true
	}
	return false
}

func initialModel() model {
	ti := textinput.New()
	ti.Placeholder = "DESCRIBE THE VOID..."
	ti.Prompt = "> "
	ti.PromptStyle = userStyle
	ti.Focus()

	root, _ := os.Getwd()
	vp := viewport.New(80, 20)

	return model{
		state:         chatState,
		textInput:     ti,
		projectRoot:   root,
		history:       []message{},
		viewport:      vp,
		selectedModel: 0,
		verbosity:     0.5,
		lastContext:   nil,
		isAsahiHost:   isAsahi(),
	}
}

func (m model) fetchModels() tea.Cmd {
	return func() tea.Msg {
		resp, err := http.Get("http://localhost:11434/api/tags")
		if err != nil { return nil }
		defer resp.Body.Close()
		var tr tagsResponse
		if err := json.NewDecoder(resp.Body).Decode(&tr); err != nil { return nil }
		var names []string
		for _, m := range tr.Models { names = append(names, m.Name) }
		return modelsMsg(names)
	}
}

type modelsMsg []string
type chunkMsg string
type doneMsg []int // Returns the context array

func (m model) Init() tea.Cmd {
	return tea.Batch(textinput.Blink, m.fetchModels())
}

func (m model) Update(msg tea.Msg) (tea.Model, tea.Cmd) {
	var (
		tiCmd tea.Cmd
		vpCmd tea.Cmd
	)

	switch msg := msg.(type) {
	case modelsMsg:
		m.models = msg
		return m, nil

	case tea.WindowSizeMsg:
		m.width = msg.Width
		m.height = msg.Height
		m.viewport.Width = msg.Width
		m.viewport.Height = msg.Height - 7

	case tea.KeyMsg:
		switch msg.Type {
		case tea.KeyCtrlC, tea.KeyEsc:
			if m.isGenerating {
				if m.cancelFunc != nil { m.cancelFunc() }
				m.isGenerating = false
				m.history = append(m.history, message{Role: "assistant", Content: m.currentResp + " [ABORTED]"})
				m.viewport.SetContent(m.renderHistory())
				return m, nil
			}
			return m, tea.Quit
		case tea.KeyTab:
			if m.state == chatState { m.state = settingsState } else { m.state = chatState }
			return m, nil
		case tea.KeyEnter:
			if m.state == chatState {
				input := m.textInput.Value()
				if input == "exit" { return m, tea.Quit }
				if strings.HasPrefix(input, "/") {
					return m, m.handleCommand(input)
				}
				if input == "" { return m, nil }
				m.history = append(m.history, message{Role: "user", Content: input})
				m.textInput.SetValue("")
				m.isGenerating = true
				m.currentResp = ""
				ctx, cancel := context.WithCancel(context.Background())
				m.cancelFunc = cancel
				return m, m.streamChat(ctx, input)
			}
		case tea.KeyUp:
			if m.state == settingsState && m.selectedModel > 0 { m.selectedModel-- }
		case tea.KeyDown:
			if m.state == settingsState && m.selectedModel < len(m.models)-1 { m.selectedModel++ }
		case tea.KeyLeft:
			if m.state == settingsState && m.verbosity > 0 { m.verbosity -= 0.1 }
		case tea.KeyRight:
			if m.state == settingsState && m.verbosity < 1 { m.verbosity += 0.1 }
		}

	case chunkMsg:
		m.currentResp += string(msg)
		m.viewport.SetContent(m.renderHistory())
		m.viewport.GotoBottom()

	case doneMsg:
		m.history = append(m.history, message{Role: "assistant", Content: m.currentResp})
		m.lastContext = msg // 🧠 Save the raw context array for the next turn
		m.isGenerating = false
		m.viewport.SetContent(m.renderHistory())
		m.viewport.GotoBottom()
	}

	if m.state == chatState {
		m.textInput, tiCmd = m.textInput.Update(msg)
	}
	m.viewport, vpCmd = m.viewport.Update(msg)
	return m, tea.Batch(tiCmd, vpCmd)
}

func (m model) handleCommand(input string) tea.Cmd {
	return func() tea.Msg {
		parts := strings.Fields(input)
		cmd := parts[0]
		switch cmd {
		case "/kill":
			_ = exec.Command("sudo", "systemctl", "stop", "ollama").Run()
			return chunkMsg("[SYSTEM] Ollama server killed via nuclear option.")
		case "/scan":
			return chunkMsg(fmt.Sprintf("[SYSTEM] Scanning: %s", m.projectRoot))
		case "/clear":
			// Wipe memory
			m.lastContext = nil
			return chunkMsg("[SYSTEM] Multi-turn context memory cleared.")
		default:
			return chunkMsg("[SYSTEM] Unknown command.")
		}
	}
}

func (m model) streamChat(ctx context.Context, prompt string) tea.Cmd {
	return func() tea.Msg {
		url := "http://localhost:11434/api/generate"
		modelName := "phi3:mini"
		if len(m.models) > 0 { modelName = m.models[m.selectedModel] }

		// ⚡ VERBOSITY LOGIC (From Python)
		var sysPrompt string
		if m.verbosity < 0.1 {
			sysPrompt = "SHUT UP AND COMPUTE. Raw code/answers only. No filler."
		} else if m.verbosity < 0.3 {
			sysPrompt = "Be extremely concise. Direct answers only."
		} else {
			sysPrompt = fmt.Sprintf("You are Aura, a high-performance local AI. User: Cody. CWD: %s. Output format: Balanced technical response.", m.projectRoot)
		}

		// 💻 HARDWARE PROFILING (From Python)
		options := map[string]interface{}{
			"temperature": 0.1,
			"num_ctx":     2048,
			"num_thread":  4,
			"use_mmap":    true,
			"stop":        []string{"\n\n", "User:"},
		}

		if m.isAsahiHost {
			options["num_ctx"] = 8192
			options["num_thread"] = 8
			options["num_gpu"] = 99 // Max out Metal
		}

		reqBody, _ := json.Marshal(generateRequest{
			Model:   modelName,
			System:  sysPrompt,
			Prompt:  prompt,
			Context: m.lastContext, // Multi-turn support
			Options: options,
		})

		req, _ := http.NewRequestWithContext(ctx, "POST", url, bytes.NewBuffer(reqBody))
		req.Header.Set("Content-Type", "application/json")
		
		resp, err := http.DefaultClient.Do(req)
		if err != nil { return chunkMsg("[!] Stream Error") }
		defer resp.Body.Close()

		var finalContext []int

		scanner := bufio.NewScanner(resp.Body)
		for scanner.Scan() {
			select {
			case <-ctx.Done():
				return doneMsg(m.lastContext) // Keep old context on abort
			default:
				var cr generateResponse
				if err := json.Unmarshal(scanner.Bytes(), &cr); err == nil {
					if cr.Response != "" {
						m.currentResp += cr.Response
					}
					if cr.Done {
						finalContext = cr.Context
					}
				}
			}
		}
		return doneMsg(finalContext)
	}
}

func (m model) renderHistory() string {
	var s strings.Builder
	for _, msg := range m.history {
		if msg.Role == "user" {
			s.WriteString(fmt.Sprintf("%s %s\n\n", userStyle.Render(">"), msg.Content))
		} else if msg.Role == "assistant" {
			s.WriteString(fmt.Sprintf("%s %s\n\n", auraStyle.Render("Aura //"), msg.Content))
		}
	}
	if m.isGenerating {
		s.WriteString(fmt.Sprintf("%s %s█", auraStyle.Render("Aura //"), m.currentResp))
	}
	return s.String()
}

func (m model) View() string {
	header := headerStyle.Width(m.width).Render("AURA // GOLANG_EDITION")
	
	var main string
	if m.state == chatState {
		main = m.viewport.View()
	} else {
		var s strings.Builder
		s.WriteString(settingsTitleStyle.Render("VOID_SETTINGS") + "\n\n")
		
		s.WriteString("VERBOSITY_SLIDER:\n")
		bar := strings.Repeat("█", int(m.verbosity*10)) + strings.Repeat("░", 10-int(m.verbosity*10))
		s.WriteString(fmt.Sprintf("  [%s] %.1f\n\n", selectedStyle.Render(bar), m.verbosity))

		s.WriteString("SELECT ACTIVE_MODEL:\n")
		for i, mod := range m.models {
			if i == m.selectedModel {
				s.WriteString(selectedStyle.Render(fmt.Sprintf("  > %s\n", mod)))
			} else {
				s.WriteString(normalStyle.Render(fmt.Sprintf("    %s\n", mod)))
			}
		}
		s.WriteString("\n[UP/DOWN] models | [LEFT/RIGHT] verbosity | [TAB] return")
		main = s.String()
	}
	
	input := m.textInput.View()
	modelName := "N/A"
	if len(m.models) > 0 { modelName = m.models[m.selectedModel] }
	
	hostProfile := "HP_LITE"
	if m.isAsahiHost { hostProfile = "ASAHI_POWER" }

	footer := footerStyle.Render(fmt.Sprintf("PROFILE: %s // MODEL: %s // STATUS: READY", hostProfile, modelName))

	return fmt.Sprintf("%s\n\n%s\n\n%s\n%s", header, main, input, footer)
}

func main() {
	p := tea.NewProgram(initialModel(), tea.WithAltScreen())
	if _, err := p.Run(); err != nil {
		fmt.Printf("Error: %v", err)
		os.Exit(1)
	}
}
