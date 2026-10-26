"""Migration and rendering tests for Ruu ADR metadata."""
from adr_metadata_test_support import (
    Path, ROOT, adr_metadata, copy_adr_fixture, disable_git_bound_validation, mock,
    shutil, structured_adr_bytes, subprocess, tempfile, unittest,
    write_repository_governance,
)

import adr_metadata_migration
import adr_metadata_rendering

class AdrMetadataMigrationTests(unittest.TestCase):
        def test_migration_evidence_preserves_exact_h1_to_eof_payload(self) -> None:
            with tempfile.TemporaryDirectory() as temporary:
                fixture_root = copy_adr_fixture(temporary)
                disable_git_bound_validation(fixture_root)
                profile_path = fixture_root / "docs" / "adr" / "adr-profile.yaml"
                profile = adr_metadata.load_yaml(profile_path)
                baseline = "1" * 40
                profile["migration_evidence"] = {
                    "path": "docs/adr/metadata-migration-evidence.yaml",
                    "required": True,
                    "baseline_commit": baseline,
                    "ids": ["ADR-082"],
                }
                profile_path.write_text(
                    adr_metadata.yaml.safe_dump(profile, sort_keys=False), encoding="utf-8"
                )
                adr_path = next((fixture_root / "docs" / "adr").glob("adr-082-*.md"))
                current_data = adr_path.read_bytes()
                baseline_payload = adr_metadata.preserved_payload_bytes(current_data)
                body = adr_metadata.decision_body_bytes(baseline_payload)
                digest = adr_metadata.sha256_hex(body)
                payload_digest = adr_metadata.sha256_hex(baseline_payload)
                evidence = {
                    "schema_version": 1,
                    "profile_version": "0.1.0",
                    "baseline_commit": baseline,
                    "records": [
                        {
                            "id": "ADR-082",
                            "path": adr_path.relative_to(fixture_root).as_posix(),
                            "baseline_file_sha256": payload_digest,
                            "baseline_payload_sha256": payload_digest,
                            "migrated_payload_sha256": payload_digest,
                            "before_decision_body_sha256": digest,
                            "after_decision_body_sha256": digest,
                        }
                    ],
                }
                (fixture_root / "docs" / "adr" / "metadata-migration-evidence.yaml").write_text(
                    adr_metadata.yaml.safe_dump(evidence, sort_keys=False), encoding="utf-8"
                )
                successful_git = mock.Mock(returncode=0, stderr=b"")
                with mock.patch.object(
                    adr_metadata_migration,
                    "_git_baseline_blob",
                    return_value=baseline_payload,
                ), mock.patch.object(
                    adr_metadata_migration,
                    "_baseline_ancestor_result",
                    return_value=successful_git,
                ):
                    self.assertEqual([], adr_metadata.collect_errors(fixture_root))

                h1 = b"# ADR-082 \xe2\x80\x94 Adopt validated OKF Architecture Decision Record metadata\n"
                adr_path.write_bytes(
                    current_data.replace(
                        h1, h1 + b"\n- **Historical metadata:** changed\n", 1
                    )
                )
                with mock.patch.object(
                    adr_metadata_migration,
                    "_git_baseline_blob",
                    return_value=baseline_payload,
                ), mock.patch.object(
                    adr_metadata_migration,
                    "_baseline_ancestor_result",
                    return_value=successful_git,
                ):
                    errors = adr_metadata.collect_errors(fixture_root)
                self.assertTrue(
                    any("H1-to-EOF payload differs from baseline" in error for error in errors),
                    errors,
                )

        def test_real_git_migration_replaces_partial_frontmatter_only(self) -> None:
            with tempfile.TemporaryDirectory() as temporary:
                fixture_root = Path(temporary)
                write_repository_governance(fixture_root)
                adr_directory = fixture_root / "docs" / "adr"
                schema_directory = adr_directory / "schemas"
                schema_directory.mkdir(parents=True)
                shutil.copyfile(
                    ROOT / "docs" / "adr" / "schemas" / "architecture-decision-record.schema.json",
                    schema_directory / "architecture-decision-record.schema.json",
                )
                shutil.copyfile(
                    ROOT / "docs" / "adr" / "schemas" / "ruu-architecture-decision-record.schema.json",
                    schema_directory / "ruu-architecture-decision-record.schema.json",
                )

                profile = adr_metadata.load_yaml(ROOT / "docs" / "adr" / "adr-profile.yaml")
                profile["legacy"] = {"unstructured": ["ADR-001"], "null_dates": []}
                profile["generated_index"]["required"] = False
                profile["migration_evidence"] = {
                    "path": "docs/adr/metadata-migration-evidence.yaml",
                    "required": False,
                    "baseline_commit": None,
                    "ids": [],
                }
                profile["repository"]["preferred_h1_from"] = 2
                profile_path = adr_directory / "adr-profile.yaml"
                profile_path.write_text(
                    adr_metadata.yaml.safe_dump(profile, sort_keys=False), encoding="utf-8"
                )

                legacy_context = b"## Context\n\nLegacy decision body.\n"
                legacy_payload = (
                    b"# ADR-001: Legacy partial metadata\n\n"
                    b"- **Status:** Accepted -- historical presentation\n\n"
                    + legacy_context
                )
                legacy_frontmatter = (
                    b"---\n"
                    b'okf_version: "1.0"\n'
                    b'kind: "KnowledgeAsset"\n'
                    b'asset_type: "architecture-decision-record"\n'
                    b'domain: "ruu"\n'
                    b'severity: "normative"\n'
                    b'name: "Legacy partial metadata"\n'
                    b'status: "accepted"\n'
                    b"---\n\n"
                )
                legacy_path = adr_directory / "adr-001-legacy-partial-metadata.md"
                legacy_path.write_bytes(legacy_frontmatter + legacy_payload)
                second_path = adr_directory / "adr-002-governance.md"
                second_path.write_bytes(
                    structured_adr_bytes(
                        "ADR-002",
                        "Governance",
                        " — ",
                        b"## Context\n\nGovernance body.\n",
                    )
                )

                subprocess.run(["git", "init", "-q", str(fixture_root)], check=True)
                subprocess.run(
                    ["git", "-C", str(fixture_root), "config", "user.name", "Test"],
                    check=True,
                )
                subprocess.run(
                    ["git", "-C", str(fixture_root), "config", "user.email", "test@example.invalid"],
                    check=True,
                )
                subprocess.run(
                    ["git", "-C", str(fixture_root), "add", "."], check=True
                )
                subprocess.run(
                    ["git", "-C", str(fixture_root), "commit", "-qm", "baseline"],
                    check=True,
                )
                baseline = subprocess.run(
                    ["git", "-C", str(fixture_root), "rev-parse", "HEAD"],
                    check=True,
                    capture_output=True,
                    text=True,
                ).stdout.strip()

                legacy_path.write_bytes(
                    structured_adr_bytes(
                        "ADR-001", "Legacy partial metadata", ": ", legacy_context
                    ).replace(
                        b"# ADR-001: Legacy partial metadata\n\n" + legacy_context,
                        legacy_payload,
                    )
                )
                profile["legacy"]["unstructured"] = []
                profile["migration_evidence"] = {
                    "path": "docs/adr/metadata-migration-evidence.yaml",
                    "required": True,
                    "baseline_commit": baseline,
                    "ids": ["ADR-001"],
                }
                profile_path.write_text(
                    adr_metadata.yaml.safe_dump(profile, sort_keys=False), encoding="utf-8"
                )

                baseline_bytes = subprocess.run(
                    [
                        "git",
                        "-C",
                        str(fixture_root),
                        "show",
                        f"{baseline}:docs/adr/{legacy_path.name}",
                    ],
                    check=True,
                    capture_output=True,
                ).stdout
                baseline_payload = adr_metadata.preserved_payload_bytes(baseline_bytes)
                migrated_payload = adr_metadata.preserved_payload_bytes(legacy_path.read_bytes())
                self.assertEqual(legacy_payload, baseline_payload)
                self.assertEqual(baseline_payload, migrated_payload)
                self.assertNotEqual(
                    adr_metadata.sha256_hex(baseline_bytes),
                    adr_metadata.sha256_hex(baseline_payload),
                )
                evidence = {
                    "schema_version": 1,
                    "profile_version": "0.1.0",
                    "baseline_commit": baseline,
                    "records": [
                        {
                            "id": "ADR-001",
                            "path": f"docs/adr/{legacy_path.name}",
                            "baseline_file_sha256": adr_metadata.sha256_hex(baseline_bytes),
                            "baseline_payload_sha256": adr_metadata.sha256_hex(baseline_payload),
                            "migrated_payload_sha256": adr_metadata.sha256_hex(migrated_payload),
                            "before_decision_body_sha256": adr_metadata.sha256_hex(legacy_context),
                            "after_decision_body_sha256": adr_metadata.sha256_hex(legacy_context),
                        }
                    ],
                }
                (adr_directory / "metadata-migration-evidence.yaml").write_text(
                    adr_metadata.yaml.safe_dump(evidence, sort_keys=False), encoding="utf-8"
                )

                self.assertEqual([], adr_metadata.collect_errors(fixture_root))

        def test_renderer_projects_outgoing_and_derived_incoming_relations(self) -> None:
            records = [
                {
                    "id": "ADR-001",
                    "number": 1,
                    "path": Path("docs/adr/adr-001-first.md"),
                    "metadata": {
                        "name": "First",
                        "status": "accepted",
                        "date": "2026-09-10",
                        "relation_completeness": "legacy-partial",
                        "governs": [],
                        "relations": {
                            "clarifies": [],
                            "amends": [],
                            "supersedes": [],
                            "confirms": [],
                        },
                    },
                },
                {
                    "id": "ADR-002",
                    "number": 2,
                    "path": Path("docs/adr/adr-002-second.md"),
                    "metadata": {
                        "name": "Second",
                        "status": "accepted",
                        "date": "2026-09-10",
                        "relation_completeness": "complete",
                        "governs": [],
                        "relations": {
                            "clarifies": ["ADR-001"],
                            "amends": [],
                            "supersedes": [],
                            "confirms": [],
                        },
                    },
                },
            ]
            profile = {"repository": {"display_name": "Ruu", "domain": "ruu"}}
            with mock.patch.object(
                adr_metadata_rendering,
                "_structured_records",
                return_value=(profile, records),
            ):
                rendered = adr_metadata.render_index(ROOT)
            self.assertIn("| [ADR-002](adr-002-second.md) | clarifies |", rendered)
            self.assertIn("| [ADR-001](adr-001-first.md) | clarified by |", rendered)
            self.assertIn("relation graph is incomplete", rendered)

        def test_stale_generated_index_is_rejected(self) -> None:
            with tempfile.TemporaryDirectory() as temporary:
                fixture_root = copy_adr_fixture(temporary)
                disable_git_bound_validation(fixture_root)
                profile_path = fixture_root / "docs" / "adr" / "adr-profile.yaml"
                profile = adr_metadata.load_yaml(profile_path)
                profile["generated_index"]["required"] = True
                profile_path.write_text(
                    adr_metadata.yaml.safe_dump(profile, sort_keys=False), encoding="utf-8"
                )
                (fixture_root / "docs" / "adr" / "index.md").write_text(
                    "stale\n", encoding="utf-8"
                )
                with mock.patch.object(
                    adr_metadata, "render_index", return_value="expected\n"
                ):
                    errors = adr_metadata.collect_errors(fixture_root)
                self.assertTrue(any("generated ADR index is stale" in error for error in errors), errors)

        def test_body_hash_mismatch_is_rejected(self) -> None:
            with tempfile.TemporaryDirectory() as temporary:
                fixture_root = copy_adr_fixture(temporary)
                disable_git_bound_validation(fixture_root)
                adr_path = next((fixture_root / "docs" / "adr").glob("adr-082-*.md"))
                text = adr_path.read_text(encoding="utf-8")
                text = text.replace(
                    'decision_body_sha256: "e403c6a5e83e60e22e80485466e7204705277e21e3da9c968e6c9c6765bbf8bb"',
                    'decision_body_sha256: "0000000000000000000000000000000000000000000000000000000000000000"',
                )
                adr_path.write_text(text, encoding="utf-8")
                errors = adr_metadata.collect_errors(fixture_root)
                self.assertTrue(any("decision_body_sha256 mismatch" in error for error in errors), errors)

