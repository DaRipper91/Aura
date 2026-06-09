import argparse

def test():
    parser = argparse.ArgumentParser()
    parser.add_argument("prompt", nargs="*")
    args, _ = parser.parse_known_args(["test", "prompt"])
    print(" ".join(args.prompt))

test()
