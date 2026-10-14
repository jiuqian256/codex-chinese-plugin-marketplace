# `coze agent at` contract

## Command input

| Option | Required | Meaning |
|---|---:|---|
| `--org-id` | for organization accounts | Global option populated from the current context's non-zero `account_id`; it becomes the `x-coze-account` request header. Omit it only when `account_id` is `0` for a personal account. |
| `--mode` | yes | `request` to delegate new work; `response` to complete the current inbound Agent-targeted request. |
| `--project-id` | yes | Current context's `group_id`, passed as a decimal string. |
| `--source-claw-id` | yes | Current context's `agent_id` (the calling Agent's `claw_id`), passed as a decimal string. |
| `--reply-to-message-id` | yes | Current context's `reply_to_message_id`. In response mode it must identify the current inbound AtAgent request message. It must be 1 to 256 UTF-8 bytes. |
| `--targets` | request only | JSON array with 1 to 3 target objects. Forbidden in response mode. |
| `--response-message` | response only | Non-empty completed result for the requesting Agent. Forbidden in request mode. |

Each target object has:

| Field | Required | Meaning |
|---|---:|---|
| `target_claw_id` | yes | Target project Agent's `claw_id`, encoded as a string. |
| `message` | yes | Non-empty delegated task, at most 4,000 Unicode code points. All target messages together must be at most 32 KiB in UTF-8. |
| `response_target_type` | no | `agent` (default) or `user`. |

Example with parallel targets:

```bash
coze --org-id "7491196930349875252" agent at \
  --mode request \
  --project-id "7600000000000000001" \
  --source-claw-id "7600000000000000002" \
  --reply-to-message-id "msg_current_turn" \
  --targets '[{"target_claw_id":"7600000000000000003","message":"Audit the API for security risks.","response_target_type":"agent"},{"target_claw_id":"7600000000000000004","message":"Check the user-facing copy and report edits.","response_target_type":"agent"}]' \
  --format json
```

Response example:

```bash
coze --org-id "7491196930349875252" agent at \
  --mode response \
  --project-id "7600000000000000001" \
  --source-claw-id "7600000000000000003" \
  --reply-to-message-id "at_agent_request_message_id" \
  --response-message "Audit complete: no blocking security risks were found." \
  --format json
```

The response target is derived by the service from the referenced request. Never pass `--targets` in response mode.

## Success output

The command emits one JSON envelope:

```json
{
  "code": 0,
  "msg": "success",
  "data": {
    "message_id": "generated_dispatch_message_id",
    "status": "accepted",
    "idempotency_replayed": false
  },
  "logid": "request_log_id"
}
```

- `message_id` identifies the visible project collaboration message.
- `status=accepted` means asynchronous dispatch was accepted.
- `idempotency_replayed=true` means the same logical request was already accepted; do not send a new variant merely to force another execution.
- `logid` is the primary diagnostic key.

## Failure handling

| Failure | Action |
|---|---|
| Invalid JSON or malformed target | Fix locally; do not call again unchanged. |
| Target is not an Agent project member | Refresh `coze agent member list`; choose an active Agent member. |
| Target equals source | Choose a different Agent. |
| Permission/authentication failure | Refresh authentication or trusted runtime context; do not broaden credentials. |
| Transport timeout, response unknown | Retry the byte-equivalent logical request. |
| Service error with a `logid` | Preserve the full JSON envelope and diagnose using the `logid`. |

## Context discipline

Map trusted current-turn context fields exactly: non-zero `account_id` -> global `--org-id`, `group_id` -> `--project-id`, `agent_id` -> `--source-claw-id`, and `reply_to_message_id` -> `--reply-to-message-id`. Use the same organization context for member discovery and dispatch. Omit `--org-id` only when `account_id` is `0` for a personal account.

`reply_to_message_id` is an opaque identifier and must refer to the message currently being processed. In request mode this is the current triggering message. In response mode this is the current inbound AtAgent request message ID. Pass it through unchanged. It is not an unrelated dispatch result, a previous turn's message, a session ID, or a generated random value.

Rendering an `at://agent:<claw_id>` link or a visible `@name` mention does not call this contract. A real request or response requires executing `coze agent at` in the corresponding mode and receiving `code=0`, `data.status="accepted"`, and a non-empty `data.message_id`.

An inbound `mode=response` is already the peer Agent's result. Consume it and synthesize; never answer it with another AtAgent response.
