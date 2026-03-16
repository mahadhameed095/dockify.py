import argparse
import subprocess
import tempfile
from pathlib import Path

def make_keep_paths_script(script_name_no_ext, keep_files):
    cleaned = set(k.strip().rstrip('/') for k in keep_files if k.strip())
    cleaned.add(script_name_no_ext)
    return " ".join(cleaned)

def generate_dockerfile(script_name, req_present, keep_files):
    script_name_no_ext = Path(script_name).stem

    # Generate copy commands for each item in keep_files
    keep_copy_lines = "\n".join(
        f"COPY --from=builder /app/{item.strip()} /app/{Path(item.strip()).name}"
        for item in keep_files + [f"dist/{script_name_no_ext}"]
    )

    return f"""
# Stage 1: Build
FROM python:3.8-slim AS builder

WORKDIR /app

COPY . /app

RUN apt-get update && apt-get install -y gcc && \\
    pip install pyinstaller {'-r requirements.txt' if req_present else ''} && \\
    pyinstaller --onefile {script_name}

# Stage 2: Final image
FROM python:3.8-slim

WORKDIR /app

{keep_copy_lines}

ENTRYPOINT ["./{script_name_no_ext}"]
"""


def build_image_and_save(dockerfile_path, tag, output_tar_path):
    # dockerfile_path: full path to Dockerfile
    # cwd = current working directory where script was called
    cwd = Path.cwd()

    subprocess.run([
        "docker", "build",
        "-f", str(dockerfile_path),
        "-t", tag,
        "."
    ], cwd=cwd, check=True)

    subprocess.run([
        "docker", "save",
        "-o", output_tar_path,
        tag
    ], check=True)

def main():
    parser = argparse.ArgumentParser(description="Dockify: package python script into docker image with exe")
    parser.add_argument("script_path", help="Path to your Python script")
    parser.add_argument("--requirements", "-r", help="Path to requirements.txt (optional)")
    parser.add_argument("--keep", "-k", help="Comma-separated files/folders to keep alongside exe (optional)", default="")
    parser.add_argument("--output", "-o", help="Output docker image tar path", default="dockify-image.tar")
    args = parser.parse_args()

    script_path = Path(args.script_path).name
    req_present = bool(args.requirements)
    keep_files = [k.strip() for k in args.keep.split(",")] if args.keep else []

    # Prepare temp build context folder
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        dockerfile_content = generate_dockerfile(script_path, req_present, keep_files)
        dockerfile_path = temp_path / "Dockerfile"
        dockerfile_path.write_text(dockerfile_content)

        # Build image and save as tar
        print("Building Docker image...")
        build_image_and_save(dockerfile_path, Path(script_path).stem, args.output)
        print(f"Docker image saved to {args.output}")

if __name__ == "__main__":
    main()
