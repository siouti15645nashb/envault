# envault

> A CLI tool for managing and encrypting project-level environment variables with team-sharing support.

---

## Installation

```bash
pip install envault
```

Or with [pipx](https://pypa.github.io/pipx/) for isolated installs:

```bash
pipx install envault
```

---

## Usage

Initialize envault in your project directory:

```bash
envault init
```

Add and encrypt environment variables:

```bash
envault set DATABASE_URL "postgres://user:pass@localhost/db"
envault set API_KEY "your-secret-key"
```

Load variables into your shell session:

```bash
eval $(envault load)
```

Remove a stored variable:

```bash
envault unset DATABASE_URL
```

Export an encrypted vault file to share with your team:

```bash
envault export --output .envault
```

Import a shared vault using a shared decryption key:

```bash
envault import .envault --key <shared-key>
```

List all stored variable names (values stay hidden):

```bash
envault list
```

---

## License

This project is licensed under the [MIT License](LICENSE).
