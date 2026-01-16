# Setting Up Your OpenAI API Key

The `file-agent` tool requires an OpenAI API key to function. Here are several ways to set it up:

## Option 1: Create .env File in Home Directory (Recommended for Global Use)

Since you're using `file-agent` from any directory, create a `.env` file in your home directory:

```bash
# Create .env file in your home directory
echo "OPENAI_API_KEY=your_actual_api_key_here" > ~/.env
```

Replace `your_actual_api_key_here` with your actual OpenAI API key.

**Note:** The config will automatically find this file when you run `file-agent` from any directory.

## Option 2: Set Environment Variable in Shell Profile

Add the API key to your shell configuration file:

```bash
# For bash
echo 'export OPENAI_API_KEY="your_actual_api_key_here"' >> ~/.bashrc
source ~/.bashrc

# For zsh
echo 'export OPENAI_API_KEY="your_actual_api_key_here"' >> ~/.zshrc
source ~/.zshrc
```

## Option 3: Create .env in Project Directory

If you only use `file-agent` from the project directory:

```bash
cd "/home/robinson-working/Langgraph replicate with AI"
cp .env.example .env
# Then edit .env and add your API key
nano .env  # or use your preferred editor
```

## Option 4: Set for Current Session Only

For temporary use in the current terminal session:

```bash
export OPENAI_API_KEY="your_actual_api_key_here"
```

## Getting Your OpenAI API Key

1. Visit [OpenAI's website](https://platform.openai.com/)
2. Sign up or log in to your account
3. Navigate to [API Keys](https://platform.openai.com/api-keys)
4. Click "Create new secret key"
5. Copy the key (you won't be able to see it again!)
6. Use it in one of the methods above

## Verification

After setting up your API key, test it:

```bash
file-agent --version
file-agent chat "hello"
```

If you see an error about the API key, double-check:
- The key is correct (no extra spaces)
- The .env file is in the right location
- You've reloaded your shell (if using environment variables)

## Security Notes

- **Never commit your .env file to git** - it should be in `.gitignore`
- **Never share your API key** - treat it like a password
- The `.env` file in your home directory is a good choice for global tools
