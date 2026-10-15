import subprocess
import os
import tempfile
from memory_manager import get_injected_prompt, record_task_log, sync_git

WORKSPACE_DIR = os.path.abspath("./workspace")

def execute_antigravity(agent_role, callback_msg=None):
    if callback_msg:
        callback_msg(f"⚙️ **{agent_role.upper()}** sedang bekerja...")

    full_prompt = get_injected_prompt(agent_role)

    # Simpan prompt gabungan ke file temporer untuk dieksekusi CLI
    with tempfile.NamedTemporaryFile("w", delete=False, suffix=".md") as temp_file:
        temp_file.write(full_prompt)
        temp_prompt_path = temp_file.name

    cmd = [
        "antigravity", "exec",
        "--prompt-file", temp_prompt_path,
        "--workspace", WORKSPACE_DIR,
        "--auto-approve"
    ]

    try:
        process = subprocess.run(cmd, capture_output=True, text=True, timeout=900)
        os.remove(temp_prompt_path)

        if process.returncode == 0:
            return True, f"✅ **{agent_role.upper()}** selesai.\n```\n{process.stdout[-250:]}\n```"
        else:
            return False, f"❌ **{agent_role.upper()}** mengalami error:\n```\n{process.stderr[-250:]}\n```"
    except Exception as e:
        if os.path.exists(temp_prompt_path):
            os.remove(temp_prompt_path)
        return False, f"⚠️ Exception pada {agent_role}: {str(e)}"

def run_mission_pipeline(task_desc, update_fn):
    # Simpan instruksi misi ke workspace
    with open(f"{WORKSPACE_DIR}/TASK.md", "w") as f:
        f.write(task_desc)

    update_fn("🚀 **Mission Control:** Misi baru diterima. Memulai pipeline eksekusi...")

    # 1. Fase Riset & Arsitektur
    ok, msg = execute_antigravity("researcher", update_fn)
    update_fn(msg)
    if not ok:
        record_task_log(task_desc, "FAILED_AT_RESEARCH")
        return

    # 2. Fase Pengembangan Kode
    ok, msg = execute_antigravity("developer", update_fn)
    update_fn(msg)
    if not ok:
        record_task_log(task_desc, "FAILED_AT_DEV")
        return

    # 3. Fase Verifikasi & Audit QA
    ok, msg = execute_antigravity("qa", update_fn)
    update_fn(msg)

    # Catat histori dan sinkronkan memori ke Git
    record_task_log(task_desc, "SUCCESS" if ok else "FLAGGED_BY_QA")
    git_status = sync_git(f"update memory after: {task_desc[:30]}")
    update_fn(git_status)

    update_fn("🏁 **Mission Control:** Seluruh tahapan selesai. Kode siap di-review pada folder `workspace/`.")
