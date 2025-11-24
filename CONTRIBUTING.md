# Contributing to 24/7 YouTube Music Live Bot

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on what is best for the community
- Show empathy towards other community members

## How to Contribute

### Reporting Bugs

If you find a bug, please create an issue with:

1. **Clear title** describing the bug
2. **Steps to reproduce** the issue
3. **Expected behavior**
4. **Actual behavior**
5. **Environment details** (OS, Python version, platform)
6. **Error messages** or logs if available

### Suggesting Features

We welcome feature suggestions! Please create an issue with:

1. **Clear description** of the feature
2. **Use case** - why is this feature needed?
3. **Proposed implementation** (if you have ideas)
4. **Examples** of similar features in other projects

### Pull Requests

1. **Fork the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/24-7YouTubeMusicLiveBot.git
   cd 24-7YouTubeMusicLiveBot
   ```

2. **Create a branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**
   - Write clean, readable code
   - Follow existing code style
   - Add comments for complex logic
   - Update documentation if needed

4. **Test your changes**
   - Test locally
   - Ensure bot works as expected
   - Verify no existing functionality is broken

5. **Commit your changes**
   ```bash
   git add .
   git commit -m "Add: brief description of your changes"
   ```

   Use these commit prefixes:
   - `Add:` for new features
   - `Fix:` for bug fixes
   - `Update:` for updates to existing features
   - `Docs:` for documentation changes
   - `Refactor:` for code refactoring

6. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Create Pull Request**
   - Go to the original repository
   - Click "New Pull Request"
   - Select your branch
   - Provide clear description of changes
   - Link related issues

## Development Setup

### Prerequisites
- Python 3.9 or higher
- FFmpeg installed
- Git

### Local Setup

1. **Clone your fork**
   ```bash
   git clone https://github.com/YOUR_USERNAME/24-7YouTubeMusicLiveBot.git
   cd 24-7YouTubeMusicLiveBot
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Setup environment**
   ```bash
   cp .env.example .env
   # Edit .env with your tokens
   ```

5. **Run the bot**
   ```bash
   python bot.py
   ```

## Code Style

- Follow PEP 8 guidelines
- Use meaningful variable names
- Add docstrings to functions and classes
- Keep functions focused and small
- Use type hints where appropriate

Example:
```python
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle /start command
    
    Args:
        update: Telegram update object
        context: Bot context
    """
    await update.message.reply_text("Welcome!")
```

## Project Structure

```
24-7YouTubeMusicLiveBot/
├── bot.py              # Main bot application
├── stream_manager.py   # Stream management logic
├── file_handler.py     # File download/upload handling
├── requirements.txt    # Python dependencies
├── .env.example        # Environment variables template
├── Dockerfile          # Docker configuration
├── docker-compose.yml  # Docker Compose configuration
├── Procfile            # Heroku/Render configuration
├── runtime.txt         # Python runtime version
├── app.json            # Heroku app configuration
├── railway.json        # Railway configuration
└── README.md          # Main documentation
```

## Adding New Features

### Adding a New Command

1. Add command handler in `bot.py`:
   ```python
   async def your_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
       """Handle /your_command"""
       await update.message.reply_text("Your response")
   ```

2. Register handler in `main()`:
   ```python
   application.add_handler(CommandHandler("your_command", your_command))
   ```

3. Update help text in `/help` and `/start` commands
4. Update README with new command

### Adding Stream Features

- Modify `stream_manager.py`
- Ensure backward compatibility
- Update FFmpeg commands carefully
- Test with different file types

### Adding File Handlers

- Modify `file_handler.py`
- Support new file formats
- Handle errors gracefully
- Update documentation

## Testing

### Manual Testing Checklist

- [ ] Bot responds to `/start`
- [ ] Help command shows correct info
- [ ] File upload works (Telegram)
- [ ] Google Drive link works
- [ ] Stream starts successfully
- [ ] Stream stops gracefully
- [ ] Status command shows correct info
- [ ] List command displays files
- [ ] Admin restrictions work
- [ ] Multi-group support works

### Testing on Platforms

Test deployments on:
- [ ] Render
- [ ] Railway
- [ ] Koyeb
- [ ] Docker

## Documentation

- Update README.md for user-facing changes
- Update DEPLOYMENT.md for deployment changes
- Add inline comments for complex code
- Update docstrings

## Review Process

1. **Automated Checks**: PRs must pass any CI checks
2. **Code Review**: Maintainers review code quality
3. **Testing**: Changes must be tested
4. **Documentation**: Docs must be updated
5. **Approval**: At least one maintainer approval required

## Questions?

- Open an issue for questions
- Check existing issues and PRs
- Read the README and DEPLOYMENT guides

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing! 🎉
