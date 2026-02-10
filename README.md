# Social Content CLI

AI-powered social media content creation tool using the Claude API. Generate platform-specific content for Twitter/X, Instagram, and LinkedIn, and manage it with a local content calendar.

## Installation

```bash
pip install -e ".[dev]"
```

## Setup

Set your Anthropic API key:

```bash
export ANTHROPIC_API_KEY=sk-ant-...
```

## Usage

### Generate content

```bash
# Interactive mode (prompts for platform and topic)
social generate

# With flags
social generate -p twitter -t "Python async programming tips"

# Generate and schedule
social generate -p linkedin -t "AI trends in 2026" -s 2026-02-14
```

### View the content calendar

```bash
# List all entries
social calendar

# Filter by platform or status
social calendar -p twitter
social calendar --status draft

# Week view
social calendar --week
```

### Manually add content

```bash
social calendar add -p instagram -c "Your caption here" -t "Photography"
```

### Edit and delete

```bash
# Update fields
social edit <id> --status scheduled --schedule 2026-02-15

# Regenerate content with AI
social edit <id> --regenerate

# Delete
social delete <id>
social delete <id> --force
```

### View supported platforms

```bash
social platforms
```

## Supported Platforms

| Platform    | Max Length | Tone                    | Hashtags |
|-------------|-----------|-------------------------|----------|
| Twitter / X | 280       | Concise, witty          | Inline   |
| Instagram   | 2200      | Casual, storytelling    | Footer   |
| LinkedIn    | 3000      | Professional, insightful| Footer   |

## Development

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest -v
```
