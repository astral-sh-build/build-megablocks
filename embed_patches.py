# /// script
# requires-python = ">=3.12"
# ///
"""Embed patch files into a wheel's .dist-info/patches/ directory."""

import argparse
import base64
import csv
import hashlib
import io
import os
import zipfile
from pathlib import Path


def rewrite_zip_with_bytes(
    src_zip_path: str | os.PathLike[str],
    dst_zip_path: str | os.PathLike[str],
    replacements: dict[str, str],
    additions: dict[str, str] | None = None,
) -> None:
    """Rewrite a zip file, replacing and adding files.

    Args:
        src_zip_path: Path to the source zip file.
        dst_zip_path: Path to the destination zip file.
        replacements: Map of filename -> content for files to replace.
        additions: Map of filename -> content for files to add.
    """
    with (
        zipfile.ZipFile(src_zip_path, "r") as zin,
        zipfile.ZipFile(dst_zip_path, "w") as zout,
    ):
        for original_info in zin.infolist():
            compress_type = original_info.compress_type

            if data := replacements.get(original_info.filename):
                # Write out the updated data.
                zout.writestr(
                    original_info,
                    data,
                    compress_type=compress_type,
                )
            else:
                # Read the existing data.
                data = zin.read(original_info.filename)

                # Copy over the existing data.
                zout.writestr(original_info, data, compress_type=compress_type)

        # Add new files.
        if additions:
            for filename, content in additions.items():
                zout.writestr(filename, content, compress_type=zipfile.ZIP_DEFLATED)


def get_dist_info_dir(wheel: zipfile.ZipFile) -> str:
    """Find the .dist-info directory in a wheel."""
    for name in wheel.namelist():
        if name.endswith(".dist-info/METADATA"):
            return name.rsplit("/", 1)[0]
    raise ValueError("Could not find .dist-info directory in wheel")


def compute_hash(content: bytes) -> str:
    """Compute the hash for a RECORD entry."""
    digest = hashlib.sha256(content).digest()
    return f"sha256={base64.urlsafe_b64encode(digest).rstrip(b'=').decode()}"


def add_record_entry(
    writer: csv.writer,
    additions: dict[str, str],
    path: str,
    content: str,
) -> None:
    """Add a file to additions and write its RECORD entry."""
    content_bytes = content.encode("utf-8")
    additions[path] = content
    writer.writerow([path, compute_hash(content_bytes), str(len(content_bytes))])


def embed_patches(
    wheel_path: Path,
    patches_dir: Path,
    upstream_repo: str | None = None,
    upstream_ref: str | None = None,
) -> None:
    """Embed patches into a wheel file."""
    # Find all .patch files.
    patch_files = sorted(patches_dir.glob("*.patch"))
    if not patch_files:
        print(f"No patch files found in {patches_dir}")
        return

    # Determine paths within the wheel.
    with zipfile.ZipFile(wheel_path, "r") as wheel:
        dist_info = get_dist_info_dir(wheel)
        record_path = f"{dist_info}/RECORD"

        # Read existing RECORD.
        record_content = wheel.read(record_path).decode("utf-8")
        record_lines = record_content.splitlines()

        # Build new RECORD entries and additions.
        record_out = io.StringIO()
        reader = csv.reader(record_lines)
        writer = csv.writer(record_out)
        for row in reader:
            if row and row[0] != record_path:  # Skip RECORD itself (added at end).
                writer.writerow(row)

        additions = {}

        # Add SOURCE file with provenance info.
        if upstream_repo or upstream_ref:
            source_content = ""
            if upstream_repo:
                source_content += f"repository: {upstream_repo}\n"
            if upstream_ref:
                source_content += f"ref: {upstream_ref}\n"
            add_record_entry(
                writer, additions, f"{dist_info}/patches/SOURCE", source_content
            )

        # Add patch files.
        for patch_file in patch_files:
            patch_content = patch_file.read_text()
            add_record_entry(
                writer, additions, f"{dist_info}/patches/{patch_file.name}", patch_content
            )

        writer.writerow([record_path, "", ""])  # RECORD has no hash.
        new_record = record_out.getvalue()

    # Rewrite the wheel.
    temp_path = wheel_path.with_suffix(".tmp")
    rewrite_zip_with_bytes(
        wheel_path,
        temp_path,
        replacements={record_path: new_record},
        additions=additions,
    )

    # Replace original wheel.
    temp_path.replace(wheel_path)
    print(f"Embedded {len(patch_files)} patch(es) into {wheel_path}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Embed patch files into a wheel's .dist-info/patches/ directory."
    )
    parser.add_argument("wheel", type=Path, help="Path to the wheel file")
    parser.add_argument("patches_dir", type=Path, help="Path to the patches directory")
    parser.add_argument(
        "--upstream-repo", type=str, help="Upstream repository URL"
    )
    parser.add_argument(
        "--upstream-ref", type=str, help="Upstream git ref (commit, tag, or branch)"
    )
    args = parser.parse_args()

    if not args.wheel.exists():
        parser.error(f"Wheel not found: {args.wheel}")

    if not args.patches_dir.exists():
        parser.error(f"Patches directory not found: {args.patches_dir}")

    embed_patches(
        args.wheel,
        args.patches_dir,
        upstream_repo=args.upstream_repo,
        upstream_ref=args.upstream_ref,
    )


if __name__ == "__main__":
    main()
