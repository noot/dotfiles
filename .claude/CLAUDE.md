# Instructions for Claude (listen carefully)

## Metaprompting

If I give you a bad prompt, suggest an improved version of the prompt and ask me to confirm.

You can improve the prompt by making it more specific. If the solution is complex, encourage thinking and creating a step-by-step plan.

When you are suggesting an improved prompt, explicitly say "PROMPT SUGGESTION".

Examples:

Poor	Good
add tests for foo.py	write a new test case for foo.py, covering the edge case where the user is logged out. avoid mocks
why does ExecutionFactory have such a weird api?	look through ExecutionFactory's git history and summarize how its api came to be
add a calendar widget	look at how existing widgets are implemented on the home page to understand the patterns and specifically how code and interfaces are separated out. HotDogWidget.php is a good example to start with. then, follow the pattern to implement a new calendar widget that lets the user select a month and paginate forwards/backwards to pick a year. Build from scratch without libraries other than the ones already used in the rest of the codebase.

## Git branches

Before making any changes, create a new branch with a branch name that describes what you will be doing.

For example: `claude-fix-clippy`, `claude-issue-88`, `claude-feat-description`

## General 

1. Do not write comments unless the code is unusually complex, or is required by clippy.
2. Do not write unused code. Only implement code that will actually be called.
3. Do not change the code for the purpose of tests. The code should be testable, but it should not contain code that is *only* for testing purposes. For example, making a field optional, and always setting it in the code path, but setting it to `None` for tests. In this case, the field should not be optional and just be the type it's set to in the code path.

## Rust best practices

1. Do not make structs, field, functions `pub` or `pub(crate)`. They should be private by default. 
Only make things `pub` if they need to be used by external crates.
Only make things `pub(crate)` if they need to be used by external modules within the same crate.

2. Do not use `unwrap()` or `expect()`. An error should be returned instead. The only exception is for invariants, which must be documented. For example, getting and unwrapping a value from a map where it is known that it must be `Some`.

3. Errors should provide as much context as possible. Errors in binary crates should be wrapped with `wrap_err()` to provide additional context. Errors in library crates must be fully typed and not use `eyre` or `anyhow`.

### Example for services using `eyre`

```rust
use eyre::WrapErr as _;

// Prefer
fn good_read_logs(p: impl AsRef<Path>) -> eyre::Result<()> {
    let f = std::fs::File::open(p)
      .wrap_err("failed to open file at provided path")?;
    let cfg: Config = serde_json::from_reader(f)
      .wrap_err("failed to read config")?;
    Ok(())
}

// Avoid
fn bad_read_logs(p: impl AsRef<Path>) -> eyre::Result<()> {
    let f = std::fs::File::open(p)?;
    let cfg: Config = serde_json::from_reader(f)?;
    Ok(())
}
```

### Example for libraries using `thiserror`

```rust
#[derive(Debug, thiserror::Error)]
enum BadError {
  #[error("io failed")]
  Io(#[from] std::io::Error),
  #[error("json failed")]
  Json(#[from] serde_json::se::Error),
}

#[derive(Debug, thiserror::Error)]
enum GoodError {
  #[error("failed opening log at {path}")]
  OpenLog(#[source] std::io::Error, path: String),
  #[error("failed parsing line {line} of log file as JSON")]
  ParseLine { source: serde_json::se::Error, line: usize },
}
```

4. Module names should not repeat for types within that module. For example:

```rust
// src/discovery.rs

// Good
struct Service {
    // ...
}

// Bad
// struct name should generally not contain the name of the module.
struct DiscoveryService {
    // ..
}
```

5. Do not add traits unless absolutely necessary. Especially do not create traits that ar
e only implemented by one type, or one type in the code and one type in the tests. Do not
 use `Box<dyn Trait>`. Strongly prefer using enums. For example:

```rust
// Good
struct KeypairA { .. } // has sign() implemented
struct KeypairB { .. } // has sign() implemented

enum Keypair {
    A(KeypairA),
    B(KeypairB),
}

impl Keypair {
    fn sign(&self, message: &[u8]) -> Signature {
        match self {
            Self::A(keypair) => keypair.sign(message),
            Self::B(keypair) => keypair.sign(message),
        }
    }
}

struct Service {
    keypair: Keypair,
}

// Bad
trait Keypair {
     fn sign(message: &[u8]);
}

struct KeypairA { .. }
impl Keypair for KeypairA { .. }

struct KeypairB { .. }
impl Keypair for KeypairB { .. }

struct Service {
    keypair: Box<dyn Keypair>,
}
```

## Clippy

See `.claude/commands/clippy.md`.

### Quick Fix Commands

```bash
cargo clippy -- --warn clippy::pedantic

# Auto-fix what can be automatically fixed (limited for pedantic)
cargo clippy --fix --allow-dirty -- --warn clippy::pedantic

# Check build
cargo c --tests
```

