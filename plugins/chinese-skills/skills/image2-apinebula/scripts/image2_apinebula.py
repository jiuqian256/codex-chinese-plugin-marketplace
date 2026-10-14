import argparse
import base64
import json
import mimetypes
import os
import sys
import time
from pathlib import Path
from urllib.parse import urlparse

import requests

BASE_URL = "https://apinebula.com"
IMG_API_BASE_URL = "https://img-api.apinebula.com/v1"
DEFAULT_MODEL = "gpt-image-2"
LOCAL_EDIT_DEFAULT_MODEL = "gpt-image-2-vip"
DEFAULT_QUALITY = "high"
DEFAULT_OUTDIR = Path.cwd() / "outputs" / "image2-apinebula"


class ApiError(RuntimeError):
    pass


def get_api_key() -> str:
    key = os.getenv("APINEBULA_API_KEY", "").strip()
    if not key:
        raise ApiError("Configure your own APINEBULA_API_KEY environment variable before using this skill.")
    return key


def headers(json_content_type: bool = True) -> dict:
    h = {"Authorization": f"Bearer {get_api_key()}"}
    if json_content_type:
        h["Content-Type"] = "application/json"
    return h


def request_json(method: str, path: str, *, params=None, payload=None):
    url = f"{BASE_URL}{path}"
    resp = requests.request(method, url, headers=headers(), params=params, json=payload, timeout=120)
    try:
        data = resp.json()
    except Exception:
        data = {"raw": resp.text}
    if resp.status_code >= 400:
        raise ApiError(f"HTTP {resp.status_code}: {json.dumps(data, ensure_ascii=False)}")
    return data


def submit_generation(prompt: str, model: str, quality: str):
    payload = {
        "model": model,
        "prompt": prompt,
        "quality": quality,
    }
    return request_json("POST", "/v1/image-tasks/generations", payload=payload)


def submit_edit(prompt: str, image_urls: list[str], model: str, quality: str):
    payload = {
        "model": model,
        "prompt": prompt,
        "images": [{"image_url": url} for url in image_urls],
        "quality": quality,
    }
    return request_json("POST", "/v1/image-tasks/edits", payload=payload)


def get_task(task_id: str, detail: bool = True):
    return request_json("GET", f"/v1/image-tasks/{task_id}", params={"detail": str(detail).lower()})


def submit_local_edit(prompt: str, image_files: list[str], model: str, quality: str, outdir: Path,
                      size: str | None = None, input_fidelity: str | None = "high",
                      response_format: str = "b64_json", mask_file: str | None = None):
    url = f"{IMG_API_BASE_URL}/images/edits"
    data = {
        "model": model,
        "prompt": prompt,
        "quality": quality,
        "response_format": response_format,
    }
    if size:
        data["size"] = size
    if input_fidelity:
        data["input_fidelity"] = input_fidelity

    file_handles = []
    files = []
    try:
        for image_file in image_files:
            p = Path(image_file).expanduser().resolve()
            if not p.exists():
                raise FileNotFoundError(f"Image file not found: {p}")
            mime = mimetypes.guess_type(str(p))[0] or "application/octet-stream"
            fh = open(p, "rb")
            file_handles.append(fh)
            files.append(("image", (p.name, fh, mime)))

        if mask_file:
            mp = Path(mask_file).expanduser().resolve()
            if not mp.exists():
                raise FileNotFoundError(f"Mask file not found: {mp}")
            mime = mimetypes.guess_type(str(mp))[0] or "application/octet-stream"
            fh = open(mp, "rb")
            file_handles.append(fh)
            files.append(("mask", (mp.name, fh, mime)))

        resp = requests.post(url, headers=headers(json_content_type=False), data=data, files=files, timeout=300)
        try:
            result = resp.json()
        except Exception:
            result = {"raw": resp.text}
        if resp.status_code >= 400:
            raise ApiError(f"HTTP {resp.status_code}: {json.dumps(result, ensure_ascii=False)}")

        saved = save_sync_result(result, outdir, prefix="local-edit")
        return result, saved
    finally:
        for fh in file_handles:
            try:
                fh.close()
            except Exception:
                pass


