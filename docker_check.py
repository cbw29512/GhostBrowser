"""
Run this if 'Launch Ghost' fails:
    python docker_check.py

Tests the exact same Docker call the app uses, prints container logs on failure.
"""
import docker
import time
import sys

IMAGE = "kasmweb/chromium:1.15.0"

print("=" * 60)
print("Ghost Browser - Docker Diagnostic")
print("=" * 60)

# 1. Connect
try:
    client = docker.from_env()
    print(f"✅ Docker connected: {client.version()['Version']}")
except Exception as e:
    print(f"❌ Docker connection FAILED: {e}")
    print("   → Is Docker Desktop running?")
    sys.exit(1)

# 2. Check image
print(f"\nChecking image '{IMAGE}'...")
try:
    img = client.images.get(IMAGE)
    print(f"✅ Image found locally: {img.id[:20]}")
except docker.errors.ImageNotFound:
    print(f"❌ Image NOT found. Pulling now (this may take a few minutes)...")
    try:
        for line in client.api.pull(IMAGE, stream=True, decode=True):
            status = line.get('status', '')
            prog = line.get('progress', '')
            if status:
                print(f"   {status} {prog}", end='\r')
        print(f"\n✅ Pull complete.")
    except Exception as e:
        print(f"❌ Pull failed: {e}")
        sys.exit(1)
except Exception as e:
    print(f"❌ Image check error: {e}")

# 3. Memory check
print("\nChecking Docker memory...")
try:
    info = client.info()
    mem_gb = info.get('MemTotal', 0) / (1024**3)
    if mem_gb < 2.0:
        print(f"⚠️  Only {mem_gb:.1f}GB RAM — Kasm needs 2GB+")
        print("   → Docker Desktop → Settings → Resources → increase Memory")
    else:
        print(f"✅ Docker memory: {mem_gb:.1f}GB")
except Exception as e:
    print(f"   (Could not check memory: {e})")

# 4. Clean up old containers
print("\nCleaning up stale ghost containers...")
old = client.containers.list(all=True, filters={"ancestor": IMAGE})
for c in old:
    print(f"   Removing {c.id[:12]}...")
    c.remove(force=True)
print(f"   Done ({len(old)} removed).")

# 5. Test launch (matches exactly what the app does)
print(f"\nLaunching test container...")
container = None
try:
    container = client.containers.run(
        IMAGE,
        detach=True,
        shm_size='512m',
        ports={'6901/tcp': None},
        environment={"VNC_PW": "ghost_pass", "KASM_PORT": "443"},
    )
    print(f"✅ Container created: {container.id[:12]}")
    print("   Waiting 5 seconds...")
    time.sleep(5)
    container.reload()

    status    = container.attrs['State']['Status']
    exit_code = container.attrs['State']['ExitCode']
    print(f"   Status:   {status}")
    print(f"   ExitCode: {exit_code}")

    if status == 'running':
        ports    = container.attrs['NetworkSettings']['Ports']
        binding  = ports.get('6901/tcp')
        if binding:
            host_port = binding[0]['HostPort']
            print(f"\n✅ ALL GOOD — Kasm running on https://localhost:{host_port}")
            print(f"   The app should work. If the iframe is blank, use 'Pop Out Window'")
            print(f"   and type 'thisisunsafe' to accept the self-signed cert.")
        else:
            print(f"⚠️  Container running but 6901/tcp not bound.")
            print(f"   Available ports: {list(ports.keys())}")
    else:
        logs = container.logs(tail=40).decode('utf-8', errors='replace')
        print(f"\n❌ Container CRASHED (exit_code={exit_code})")
        print(f"\n--- Container Logs ---\n{logs}")
        print("\n→ Common fixes:")
        print("   1. Docker memory < 2GB: Docker Desktop → Settings → Resources → Memory → 3GB+")
        print("   2. Port 6901 in use:    netstat -an | findstr 6901  then kill the process")
        print("   3. Corrupted image:     docker rmi kasmweb/chromium:1.15.0  then rerun this script")

except Exception as e:
    print(f"❌ Launch exception: {e}")

finally:
    if container:
        try:
            container.remove(force=True)
            print("\nTest container cleaned up.")
        except Exception:
            pass

print("\n" + "=" * 60)
print("Diagnostic complete.")
