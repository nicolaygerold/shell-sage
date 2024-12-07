from typing import Dict, List, Tuple

# Model definitions and pricing
MODEL_TYPES: Dict[str, str] = {
    'claude-3-opus-20240229': 'opus',
    'claude-3-5-sonnet-20241022': 'sonnet',
    'claude-3-haiku-20240307': 'haiku-3',
    'claude-3-5-haiku-20241022': 'haiku-3-5',
}

PRICING: Dict[str, Tuple[float, float, float, float]] = {
    'opus': (15, 75, 18.75, 1.5),
    'sonnet': (3, 15, 3.75, 0.3),
    'haiku-3': (0.25, 1.25, 0.3, 0.03),
    'haiku-3-5': (1, 3, 1.25, 0.1),
}

TEXT_ONLY_MODELS: List[str] = ['claude-3-5-haiku-20241022']