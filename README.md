# cronscope

> Visualize and validate cron expressions with next-run previews in the terminal.

---

## Installation

```bash
pip install cronscope
```

Or install from source:

```bash
git clone https://github.com/youruser/cronscope.git && cd cronscope && pip install .
```

---

## Usage

```bash
cronscope "*/15 * * * *"
```

**Example output:**

```
Expression : */15 * * * *
Description: Every 15 minutes

Next 5 runs:
  1 → 2024-06-10 14:15:00
  2 → 2024-06-10 14:30:00
  3 → 2024-06-10 14:45:00
  4 → 2024-06-10 15:00:00
  5 → 2024-06-10 15:15:00
```

Show more upcoming runs with the `--count` flag:

```bash
cronscope "0 9 * * 1-5" --count 10
```

Validate an expression without previewing runs:

```bash
cronscope "0 25 * * *" --validate
# Error: Hour field value 25 is out of range (0-23)
```

---

## Options

| Flag | Description |
|------|-------------|
| `--count N` | Number of next runs to display (default: 5) |
| `--validate` | Validate expression and exit without listing runs |
| `--utc` | Display times in UTC instead of local time |

---

## License

[MIT](LICENSE)