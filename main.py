# main.py
import sys
import time
import subprocess
import requests
import argparse
from chat import send_message  # your helper from chat.py

API_BASE = "http://localhost:11434"

def ensure_server(start_if_missing: bool = False):
    """Ping the Ollama server; optionally start it if it’s not running."""
    health_url = f"{API_BASE}/api/tags"
    try:
        requests.get(health_url, timeout=1).raise_for_status()
        # server is up
    except Exception:
        if not start_if_missing:
            print("Error: Ollama server isn’t running.  Start it with `ollama serve` and try again.")
            sys.exit(1)
        # spawn it in a detached window (Windows example)
        subprocess.Popen(
            ["ollama", "serve"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
        # wait for it to come up
        for _ in range(20):
            try:
                requests.get(health_url, timeout=1).raise_for_status()
                return
            except Exception:
                time.sleep(0.5)
        print("Timed out waiting for Ollama to start.")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Deepseek chat CLI")
    parser.add_argument("--flux", action="store_true",
                        help="Use the Flux prompt engineer persona")
    parser.add_argument("--wtboy", action="store_true",
                        help="Use the WT BOY Flux prompt engineer persona")
    parser.add_argument("rest", nargs=argparse.REMAINDER,
                        help="If --flux: <name> <prompt...>. Else: <convo> <prompt...>")
    args = parser.parse_args()

    if args.flux:
        if len(args.rest) < 2:
            sys.exit("Usage: python main.py --flux <flux_name> <your prompt>")
        conv_name = f"flux-{args.rest[0]}"
        prompt    = " ".join(args.rest[1:])
    elif args.wtboy:
        if len(args.rest) < 2:
            sys.exit("Usage: python main.py --wtboy <flux_name> <your prompt>")
        conv_name = f"wtboy-{args.rest[0]}"
        prompt    = " ".join(args.rest[1:])
    else:
        if len(args.rest) < 2:
            sys.exit("Usage: python main.py <convo_name> <your prompt>")
        conv_name = args.rest[0]
        prompt    = " ".join(args.rest[1:])

    reply = send_message(conv_name, prompt)

if __name__ == "__main__":
    main()