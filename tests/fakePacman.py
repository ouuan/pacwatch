import sys
from pathlib import Path

if __name__ == "__main__":
    args = []
    for arg in sys.argv[1:]:
        if arg == '--noconfirm' or arg == '--color=always':
            continue
        args.append(arg)
    with open(Path('tests') / 'data' / ' '.join(args)) as output:
        sys.stdout.write(output.read())
