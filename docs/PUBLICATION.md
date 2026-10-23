# English public releases

The original working repository retains historical records and must never be pushed as the public repository. The public repository is a separate clean history. The English source and fresh English calculation runs are copied without changing their evidence bytes. Quantum evidence has a documented derivative export that replaces machine paths and normalizes archive ownership; numerical fields, status, and binary densities are preserved and checked.

From the original research workspace, review `configs/publication.json`, then use a new staging directory:

```sh
.venv/bin/python tools/export_public.py --output dist/public-next
.venv/bin/python tools/export_public.py --audit dist/public-next
```

The export is deliberately fail-closed: it does not overwrite an existing directory, allow symlinks, accept changed evidence hashes, or silently include unlisted historical runs. Review the staged source, English interface screenshot, scientific claims, file list, and audit before publishing. Pattern scans are bounded checks, not a guarantee that any arbitrary file is safe to publish. Original quantum evidence remains in place; its transformation ledger is `runs/quantum/public-transformation.json` in the public tree.

For an update, clone the existing public repository into another new directory, synchronize only the reviewed export files while preserving the clone's `.git`, inspect the complete diff, commit in English, and push normally. Never replace public history or force-push. Re-run the audit on the clone after synchronization. Use an English release title and notes, and attach only an archive created from the audited public files with a SHA256 checksum.

In a clean public clone, `python tools/export_public.py --audit .` checks the saved release using only the Python standard library. Audit rejects temporary files and installation/test caches in the publication tree; use a clean checkout for this check. Creating the original derivative requires the canonical research workspace, so `--output` intentionally rejects an already-exported quantum dataset. Ordinary contributors can run new English campaigns and submit normal reviewed changes; this release tool is not needed to execute the platform.

After intentional public changes, regenerate a release through the canonical reviewed workflow. A hash mismatch after editing is expected; never rewrite a calculation manifest to disguise modified measurements. New measurements belong in new runs.
