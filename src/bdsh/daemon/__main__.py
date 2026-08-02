import argparse
import sys

from bdsh import SHELL_COPYRIGHT
from bdsh.daemon import get_daemon


def main():
    print("BadProc Daemon Manager, " + SHELL_COPYRIGHT)

    parser = argparse.ArgumentParser(description="BadOS daemon launcher", color=False)
    parser.add_argument('daemon', type=str, help='name of daemon to launch')

    args = parser.parse_args(sys.argv[1:])
    daemon = get_daemon(args.daemon)
    try:
        print(f"Attempting to start {args.daemon}... SIGINT to stop")
        daemon.start()
    except ValueError as e:
        print(e)
        exit()
    except KeyboardInterrupt:
        daemon.stop()


if __name__ == '__main__':
    main()