def extract_task_id(data: dict) -> str:
    return data.get("task_id") or data.get("id")


def wait_for_task(task_id: str, interval: float = 3.0, timeout: int = 600):
    start = time.time()
    while True:
        task = get_task(task_id, detail=True)
        status = task.get("status")
        print(f"[poll] task_id={task_id} status={status}")
        if status in {"completed", "failed"}:
            return task
        if time.time() - start > timeout:
            raise TimeoutError(f"Timed out waiting for task {task_id}")
        time.sleep(interval)


def _safe_suffix_from_url(url: str) -> str:
    path = urlparse(url).path
    suffix = Path(path).suffix.lower()
    return suffix if suffix else ".png"


def _task_result_items(task: dict):
    detail = task.get("detail")
    if isinstance(detail, dict):
        data = detail.get("data")
        if isinstance(data, list):
            return data
    data = task.get("data")
    if isinstance(data, list):
        return data
    return []


def download_from_task(task: dict, outdir: Path):
    outdir.mkdir(parents=True, exist_ok=True)
    task_id = task.get("task_id") or task.get("id") or "task"
    items = _task_result_items(task)
    if not items:
        raise ApiError(f"No downloadable result found in task: {json.dumps(task, ensure_ascii=False)}")

    saved = []
    for idx, item in enumerate(items, start=1):
        if "download_url" in item and item["download_url"]:
            url = item["download_url"]
            suffix = _safe_suffix_from_url(url)
            path = outdir / f"{task_id}-{idx}{suffix}"
            with requests.get(url, timeout=120, stream=True) as resp:
                resp.raise_for_status()
                with open(path, "wb") as f:
                    for chunk in resp.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
            saved.append(str(path.resolve()))
        elif "b64_json" in item and item["b64_json"]:
            path = outdir / f"{task_id}-{idx}.png"
            with open(path, "wb") as f:
                f.write(base64.b64decode(item["b64_json"]))
            saved.append(str(path.resolve()))
    if not saved:
        raise ApiError(f"Task completed but no supported result payload was found: {json.dumps(items, ensure_ascii=False)}")
    return saved


def save_sync_result(result: dict, outdir: Path, prefix: str = "image"):
    outdir.mkdir(parents=True, exist_ok=True)
    items = result.get("data") or []
    if not isinstance(items, list) or not items:
        raise ApiError(f"No image data found in response: {json.dumps(result, ensure_ascii=False)}")

    saved = []
    for idx, item in enumerate(items, start=1):
        if item.get("b64_json"):
            ext = ".jpg" if result.get("output_format") == "jpeg" else ".png"
            path = outdir / f"{prefix}-{idx}{ext}"
            with open(path, "wb") as f:
                f.write(base64.b64decode(item["b64_json"]))
            saved.append(str(path.resolve()))
        elif item.get("url"):
            url = item["url"]
            suffix = _safe_suffix_from_url(url)
            path = outdir / f"{prefix}-{idx}{suffix}"
            with requests.get(url, timeout=120, stream=True) as resp:
                resp.raise_for_status()
                with open(path, "wb") as f:
                    for chunk in resp.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
            saved.append(str(path.resolve()))
    if not saved:
        raise ApiError(f"Response did not include supported image payloads: {json.dumps(items, ensure_ascii=False)}")
    return saved


def print_json(data):
    print(json.dumps(data, ensure_ascii=False, indent=2))


def cmd_generate(args):
    result = submit_generation(args.prompt, args.model, args.quality)
    print_json(result)
    task_id = extract_task_id(result)
    if args.wait and task_id:
        task = wait_for_task(task_id, interval=args.interval, timeout=args.timeout)
        print_json(task)
        if task.get("status") == "failed":
            raise ApiError(json.dumps(task.get("error") or task, ensure_ascii=False))
        if args.download:
            saved = download_from_task(task, Path(args.outdir))
            print(json.dumps({"saved_files": saved}, ensure_ascii=False, indent=2))


