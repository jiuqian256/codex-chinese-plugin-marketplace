---
name: coze-agent-collaboration
description: '扣子 Agent 协作：通过 Coze CLI 正确派发和接收 Agent 协作请求，避免消息循环。 CRITICAL Coze project Agent collaboration protocol: use `coze agent at --mode request` to delegate to peer Agents and `coze agent at --mode response` to return a result for an inbound Agent-targeted request. A visible @mention never dispatches or responds. Also use this skill to discover Agent members, consume collaboration responses without creating a loop, or retry an unchanged call after an unknown transport outcome.'
metadata:
  requires:
    bins:
    - coze
  cliHelp: coze agent at --help
  version: 0.3.7
---

## 中文名称与用法

**中文名称：** 扣子 Agent 协作

**用途：** 通过 Coze CLI 正确派发和接收 Agent 协作请求，避免消息循环。

**调用示例：** 使用 $chinese-skills:coze-agent-collaboration 通过 Coze CLI 与项目中的其他 Agent 协作。

文中的 `<SKILL_DIR>` 指本次加载的 SKILL.md 所在目录；从实际技能路径解析，不假定用户目录、操作系统或插件缓存版本。脚本接收的项目路径和输出路径仍使用当前任务的实际路径。


# Coze Agent Collaboration

Use `coze agent at` for both halves of project-group Agent collaboration:

- `--mode request` delegates work to one or more peer Agents.
- `--mode response` returns completed work for the current inbound Agent request.

An `at://agent:<claw_id>` link or visible `@name` mention only controls display; it neither dispatches nor responds. Never report delivery unless `coze agent at` returned an accepted response.

Treat the command as asynchronous dispatch: an accepted response means delivery was queued, not that the delegated work has finished.

## Preconditions

- Run only inside a current Coze project Agent turn.
- Obtain `account_id`, `group_id`, `agent_id`, and `reply_to_message_id` from the trusted current-turn context. Never guess them, derive them from names, or reuse values from an earlier turn. In response mode, `reply_to_message_id` must be the message ID of the current inbound AtAgent request.
- Map context fields exactly: non-zero `account_id` -> global `--org-id`, `group_id` -> `--project-id`, `agent_id` -> `--source-claw-id`, and `reply_to_message_id` -> `--reply-to-message-id`. Omit `--org-id` only when `account_id` is `0` for a personal account.
- Keep `account_id`, `group_id`, `agent_id`, and every `target_claw_id` as decimal strings. Never convert these int64 IDs through a JavaScript number or another floating-point type. Treat `reply_to_message_id` as an opaque string and pass it through unchanged.
- Keep `reply_to_message_id` within 256 UTF-8 bytes, each target message within 4,000 Unicode code points, and all target messages together within 32 KiB.
- Check authentication with `coze auth status --format json` when the CLI reports an authentication error.
- Do not apply Coze App version checks. CLI availability is independent of the App UI version gate.

## Choose the mode

- Initiating new delegated work: use `request`.
- Completing an inbound `mode=request` whose `response_target_type=agent`: use `response` exactly once after the work is complete.
- Receiving `mode=response`: consume the result and continue synthesis for the user. Do **not** call `coze agent at` again; that would create a collaboration loop.
- Handling an inbound request whose `response_target_type=user`: reply normally to the user. Do not call response mode.

## Request workflow

1. Refresh current project members before each dispatch:

   ```bash
   coze --org-id "<account_id>" agent member list --project-id "<group_id>" --format json
   ```

2. Select only members with `user_type=2` and a non-empty `claw_id`. Exclude the current `agent_id` (the `source_claw_id`). Delegate to at most three Agents per request.
3. Give every target a concrete, self-contained task. Do not forward secrets or unrelated conversation text.
4. Call `coze agent at --mode request` with the exact current-turn identifiers and a JSON array:

   ```bash
   coze --org-id "<account_id>" agent at \
     --mode request \
     --project-id "<group_id>" \
     --source-claw-id "<agent_id>" \
     --reply-to-message-id "<reply_to_message_id>" \
     --targets '[{"target_claw_id":"<target_claw_id>","message":"Review the API contract and return concrete issues.","response_target_type":"agent"}]' \
     --format json
   ```

5. Require `code=0`, `data.status="accepted"`, and a non-empty `data.message_id` before treating dispatch as accepted. An `at://agent:<claw_id>` mention without this command result is not a dispatch. Preserve `logid` for diagnostics.
6. Continue according to `response_target_type`:
   - `agent` (default): the target reports back in a later collaboration turn. Do not block or poll after `accepted`, and do not dispatch a duplicate; incorporate the later response before final synthesis when the task depends on it.
   - `user`: the target delivers directly to the user; use only when direct independent delivery was explicitly intended.

## Response workflow

1. Confirm the current turn is an inbound AtAgent `mode=request` with `response_target_type=agent`. Never use response mode for a normal user message or an inbound `mode=response`.
2. Complete the requested work, then call response mode without `--targets`:

   ```bash
   coze --org-id "<account_id>" agent at \
     --mode response \
     --project-id "<group_id>" \
     --source-claw-id "<agent_id>" \
     --reply-to-message-id "<current_at_agent_request_message_id>" \
     --response-message "<completed result for the requesting Agent>" \
     --format json
   ```

3. Require `code=0`, `data.status="accepted"`, and a non-empty `data.message_id`. After acceptance, do not send a second request or a visible `@source` message as an acknowledgement.

## Safety and retry rules

- Never target the source Agent itself.
- Always pass explicit `--mode request` or `--mode response`.
- Request mode requires `--targets` and forbids `--response-message`; response mode requires `--response-message` and forbids `--targets`.
- Do not invent an `idempotency_key`; the service derives idempotency from trusted request context.
- On a transport timeout with no response, retry the exact same request. Keep identifiers, target order, messages, and response targets unchanged.
- Do not retry validation, permission, or membership errors until the underlying input or authorization is corrected.
- Do not report delegated work as complete from the `accepted` response alone.
- Prefer one focused request containing all independent targets over several duplicate calls.

Read [references/at-agent-contract.md](references/at-agent-contract.md) for the full input/output contract and failure handling.
