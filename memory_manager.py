import os
import subprocess
import json
from datetime import datetime

MEMORY_DIR = os.path.abspath("./.memory")

def get_injected_prompt(agent_role):
    prompt_path = f"./agents/{agent_role}/prompt.md"
    with open(prompt_path, "r") as f:
        base_prompt = f.read()

    context_path = f"{MEMORY_DIR}/system_context.md"
    lessons_path = f"{MEMORY_DIR}/lessons_learned.md"

    context = open(context_path).read() if os.path.exists(context_path) else ""
    lessons = open(lessons_path).read() if os.path.exists(lessons_path) else ""

    # Daftar skill kustom yang tersedia
    skills_dir = f"./agents/{agent_role}/skills"
    skills = os.listdir(skills_dir) if os.path.exists(skills_dir) else []
    skills_info = "\n".join([f"- {s}" for s in skills]) if skills else "Tidak ada tool kustom."

    full_prompt = f"""{base_prompt}

---
### KONTEKS ARSITEKTUR:
{context}

### CATATAN EVALUASI SEBELUMNYA:
{lessons}

### TOOL/SKILL TERSEDIA:
{skills_info}
"""
    return full_prompt

def record_task_log(task_desc, status):
    log_file = f"{MEMORY_DIR}/task_history.jsonl"
    entry = {
        "timestamp": datetime.now().isoformat(),
        "task": task_desc,
        "status": status
    }
    with open(log_file, "a") as f:
        f.write(json.dumps(entry) + "\n")

def sync_git(commit_message):
    try:
        subprocess.run(["git", "add", ".memory/", "agents/"], check=True)
        diff = subprocess.run(["git", "diff", "--cached", "--quiet"])
        if diff.returncode != 0:
            subprocess.run(["git", "commit", "-m", f"chore(agent): {commit_message}"], check=True)
            # Batalkan komentar jika remote origin sudah disiapkan
            # subprocess.run(["git", "push", "origin", "main"], check=True)
            return "💾 Memori & skill berhasil di-commit ke Git."
        return "ℹ️ Tidak ada perubahan memori untuk di-commit."
    except Exception as e:
        return f"⚠️ Gagal sinkronisasi Git: {str(e)}"
