import sys
import pacwatch
from io import StringIO
from pathlib import Path

if __name__ == "__main__":
    pacwatch.settings['pacman_command'] = 'python tests/fakePacman.py'
    output = StringIO()
    sys.stdout = output
    pacwatch.main()
    with (Path('tests') / 'data' / 'expected-output').open('r') as expected:
        assert output.getvalue() == expected.read()
