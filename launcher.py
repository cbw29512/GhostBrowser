import os
import sys
import subprocess
import time
import socket
import ctypes

def is_docker_running():
    try:
        import docker
        client = docker.from_env()
        client.ping()
        return True
    except:
        return False

def launch():
    if not is_docker_running():
        ctypes.windll.user32.MessageBoxW(0, "Docker Desktop must be running to use Ghost Hub.", "Ghost Engine Error", 0x10)
        sys.exit(1)

    print("Igniting Ghost Engine Backend...")
    env = os.environ.copy()
    
    backend = subprocess.Popen(
        [sys.executable, "-m", "reflex", "run"], 
        creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0,
        env=env
    )

    print("Waiting for dashboard to come online...")
    for _ in range(40):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(('127.0.0.1', 3000)) == 0:
                break
        time.sleep(1)

    target_url = "http://localhost:3000"
    temp_profile = os.path.join(os.environ.get('TEMP', ''), 'ghost_browser_profile')
    
    # --- ARCHITECT FIX: Dynamically build the Auto-Auth Chrome Extension ---
    ext_dir = os.path.join(temp_profile, "ghost_ext")
    os.makedirs(ext_dir, exist_ok=True)
    
    with open(os.path.join(ext_dir, "manifest.json"), "w") as f:
        f.write('''{
  "name": "GhostAuth",
  "version": "1.0",
  "manifest_version": 3,
  "permissions": ["declarativeNetRequest"],
  "host_permissions": ["<all_urls>"],
  "declarativeNetRequest": {
    "rule_resources": [{"id": "rules", "enabled": true, "path": "rules.json"}]
  }
}''')

    # a2FzbV91c2VyOmdob3N0X3Bhc3M= is Base64 for "kasm_user:ghost_pass"
    with open(os.path.join(ext_dir, "rules.json"), "w") as f:
        f.write('''[
  {
    "id": 1,
    "priority": 1,
    "action": {
      "type": "modifyHeaders",
      "requestHeaders": [
        { "header": "Authorization", "operation": "set", "value": "Basic a2FzbV91c2VyOmdob3N0X3Bhc3M=" }
      ]
    },
    "condition": {
      "urlFilter": "*",
      "resourceTypes": ["main_frame", "sub_frame", "xmlhttprequest", "websocket", "other"]
    }
  }
]''')

    flags = [
        f"--app={target_url}",
        "--ignore-certificate-errors",
        "--allow-insecure-localhost",
        "--disable-web-security",
        "--test-type",  # Hides the yellow "Unsupported Flag" warning banner
        f"--user-data-dir={temp_profile}",
        f"--load-extension={ext_dir}",
        "--window-size=1400,900"
    ]
    
    browser_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    ]
    
    browser_exe = next((p for p in browser_paths if os.path.exists(p)), None)

    if browser_exe:
        print("Launching secure UI...")
        subprocess.run([browser_exe] + flags)
    else:
        import webbrowser
        webbrowser.open(target_url)
        input("Press Enter to close Ghost Hub...")

    # Cleanup backend and wipe RAM containers when user closes the app
    backend.terminate()
    try:
        import docker
        client = docker.from_env()
        for c in client.containers.list(all=True, filters={"ancestor": "kasmweb/chromium:1.15.0"}):
            c.remove(force=True)
    except:
        pass

if __name__ == "__main__":
    launch()