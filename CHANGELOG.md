# Release notes

<!-- do not remove -->

## 0.0.1

Initial release of the Shell-Sage Adaptation from AnswerDotAI.
- Support for multiple AI providers by using the `aisuite` library:
  - Anthropic Claude 3 models (Sonnet, Haiku, Opus)
  - OpenAI GPT-4 models
- Refactored the code to be more readable and maintainable

Core dependencies:
  - aisuite ≥0.1.6
  - anthropic ≥0.40.0
  - openai ≥1.57.0
  - rich ≥13.9.4
  - typer ≥0.15.1