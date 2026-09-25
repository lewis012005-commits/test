# Red Team Report Spec

What can break the build, and the minimum the attacker needs to report for each so it can be patched.
Rule of thumb: report **where it broke, what class of bug, and the evidence**. Never the exploit, the
attacker's reasoning, or unused variants. The attacker's harness owns reproduction and re-testing.

## Every report, every time

| Field | Example |
|---|---|
| Commit tested | `a1b2c3d` |
| Component | `api/auth.py::login`, `sonnet-sorter agent`, `dump/` folder |
| Category | One of the categories below |
| Severity | Critical / High / Medium / Low |
| Evidence | Stack trace, log lines, bad output (redact any secrets) |
| Reproducibility | Always / intermittent / only after a sequence |
| Re-test result | Pass / fail after each fix, run by the harness |
| Harmless trigger | Optional. Smallest benign input that shows the bug |

## Classic application bugs

| Category | What it looks like | What I need on top of the basics |
|---|---|---|
| Injection (SQL, shell, template, LDAP) | Input reaches an interpreter | Entry point, the sink it reached, input type |
| Path traversal / file access | Reads or writes outside the allowed folder | Which path parameter, what file it reached |
| Broken authentication | Logged in without valid credentials | Endpoint, which check was skipped or weak |
| Broken authorisation | Did something its role shouldn't allow | Role used, action performed, resource touched |
| Unsafe deserialisation / parsing | Parser executes or expands attacker data | Parser, format, where the data came from |
| Memory safety (native code) | Crash, corruption, overread | Crash trace or sanitizer output, input size |
| Crypto misuse | Weak algorithm, bad randomness, reused keys | Algorithm, where it's used, what it protects |
| Race condition / TOCTOU | Check and use happen at different times | The two operations, rough timing window |
| Resource exhaustion (DoS) | Hang, memory blowout, disk fill | Component, input size or rate, resource exhausted |
| Output handling (XSS etc.) | Output rendered or executed unsafely | Where output is rendered, what context |

## Infrastructure and config

| Category | What it looks like | What I need on top of the basics |
|---|---|---|
| Secret exposure | Key, token or password reachable | Secret *type* (never the value), where found, who can reach it |
| Misconfiguration | Debug on, permissive CORS, default creds | Setting name, file, effect |
| Network exposure | Service reachable that shouldn't be | Service, port, bind address |
| Vulnerable dependency | Known-bad package version | Package, version, CVE ID |
| Supply chain / build tampering | Build pulls or runs untrusted code | Which step, what it pulled |
| Privilege escalation | Went from low to high privilege | Starting privilege, ending privilege, bug class |
| Lateral movement | Hopped from one component to another | Foothold, each hop, **what trust allowed each hop**, end point |
| Persistence | Something survived a restart or cleanup | What artifact, where it lived |
| Logging / monitoring gaps | Action happened with no record | Which action, which log should have caught it |

## Agent and pipeline specific

| Category | What it looks like | What I need on top of the basics |
|---|---|---|
| Direct prompt injection | Agent obeyed attacker instructions | Agent, input channel, behaviour caused |
| Indirect prompt injection | Poisoned file, tool output or web page steered an agent | Poisoned source, which agent read it, what it did |
| Inter-agent trust poisoning | Haiku's dump tricked Sonnet, or Sonnet's handoff tricked the lead | Writer, reader, what was accepted without checking |
| Excessive agency / tool misuse | Agent used a tool outside its job | Agent, tool, action, what scope it should have had |
| Guardrail bypass | Agent produced something its rules forbid | Which rule, input class, output (redacted) |
| Loop / cost abuse | Infinite loop, token burn, orchestrator stuck | Loop location, trigger, how many rounds before cap |
| Context / data leakage | Agent revealed data it shouldn't | What leaked (type, not content), through which channel |
| Handoff tampering | Dump folder files altered, swapped or half-written | File, manifest state, which agent consumed it |

## Lateral movement chain format

```
foothold:  <component> via <bug class>
hop 1:     <A> -> <B> allowed by <trust: shared token / no auth / writable folder / trusted output>
hop 2:     <B> -> <C> allowed by <...>
reached:   <what it could do at the end>
```

The fix is usually on the "allowed by" lines: least privilege, per-component credentials, segmentation,
and agents that validate each other's output instead of trusting it.

## Never include

- Working exploit code or weaponised payloads
- The attacker's reasoning or how it picks targets
- Variants it hasn't used yet
- Real secret values
