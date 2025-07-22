import json
import re
import requests
from colorama import init, Fore, Style
from conv_manager import ConversationManager

API_URL = "http://localhost:11434/api/chat"
conv_mgr = ConversationManager()

init(autoreset=True)

def stream_colorize(chunks):
    in_think = False
    buf = ""
    for chunk in chunks:
        buf += chunk
        while True:
            if not in_think:
                idx = buf.find("<think>")
                if idx == -1:
                    yield buf
                    buf = ""
                    break
                yield buf[:idx]
                buf = buf[idx + len("<think>"):]
                in_think = True
            else:
                idx = buf.find("</think>")
                if idx == -1:
                    yield f"{Fore.GREEN}{buf}{Style.RESET_ALL}"
                    buf = ""
                    break
                yield f"{Fore.GREEN}{buf[:idx]}{Style.RESET_ALL}"
                buf = buf[idx + len("</think>"):]
                in_think = False
    if buf:
        if in_think:
            yield f"{Fore.GREEN}{buf}{Style.RESET_ALL}"
        else:
            yield buf

def send_message(conv_name: str, user_text: str, model: str = "deepseek-r1") -> str:
    # 1) record user
    conv_mgr.append(conv_name, "user", user_text)
    history = conv_mgr.get(conv_name)

    # 2) collect raw model chunks (with tags)
    raw_chunks = []
    with requests.post(
        API_URL,
        json={"model": model, "messages": history, "stream": True},
        stream=True,
        timeout=300
    ) as r:
        r.raise_for_status()
        for line in r.iter_lines():
            if not line: continue
            data = json.loads(line)
            text = data.get("delta", {}).get("content") or data.get("message", {}).get("content") or ""
            raw_chunks.append(text)

    # 3) print colored stream
    for piece in stream_colorize(raw_chunks):
        print(piece, end="", flush=True)
    print()

    # 4) build single raw reply
    raw_reply = "".join(raw_chunks)

    # 5) extract all think-blocks
    think_blocks = re.findall(r"<think>(.*?)</think>", raw_reply, re.DOTALL)
    full_think = "\n".join(b.strip() for b in think_blocks)

    # 6) extract only the user-facing content *after* the last </think>
    split_tag = "</think>"
    if split_tag in raw_reply:
        content = raw_reply.split(split_tag, 1)[1].strip()
    else:
        content = raw_reply.strip()

    # 7) append a single 3-key object
    history.append({
        "role":    "assistant",
        "think":   full_think,
        "content": content
    })
    conv_mgr.save(conv_name)

    return content
