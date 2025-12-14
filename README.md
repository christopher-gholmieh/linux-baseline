# Linux Baseline

Tooling to record a Linux system's state and compare it against a saved baseline. The project snapshots packages, service enablement, key configuration trees, and hashes of critical files so you can detect differences between hosts. 

## What it captures
- Packages installed via `dpkg-query`
- Systemd service states (`enabled`, `disabled`, `masked`)
- File metadata (mode, owner, group) for everything under `/etc`
- SHA-256 fingerprints for critical files such as `/etc/passwd`, `/etc/shadow`, `/etc/group`, `/etc/sudoers`, `/etc/ssh/sshd_config`, and `/etc/login.defs`

Each run produces a JSON file under `database/` with:
- `metadata`: hostname and UTC timestamp
- `packages`: list of package names
- `services`: lists of services keyed by state
- `trees`: metadata records per file in `/etc`
- `fingerprints`: path plus SHA-256 hash for critical files

## Requirements
- Python 3.10+
- Debian/Ubuntu (relies on `dpkg-query` and `systemctl`)
- System utilities: `dpkg-query`, `systemctl`, `sha256sum` (via Python's `hashlib`), plus read access to `/etc` and the listed fingerprint files (root recommended for full coverage)
- Python dependencies: `loguru` and `prompt_toolkit`

Install the Python dependencies on Debian/Ubuntu:
```bash
sudo apt update && sudo ./install-dependencies.sh
```

## Usage
Run commands from the repository root.

### Record a system snapshot
```bash
sudo python3 main.py record
```
- You will be prompted for a filename; the recorder writes to `database/<name>.json` (adds `.json` if omitted).
- Ensure you have sufficient permissions to read `/etc/shadow` and other protected files.

### Compare two snapshots
```bash
sudo python3 main.py compare
```
- An interactive list lets you pick the baseline file and the current recording from `database/`.
- Differences are emitted via `loguru`:
  - `[PACKAGE +]` added packages
  - `[PACKAGE -]` removed packages
  - `[SERVICE]` changes to service enablement state
  - `[FILE +]` or `[FILE -]` file additions/removals under `/etc`
  - `[FILE !]` metadata changes (mode/owner/group)
  - `[HASH]` or `[HASH -]` fingerprint changes or missing critical files

## Notes and limitations
- Recording is tailored to systemd-based Debian/Ubuntu systems; other distros/package managers are not supported.
- Running as root is recommended; without it, some files (e.g., `/etc/shadow`) cannot be read and will be skipped.
- The tree scan currently targets `/etc`; adjust in `Recorder.query_trees` and `Recorder.query_fingerprints` if you need broader coverage.

## Workflow:
1. On a clean system: `sudo python main.py record` → `database/baseline.json`
2. After changes: `sudo python main.py record` → `database/after-maintenance.json`
3. Compare: `sudo python main.py compare` and select `baseline.json` vs `after-maintenance.json` to review differences.
