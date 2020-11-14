import sys
import argparse
import pacwatch
from io import StringIO
from pathlib import Path

expected_output = Path('tests') / 'data' / 'expected-output'

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--update', action='store_true',
                        help='update expected output')
    parserResult = parser.parse_args()

    pacwatch.settings['pacman_command'] = 'python tests/fakePacman.py'

    if parserResult.update:
        with expected_output.open('w') as f:
            sys.stdout = f
            pacwatch.main()
    else:
        output = StringIO()
        sys.stdout = output
        pacwatch.main()
        with expected_output.open('r') as expected:
            assert output.getvalue() == expected.read()
