from pathlib import Path

from workflowpy.compiler import Compiler
from workflowpy.utils import sign_shortcut

path = Path(__file__).parent

with open(path / 'main.py') as f:
    code = f.read()

shortcut = Compiler().compile(code)
signed_shortcut = sign_shortcut(shortcut)

with open(path / 'PassBuilder.shortcut', 'wb') as f:
    f.write(signed_shortcut)
