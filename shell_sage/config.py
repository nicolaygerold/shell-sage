import os
from pathlib import Path
import json
from typing import Optional

def get_config_dir() -> Path:
    """Get the configuration directory with proper permissions"""
    # Use XDG_CONFIG_HOME if available, otherwise fallback to ~/.config
    xdg_config = os.environ.get('XDG_CONFIG_HOME', os.path.expanduser('~/.config'))
    config_dir = Path(xdg_config) / 'shell_sage'

    # Create directory if it doesn't exist
    config_dir.mkdir(parents=True, exist_ok=True)
    # Secure the directory permissions (700 - only owner can read/write/execute)
    config_dir.chmod(0o700)
    return config_dir

def get_config_file() -> Path:
    """Get the path to the credentials file"""
    return get_config_dir() / 'credentials.json'

def load_api_key() -> Optional[str]:
    """Load API key from config file

    Returns:
        Optional[str]: The API key if found, None otherwise
    """
    config_file = get_config_file()
    try:
        if config_file.exists():
            with open(config_file) as f:
                config = json.load(f)
                return config.get('anthropic_api_key')
    except (json.JSONDecodeError, OSError) as e:
        # Log error but don't expose details to caller
        return None
    return None

def save_api_key(api_key: str) -> None:
    """Save API key to config file

    Args:
        api_key: The API key to save

    Raises:
        OSError: If unable to write config file
        ValueError: If api_key is empty or invalid
    """
    if not api_key or not api_key.strip():
        raise ValueError("API key cannot be empty")

    config_file = get_config_file()
    config = {}

    # Load existing config if present
    if config_file.exists():
        try:
            with open(config_file) as f:
                config = json.load(f)
        except json.JSONDecodeError:
            # If file is corrupted, start fresh
            pass

    # Update config
    config['anthropic_api_key'] = api_key.strip()

    # Write config with secure permissions
    with open(config_file, 'w') as f:
        json.dump(config, f)
    config_file.chmod(0o600)  # Read/write for owner only