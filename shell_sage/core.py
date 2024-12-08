import logging
import os
import subprocess
import sys
from functools import partial
from typing import Optional
from pydantic import BaseModel

import typer
from rich.console import Console
from rich.markdown import Markdown

import aisuite as ai
from .pane import get_history
from .prompts import sp as sage_prompt, ssp as sassy_sage_prompt


class ShellSageConfig(BaseModel):
    """Configuration for ShellSage CLI"""
    code_theme: str = "monokai"
    code_lexer: str = "python"
    default_history_lines: int = 200
    log_level: str = "INFO"
    model: str = "anthropic:claude-3-5-sonnet-20241022"  # Default to Sonnet
    log_usage: bool = False

def create_messages(query: str, system_prompt: str) -> list[dict[str, str]]:
    """Create properly formatted messages for AI completion

    Args:
        query: The user's query with context
        system_prompt: The system prompt template

    Returns:
        List of message dictionaries in the format expected by the AI client

    Raises:
        ValueError: If query or system_prompt is empty
    """
    if not query or not system_prompt:
        raise ValueError("Query and system prompt cannot be empty")

    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": query}
    ]

class ShellSage:
    def __init__(self, config: ShellSageConfig):
        """Initialize ShellSage with configuration and dependencies

        Raises:
            ImportError: If required dependencies are missing
            ConnectionError: If Claude API connection fails
            ValueError: If invalid model specified
        """
        self.config = config
        self.console = Console()
        self.setup_logging()
        self.setup_client()

    def setup_logging(self) -> None:
        """Configure logging with specified level"""
        logging.basicConfig(
            level=getattr(logging, self.config.log_level),
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def setup_client(self) -> None:
        """Initialize Claude client with appropriate prompt templates

        Raises:
            ImportError: If prompt templates are not found
            ConnectionError: If Claude API connection fails
        """
        try:
            self.client = ai.Client(

            )
            try:
                self.ss = partial(self._get_completion, system=sage_prompt)
                self.sss = partial(self._get_completion, system=sassy_sage_prompt)
            except NameError as e:
                raise ImportError(f"Failed to load prompt templates: {e}")
        except Exception as e:
            raise ConnectionError(f"Failed to initialize Claude client: {e}")

    def _get_completion(self, query: str, system: str) -> str:
        """Get completion from Claude with proper message formatting"""
        messages = create_messages(query, system)
        response = self.client.chat.completions.create(
            model=self.config.model or "anthropic:claude-3-5-sonnet-20240620",
            messages=messages,
            temperature=0.7
        )
        return response.choices[0].message.content

    def get_tmux_context(self, pid: str, n: int) -> Optional[str]:
        """Get tmux context safely with proper error handling"""
        try:
            if not os.environ.get('TMUX'):
                return None
            return get_history(n, pid)
        except subprocess.CalledProcessError as e:
            self.logger.warning(f"Failed to get tmux history: {e}")
            return None

app = typer.Typer(help="ShellSage - Your CLI Teaching Assistant")

@app.command()
def main(
    query: str = typer.Argument(..., help="The query to send to ShellSage"),
    pid: str = typer.Option("current", help="Tmux pane ID ('current', 'all', or specific ID)"),
    history_lines: int = typer.Option(200, "--lines", "-n", help="Number of history lines"),
    sassy: bool = typer.Option(False, "--sassy", "-s", help="Enable sassy mode"),
    theme: str = typer.Option("monokai", help="Code theme for responses"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output"),
) -> None:
    """ShellSage CLI - Get help with shell commands and system administration"""
    try:
        config = ShellSageConfig(
            code_theme=theme,
            log_level="DEBUG" if verbose else "INFO"
        )
        sage = ShellSage(config)

        # Build context
        context_parts = []

        # Get tmux context
        if tmux_context := sage.get_tmux_context(pid, history_lines):
            context_parts.append(f"<terminal_history>\n{tmux_context}\n</terminal_history>")

        # Get stdin if available
        if not sys.stdin.isatty():
            context_parts.append(f"<context>\n{sys.stdin.read()}</context>")

        # Construct final query
        full_query = "\n".join([*context_parts, f"<query>\n{query}\n</query>"])

        # Get and render response
        response = sage.sss(full_query) if sassy else sage.ss(full_query)
        sage.console.print(Markdown(
            response,
            code_theme=config.code_theme,
            inline_code_lexer=config.code_lexer,
            inline_code_theme=config.code_theme
        ))

    except Exception as e:
        logging.error(f"Error processing request: {e}")
        raise typer.Exit(code=1)

# @app.command()
# def setup(api_key: str = typer.Option(
#     ...,
#     prompt=True,
#     hide_input=True,
#     help="Your Anthropic API key"
# )) -> None:
#     """Configure ShellSage with your API key"""
#     try:
#         save_api_key(api_key)
#         typer.echo("API key saved successfully!")
#     except Exception as e:
#         typer.echo(f"Failed to save API key: {e}", err=True)
#         raise typer.Exit(1)

if __name__ == "__main__":
    app()