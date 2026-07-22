#!/usr/bin/env python3
import argparse
import json
import os
from pathlib import Path
import sys

CONFIG_FILE = Path(__file__).resolve().parent / '.openclaw_profiles.json'


def load_config() -> dict:
    if CONFIG_FILE.exists():
        try:
            return json.loads(CONFIG_FILE.read_text(encoding='utf-8'))
        except json.JSONDecodeError:
            print(f'ERROR: invalid JSON in {CONFIG_FILE}', file=sys.stderr)
            sys.exit(1)
    return {}


def save_config(data: dict) -> None:
    CONFIG_FILE.write_text(json.dumps(data, indent=2), encoding='utf-8')


def prompt_api_key() -> str:
    if not sys.stdin.isatty():
        print('ERROR: --api-key is required when stdin is not interactive.', file=sys.stderr)
        sys.exit(1)
    return input('Paste API key: ').strip()


def resolve_api_key(explicit: str | None) -> str | None:
    if explicit:
        return explicit.strip()

    env_key = os.environ.get('OPENCLAW_API_KEY', '').strip()
    if env_key:
        return env_key

    if not sys.stdin.isatty():
        stdin_data = sys.stdin.read().strip()
        if stdin_data:
            return stdin_data.splitlines()[0].strip()

    return None


def main() -> int:
    parser = argparse.ArgumentParser(prog='openclaw')
    parser.add_argument('--version', action='store_true', help='Print openclaw package version')
    parser.add_argument('--profile', default='default', help='Profile name to use')

    subparsers = parser.add_subparsers(dest='command')

    models = subparsers.add_parser('models', help='Model-related subcommands')
    models_subparsers = models.add_subparsers(dest='models_command')

    auth = models_subparsers.add_parser('auth', help='Authentication operations')
    auth_subparsers = auth.add_subparsers(dest='auth_command')

    paste_api_key = auth_subparsers.add_parser('paste-api-key', help='Store provider API key for a profile')
    paste_api_key.add_argument('--provider', required=True, help='Provider name such as anthropic')
    paste_api_key.add_argument('--profile-id', required=True, help='Profile id for the provider')
    paste_api_key.add_argument('--api-key', help='Paste the API key directly')

    args = parser.parse_args()

    if args.version:
        try:
            import importlib
            m = importlib.import_module('openclaw')
            print(getattr(m, '__version__', '(no __version__)'))
            return 0
        except Exception as exc:
            print('ERROR: failed to import openclaw:', exc, file=sys.stderr)
            return 1

    if args.command == 'models' and args.models_command == 'auth' and args.auth_command == 'paste-api-key':
        api_key = resolve_api_key(args.api_key)
        if api_key is None:
            api_key = prompt_api_key()
        api_key = api_key.strip()
        if not api_key:
            print('ERROR: API key cannot be empty.', file=sys.stderr)
            return 1

        config = load_config()
        profile_data = config.get(args.profile, {})
        profile_data['provider'] = args.provider
        profile_data['profile_id'] = args.profile_id
        profile_data['api_key'] = api_key
        config[args.profile] = profile_data
        save_config(config)

        print(f"Saved API key for profile '{args.profile}' to {CONFIG_FILE}")
        print(f"provider={args.provider}, profile_id={args.profile_id}")
        return 0

    parser.print_help()
    return 1


if __name__ == '__main__':
    raise SystemExit(main())
