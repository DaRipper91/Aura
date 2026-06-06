use reqwest::Client;
use serde::{Deserialize, Serialize};
use futures::StreamExt;
use std::io::{self, stdout, Write};
use std::process::Command;
use std::fs;
use anyhow::Result;

use ratatui::{
    backend::CrosstermBackend,
    layout::{Constraint, Direction, Layout},
    style::{Color, Modifier, Style},
    widgets::{Block, Borders, Paragraph, Wrap},
    Terminal,
};
use crossterm::{
    event::{self, Event, KeyCode},
    execute,
    terminal::{disable_raw_mode, enable_raw_mode, EnterAlternateScreen, LeaveAlternateScreen},
};

#[derive(Serialize)]
struct ChatRequest {
    model: String,
    messages: Vec<Message>,
    options: serde_json::Value,
}

#[derive(Serialize, Deserialize, Clone)]
struct Message {
    role: String,
    content: String,
}

#[derive(Deserialize)]
struct ChatResponse {
    message: Message,
    done: bool,
}

pub struct AuraEngine {
    client: Client,
    base_url: String,
    history: Vec<Message>,
    project_root: String,
    file_map: String,
    memory: String,
    current_response: String,
    is_generating: bool,
}

impl AuraEngine {
    pub fn new(base_url: &str) -> Self {
        let current_dir = std::env::current_dir()
            .map(|p| p.to_string_lossy().into_owned())
            .unwrap_or_else(|_| "/home/daripper/Projects/Aura".to_string());

        let memory = fs::read_to_string("memory/MEMORY.md").unwrap_or_default();

        let mut engine = Self {
            client: Client::new(),
            base_url: base_url.to_string(),
            history: Vec::new(),
            project_root: current_dir,
            file_map: String::new(),
            memory,
            current_response: String::new(),
            is_generating: false,
        };
        engine.scan_workspace(".");
        engine
    }

    fn scan_workspace(&mut self, sub_dir: &str) {
        let target_path = if sub_dir == "." {
            self.project_root.clone()
        } else {
            format!("{}/{}", self.project_root, sub_dir)
        };

        let mut map = format!("MAP [{}]:\n", sub_dir);
        if let Ok(entries) = fs::read_dir(&target_path) {
            for entry in entries.flatten() {
                let p = entry.path();
                let name = p.file_name().unwrap_or_default().to_string_lossy();
                if name.starts_with('.') || name == "target" || name == "python" { continue; } 
                if p.is_dir() { map.push_str(&format!("  [D] {}\n", name)); }
                else { map.push_str(&format!("  [F] {}\n", name)); }
            }
        }
        self.file_map = map;
    }

    fn get_system_prompt(&self) -> String {
        format!(
            "You are Phi, voice of Aura-RE. System agent for Cody & Deanna.\n\
             CWD: {}\n\
             {}\n\
             MEMORY:\n{}\n\n\
             ACTIONS:\n[COMMAND] <cmd>\n[WRITE] <path> CONTENT: <text> [EOF]\n[SCAN] <path>\n\n\
             RULES: NO CHATTER. NO INTROS. NO FILLER. STOP after tags.",
            self.project_root, self.file_map, self.memory
        )
    }

    pub async fn stream_chat(&mut self, model: &str, prompt: &str) -> Result<()> {
        if self.history.is_empty() {
            self.history.push(Message { role: "system".to_string(), content: self.get_system_prompt() });
        }
        self.history.push(Message { role: "user".to_string(), content: prompt.to_string() });
        
        self.is_generating = true;
        self.current_response.clear();

        let url = format!("{}/api/chat", self.base_url);
        let request = ChatRequest {
            model: model.to_string(),
            messages: self.history.clone(),
            options: serde_json::json!({ "temperature": 0.1, "stop": ["[EOF]", "\n\n", "User:"], "num_predict": 1024 }),
        };

        let res = self.client.post(&url).json(&request).send().await?;
        let mut stream = res.bytes_stream();

        while let Some(item) = stream.next().await {
            let chunk = item?;
            let chunk_str = String::from_utf8_lossy(&chunk);
            for part in chunk_str.split('\n') {
                if part.is_empty() { continue; }
                if let Ok(response) = serde_json::from_str::<ChatResponse>(part) {
                    self.current_response.push_str(&response.message.content);
                    if response.done { break; }
                }
            }
        }

        self.is_generating = false;
        self.history.push(Message { role: "assistant".to_string(), content: self.current_response.clone() });
        Ok(())
    }
}

