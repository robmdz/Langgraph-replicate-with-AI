# Making file-agent Globally Accessible

## Quick Installation (Run these commands in your terminal)

### Option 1: Create a Symlink (Easiest)

```bash
# Create the directory if it doesn't exist
mkdir -p ~/.local/bin

# Create a symlink to the file-agent command
ln -sf ~/.cache/pypoetry/virtualenvs/file-agent-JSJ-BFdj-py3.13/bin/file-agent ~/.local/bin/file-agent

# Make sure it's executable
chmod +x ~/.local/bin/file-agent

# Verify it works
file-agent --version
```

If `~/.local/bin` is not in your PATH, add this to your `~/.bashrc` or `~/.zshrc`:
```bash
export PATH="$HOME/.local/bin:$PATH"
```

Then reload your shell:
```bash
source ~/.bashrc  # or source ~/.zshrc
```

### Option 2: Install with pipx (Recommended for production)

```bash
# Install pipx
sudo apt install pipx
pipx ensurepath

# Install file-agent globally
cd "/home/robinson-working/Langgraph replicate with AI"
pipx install .

# Verify it works
file-agent --version
```

### Option 3: Use Poetry Run (No installation needed)

You can always use:
```bash
cd "/home/robinson-working/Langgraph replicate with AI"
poetry run file-agent create "your prompt"
```

Or create an alias in your `~/.bashrc` or `~/.zshrc`:
```bash
alias file-agent='cd "/home/robinson-working/Langgraph replicate with AI" && poetry run file-agent'
```

Then reload: `source ~/.bashrc`

## Troubleshooting

### Command not found after symlink
- Make sure `~/.local/bin` is in your PATH: `echo $PATH | grep local`
- If not, add it to your shell config file and reload

### Permission denied
- Make sure you have write access to `~/.local/bin`
- Try: `chmod 755 ~/.local/bin`

### Poetry virtualenv path changed
If Poetry recreates the virtualenv, the path will change. Use this command to find the current path:
```bash
poetry env info --path
```

Then update the symlink:
```bash
ln -sf $(poetry env info --path)/bin/file-agent ~/.local/bin/file-agent
```
