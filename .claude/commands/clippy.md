# Clippy

Run the following steps until there are no more pedantic clippy warnings.
Pedantic clippy command: `cargo clippy --all-targets --all-features -- --warn clippy::pedantic`
IMPORTANT:
DO NOT USE `#[allow]`!
DO NOT STOP UNTIL THERE ARE NO WARNINGS LEFT!
Only output what step of the plan you are running.
If there are over 100 warnings, you can think hard.
Note that you can run `cargo clippy --fix -- --warn clippy::pedantic` to auto-fix warnings.
Make a new branch before you start.

1. Run clippy for each crate; write the warnings (with filename and line numbers) to a file as a checklist ordered by crate and warning type. 
2. In the same file, write a detailed fix plan for each crate and each warning within the crate. 
3. Execute each step of the fix plan one at a time.
4. After each step is executed, run `cargo c --tests` and ensure the code still builds.
5. If it does not build, fix the errors you caused.
6. Run clippy again. If there are any warnings left, go to step 1.

### Testing Strategy

After each phase:
1. **Compilation check**: `cargo c --tests`
2. **Clippy verification**: `cargo clippy -- --warn clippy::pedantic`
