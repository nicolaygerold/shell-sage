import subprocess
from subprocess import check_output as co
from typing import Optional, List

def get_pane_output(num_lines: int, pane_id: Optional[str] = None) -> str:
    """Get output from a tmux pane

    Args:
        num_lines: Number of lines of history to capture
        pane_id: Optional tmux pane ID to capture from. If None, uses current pane.

    Returns:
        Captured pane output as string

    Raises:
        subprocess.CalledProcessError: If tmux command fails
    """
    cmd = ['tmux', 'capture-pane', '-p', '-S', f'-{num_lines}']
    if pane_id:
        cmd += ['-t', pane_id]
    return co(cmd, text=True)

def get_pane_outputs(num_lines: int) -> str:
    """Get output from all tmux panes with XML-style formatting

    Args:
        num_lines: Number of lines of history to capture per pane

    Returns:
        String containing all pane outputs with XML tags

    Raises:
        subprocess.CalledProcessError: If tmux commands fail
    """
    current_id = co(['tmux', 'display-message', '-p', '#{pane_id}'], text=True).strip()
    pane_ids: List[str] = co(['tmux', 'list-panes', '-F', '#{pane_id}'], text=True).splitlines()

    outputs = []
    for pid in pane_ids:
        is_active = 'active' if pid == current_id else ''
        pane_output = get_pane_output(num_lines, pid)
        outputs.append(f"<pane id={pid} {is_active}>{pane_output}</pane>")

    return '\n'.join(outputs)

def get_history(num_lines: int, pane_id: str = 'current') -> Optional[str]:
    """Get history from tmux pane(s)

    Args:
        num_lines: Number of lines of history to capture
        pane_id: Which pane(s) to capture from:
                'current' - current pane only
                'all' - all panes
                <pane_id> - specific pane ID

    Returns:
        Captured history as string, or None if capture fails
    """
    try:
        if pane_id == 'current':
            return get_pane_output(num_lines)
        if pane_id == 'all':
            return get_pane_outputs(num_lines)
        return get_pane_output(num_lines, pane_id)
    except subprocess.CalledProcessError:
        return None