#[tokio::main]
async fn main() -> Result<()> {
    enable_raw_mode()?;
    let mut stdout = stdout();
    execute!(stdout, EnterAlternateScreen)?;
    let backend = CrosstermBackend::new(stdout);
    let mut terminal = Terminal::new(backend)?;

    let mut engine = AuraEngine::new("http://localhost:11434");
    let mut input = String::new();
    let mut logs = Vec::new();
    logs.push("Aura-RE // Warp Drive Online".to_string());

    loop {
        terminal.draw(|f| {
            let chunks = Layout::default()
                .direction(Direction::Horizontal)
                .constraints([Constraint::Percentage(25), Constraint::Percentage(75)].as_ref())
                .split(f.size());

            // Sidebar
            let sidebar = Layout::default()
                .direction(Direction::Vertical)
                .constraints([Constraint::Percentage(50), Constraint::Percentage(50)].as_ref())
                .split(chunks[0]);

            let map_block = Block::default().title(" SYSTEM_MAP ").borders(Borders::ALL).border_style(Style::default().fg(Color::Rgb(102, 51, 255)));
            let map_text = Paragraph::new(engine.file_map.as_str()).block(map_block);
            f.render_widget(map_text, sidebar[0]);

            let mem_block = Block::default().title(" PERSONAL_MEMORY ").borders(Borders::ALL).border_style(Style::default().fg(Color::Rgb(212, 175, 55)));
            let mem_text = Paragraph::new(engine.memory.as_str()).block(mem_block).wrap(Wrap { trim: true });
            f.render_widget(mem_text, sidebar[1]);

            // Main Chat
            let main_chunks = Layout::default()
                .direction(Direction::Vertical)
                .constraints([Constraint::Min(3), Constraint::Length(3)].as_ref())
                .split(chunks[1]);

            let mut chat_content = String::new();
            for msg in &engine.history {
                if msg.role == "user" { chat_content.push_str(&format!("> {}\n\n", msg.content)); }
                else if msg.role == "assistant" { chat_content.push_str(&format!("Aura // {}\n\n", msg.content)); }
            }
            if engine.is_generating {
                chat_content.push_str(&format!("Aura // {}█", engine.current_response));
            }

            let chat_block = Block::default().title(" AURA_RE_STREAM ").borders(Borders::ALL).border_style(Style::default().fg(Color::Cyan));
            let chat_text = Paragraph::new(chat_content).block(chat_block).wrap(Wrap { trim: true });
            f.render_widget(chat_text, main_chunks[0]);

            let input_block = Block::default().title(" COMMAND_VOID ").borders(Borders::ALL).border_style(Style::default().fg(Color::Green));
            let input_text = Paragraph::new(input.as_str()).block(input_block);
            f.render_widget(input_text, main_chunks[1]);
        })?;

        if event::poll(std::time::Duration::from_millis(50))? {
            if let Event::Key(key) = event::read()? {
                match key.code {
                    KeyCode::Enter => {
                        if input == "exit" { break; }
                        let prompt = input.clone();
                        input.clear();
                        engine.stream_chat("phi3:mini", &prompt).await?;
                    }
                    KeyCode::Char(c) => {
                        input.push(c);
                    }
                    KeyCode::Backspace => {
                        input.pop();
                    }
                    KeyCode::Esc => break,
                    _ => {}
                }
            }
        }
    }

    disable_raw_mode()?;
    execute!(terminal.backend_mut(), LeaveAlternateScreen)?;
    Ok(())
}
