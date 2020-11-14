import sys
import pacwatch
from io import StringIO
from pathlib import Path

if __name__ == "__main__":
    if len(sys.argv) <= 1 or sys.argv[1] != '--confirm':
        print('This test resets your local settings! You need to add "--confirm" to run this test.')
        quit()
    pacwatch.settings['pacman_command'] = 'python tests/fakePacman.py'
    pacwatch.saveSettings()
    output = StringIO()
    sys.stdout = output
    sys.argv = sys.argv[:1]
    pacwatch.main()
    with (Path('tests') / 'data' / 'expected-output').open('r') as expected:
        assert output.getvalue() == expected.read()
