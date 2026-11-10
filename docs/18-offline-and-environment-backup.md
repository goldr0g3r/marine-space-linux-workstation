# Offline use and development-environment recovery

External source backups are essential, but they are only part of an engineering workstation restore. A container image, its writable layer, a bind-mounted source folder and a named volume are different things. Back up the layer that actually contains your work.

## What to preserve

| Data | Preservation method | Common omission |
|---|---|---|
| Git source and configuration | Commit/push plus external backup of unpushed changes | Untracked files and local configuration |
| Supplied ROS workspace | Back up the host `workspaces/ros` directory | It is ignored by this guide's Git repository |
| Known-good container image | `podman save`, with ID and checksum recorded | Images are not named-volume backups |
| Named container volume | Application-consistent export/backup | Backing up only the Containerfile |
| Distrobox working data | Back up custom home and explicit project paths; document installed tools | Custom home is still separate from image contents |
| Firmware / SDK | Release or commit, compiler identity, build/flash configuration | Reinstalling an unpinned latest SDK |
| ML project | Source, lockfile, dataset version, preprocessing and required weights | A model file without the code/data definition |
| ROS recording | Entire bag directory and experiment notes | Copying only one data file |

## Save a known-good image

Run the recording/replay or talker/listener exercise before archiving the image. Store exports outside the Git working tree and eventually on an external disk. This example initially writes under your home directory; that local copy will not survive erasing the Linux SSD.

```bash
mkdir -p "$HOME/Backups/robotics-images"
podman image inspect localhost/robotics-jazzy --format '{{.Id}}'
podman save --format oci-archive \
  --output "$HOME/Backups/robotics-images/robotics-jazzy.oci.tar" \
  localhost/robotics-jazzy
cd "$HOME/Backups/robotics-images"
sha256sum robotics-jazzy.oci.tar > robotics-jazzy.oci.tar.sha256
```

Use a dated filename for later versions if you want to retain several. Copy the archive, checksum and version record to the verified external backup destination. Image archives can contain anything installed or copied into the image; avoid embedding credentials during builds. [Podman save](https://docs.podman.io/en/latest/markdown/podman-save.1.html).

After reinstalling, from the directory containing the archive and checksum:

```bash
sha256sum -c robotics-jazzy.oci.tar.sha256
podman load --input robotics-jazzy.oci.tar
podman image inspect localhost/robotics-jazzy --format '{{.Id}}'
```

Compare the ID with the recorded value and re-run the lab. The host still needs a compatible architecture, kernel, runtime and—if used—GPU driver. An archived image does not preserve those. [Podman load](https://docs.podman.io/en/latest/markdown/podman-load.1.html).

## Protect named volumes separately

Inspect volumes and their users before touching them:

```bash
podman volume ls
podman ps -a --format '{{.Names}} {{.Mounts}}'
```

For a volume called `PROJECT_VOLUME`, stop its writers and use the application's own dump/backup procedure if it holds a database. Then, with the actual volume name substituted:

```bash
podman volume export PROJECT_VOLUME --output project-volume.tar
```

Test restoration into a **new empty volume**, leaving the original untouched:

```bash
podman volume create project-restore-check
podman volume import project-restore-check project-volume.tar
```

Verify representative content and ownership using the intended application/runtime. A tar export is not a consistent database backup while transactions are being written. [Volume export](https://docs.podman.io/en/latest/markdown/podman-volume-export.1.html), [volume import](https://docs.podman.io/en/latest/markdown/podman-volume-import.1.html).

The supplied ROS helper uses a bind mount, not a named volume. For that helper, back up the host workspace itself. Do not expect `podman save` or a container export to include mounted project data.

## Offline rehearsal before field work

- [ ] Pull/build the exact images you need while online and record their IDs.
- [ ] Populate required SDKs, Python environments, model files and simulator assets.
- [ ] Keep the complete project and small test data locally, including submodules or other declared dependencies.
- [ ] Store necessary device manuals, pin maps, wiring diagrams and recovery instructions locally.
- [ ] Start the actual workload without internet access; watch for first-run downloads, authentication requirements and missing assets.
- [ ] Verify enough free space for expected logs and sensor recordings.
- [ ] Test external backup access and a restore before leaving.

A cached image is useful, but rebuilding it can still need network access for package installation. Similarly, a Python lockfile identifies dependencies; it does not contain the wheels. For a small uv project with cached dependencies, `uv sync --locked --offline` is an explicit offline check. Run it in that project's directory and investigate failures before relying on it. [uv CLI reference](https://docs.astral.sh/uv/reference/cli/).

## Small recovery note for each project

Record the repository URL/commit, image ID or SDK version, Python lockfile, board revision, flash command, required devices, environment variables without secret values, data locations and the command that proves the project works. Store secret recovery material separately.

Once the restored project passes its original acceptance test, document the result in [the acceptance record](../templates/acceptance-record.md). An archive that has never been restored remains an unverified recovery plan.
