# Portable Loader Prompt

Use this prompt in agents that do not natively discover `SKILL.md` folders, including Claude Code, Hermes, and OpenClaw deployments that receive skills as copied folders.

```text
You have access to a local skill named guarantee-risk-scan at:
<GUARANTEE_RISK_SCAN_SKILL_ROOT>

When the user asks to scan A-share holdings for cumulative guarantee risks, monitor guarantee ratios, flag excess guarantee events, generate guarantee risk reports, or schedule recurring guarantee risk scans:
1. Read <GUARANTEE_RISK_SCAN_SKILL_ROOT>/SKILL.md.
2. For detailed API fields and risk classification logic, read <GUARANTEE_RISK_SCAN_SKILL_ROOT>/references/api_guide.md.
3. Use the local pandadata-api skill to verify exact method parameters and fields before any real Pandadata call.
4. Set environment variables PANDA_DATA_USERNAME and PANDA_DATA_PASSWORD before calling run().
5. Preserve source method names, query parameters, data dates, risk thresholds, and stale-data notes.
6. Do not invent data interfaces, credentials, fields, disclosure dates, or trading advice.
```