def cmd_edit(args):
    if args.image_file:
        model = args.model or LOCAL_EDIT_DEFAULT_MODEL
        result, saved = submit_local_edit(
            args.prompt,
            args.image_file,
            model,
            args.quality,
            Path(args.outdir),
            size=args.size,
            input_fidelity=args.input_fidelity,
            response_format=args.response_format,
            mask_file=args.mask_file,
        )
        print_json(result)
        print(json.dumps({"saved_files": saved}, ensure_ascii=False, indent=2))
        return

    if not args.image_url:
        raise ApiError("For URL-based edit you must provide at least one --image-url. For local files use --image-file.")

    model = args.model or DEFAULT_MODEL
    result = submit_edit(args.prompt, args.image_url, model, args.quality)
    print_json(result)
    task_id = extract_task_id(result)
    if args.wait and task_id:
        task = wait_for_task(task_id, interval=args.interval, timeout=args.timeout)
        print_json(task)
        if task.get("status") == "failed":
            raise ApiError(json.dumps(task.get("error") or task, ensure_ascii=False))
        if args.download:
            saved = download_from_task(task, Path(args.outdir))
            print(json.dumps({"saved_files": saved}, ensure_ascii=False, indent=2))


def cmd_status(args):
    task = get_task(args.task_id, detail=args.detail)
    print_json(task)


def cmd_download(args):
    task = get_task(args.task_id, detail=True)
    if task.get("status") != "completed":
        raise ApiError(f"Task {args.task_id} is not completed. Current status: {task.get('status')}")
    saved = download_from_task(task, Path(args.outdir))
    print(json.dumps({"saved_files": saved}, ensure_ascii=False, indent=2))


def build_parser():
    p = argparse.ArgumentParser(description="APINebula image2 helper")
    sub = p.add_subparsers(dest="command", required=True)

    p_gen = sub.add_parser("generate", help="submit image generation task")
    p_gen.add_argument("--prompt", required=True)
    p_gen.add_argument("--model", default=DEFAULT_MODEL)
    p_gen.add_argument("--quality", default=DEFAULT_QUALITY)
    p_gen.add_argument("--wait", action="store_true")
    p_gen.add_argument("--download", action="store_true")
    p_gen.add_argument("--interval", type=float, default=3.0)
    p_gen.add_argument("--timeout", type=int, default=600)
    p_gen.add_argument("--outdir", default=str(DEFAULT_OUTDIR))
    p_gen.set_defaults(func=cmd_generate)

    p_edit = sub.add_parser("edit", help="edit image(s) from URL(s) or local file(s)")
    p_edit.add_argument("--prompt", required=True)
    p_edit.add_argument("--image-url", action="append")
    p_edit.add_argument("--image-file", action="append")
    p_edit.add_argument("--mask-file")
    p_edit.add_argument("--model")
    p_edit.add_argument("--quality", default=DEFAULT_QUALITY)
    p_edit.add_argument("--size")
    p_edit.add_argument("--response-format", default="b64_json")
    p_edit.add_argument("--input-fidelity", default="high")
    p_edit.add_argument("--wait", action="store_true")
    p_edit.add_argument("--download", action="store_true")
    p_edit.add_argument("--interval", type=float, default=3.0)
    p_edit.add_argument("--timeout", type=int, default=600)
    p_edit.add_argument("--outdir", default=str(DEFAULT_OUTDIR))
    p_edit.set_defaults(func=cmd_edit)

    p_status = sub.add_parser("status", help="get task status")
    p_status.add_argument("--task-id", required=True)
    p_status.add_argument("--detail", action="store_true")
    p_status.set_defaults(func=cmd_status)

    p_dl = sub.add_parser("download", help="download completed task result")
    p_dl.add_argument("--task-id", required=True)
    p_dl.add_argument("--outdir", default=str(DEFAULT_OUTDIR))
    p_dl.set_defaults(func=cmd_download)

    return p


def main():
    parser = build_parser()
    args = parser.parse_args()
    try:
        args.func(args)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
