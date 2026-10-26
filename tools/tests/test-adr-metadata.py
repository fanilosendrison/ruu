#!/usr/bin/env python3
from adr_metadata_test_support import (
    Path, ROOT, adr_metadata, copy, copy_adr_fixture,
    disable_git_bound_validation, invoke_compat_result, load_structured_governance,
    shared_adr_metadata, shutil, tempfile, unittest,
)

class AdrMetadataTests(unittest.TestCase):
        def test_repository_passes_full_profile(self) -> None:
            self.assertEqual([], adr_metadata.collect_errors(ROOT))

        def test_shared_primitives_are_bound_to_native_provider(self) -> None:
            self.assertNotIn("proto-ring", (ROOT / "requirements.txt").read_text())
            bindings = {
                "AdrMetadataError": shared_adr_metadata.AdrMetadataError,
                "decision_body_bytes": shared_adr_metadata.decision_body_bytes,
                "load_json": shared_adr_metadata.load_json,
                "load_yaml": shared_adr_metadata.load_yaml,
                "parse_adr": shared_adr_metadata.parse_adr,
                "preserved_payload_bytes": shared_adr_metadata.preserved_payload_bytes,
                "repository_path": shared_adr_metadata.repository_path,
                "schema_errors": shared_adr_metadata.schema_errors,
                "sha256_hex": shared_adr_metadata.sha256_hex,
            }
            for name, shared in bindings.items():
                with self.subTest(name=name):
                    self.assertIs(getattr(adr_metadata, name), shared)

        def test_profile_path_resolution_delegates_to_native_provider(self) -> None:
            model = load_structured_governance(ROOT)[0]
            self.assertEqual(2, model["model_version"])
            self.assertEqual("proto-ring", model["provider"]["id"])
            self.assertEqual("shared_governance_provider", model["provider"]["binding"]["capability"])
            self.assertEqual("registry", model["provider"]["binding"]["route"])
            profile = model["capabilities"]["architecture_decisions"]["routes"]["profile"]
            self.assertEqual("docs/adr/adr-profile.yaml", profile["declared_path"])
            self.assertEqual(profile["declared_path"], profile["resolved_target"])
            self.assertIs(adr_metadata.configured_profile_path, shared_adr_metadata.configured_profile_path)
            self.assertEqual(
                (ROOT / "docs/adr/adr-profile.yaml").resolve(),
                adr_metadata.configured_profile_path(ROOT),
            )

        def test_adr_085_resolves_and_outside_same_id_is_ignored(self) -> None:
            expected = ROOT / "docs/adr/adr-085-require-proto-ring-for-applicable-generic-repository-governance.md"
            value = invoke_compat_result(
                ROOT,
                "canonical-adr.resolve",
                {"mode": "resolve_adr", "repository": str(ROOT), "adr_id": "ADR-085"},
            )
            self.assertEqual(expected.resolve(), (ROOT / value["relative_path"]).resolve())

            with tempfile.TemporaryDirectory() as temporary:
                fixture_root = copy_adr_fixture(temporary)
                outside = fixture_root / "outside/adr-085-impostor.md"
                outside.parent.mkdir(parents=True)
                shutil.copyfile(expected, outside)
                value = invoke_compat_result(
                    ROOT,
                    "canonical-adr.resolve",
                    {"mode": "resolve_adr", "repository": str(fixture_root), "adr_id": "ADR-085"},
                )
                self.assertEqual(expected.name, Path(value["relative_path"]).name)

        def test_calendar_schema_and_local_future_date_rule(self) -> None:
            adr_path = next((ROOT / "docs" / "adr").glob("adr-082-*.md"))
            metadata, _ = adr_metadata.parse_adr(adr_path)
            profile = adr_metadata.load_yaml(ROOT / "docs" / "adr" / "adr-profile.yaml")
            base = adr_metadata.load_json(ROOT / profile["canonical_schema"]["vendored_path"])
            overlay = adr_metadata.load_json(ROOT / profile["local_overlay"]["path"])

            for invalid_date in ("2026-13-01", "2026-04-31", "2025-02-29"):
                with self.subTest(date=invalid_date):
                    candidate = copy.deepcopy(metadata)
                    candidate["date"] = invalid_date
                    errors = adr_metadata.schema_errors(candidate, base, overlay)
                    self.assertTrue(any("date" in error for error in errors), errors)

            with tempfile.TemporaryDirectory() as temporary:
                fixture_root = copy_adr_fixture(temporary)
                disable_git_bound_validation(fixture_root)
                fixture_adr = next((fixture_root / "docs" / "adr").glob("adr-082-*.md"))
                fixture_adr.write_text(
                    fixture_adr.read_text(encoding="utf-8").replace(
                        'date: "2026-09-13"', 'date: "2099-01-01"'
                    ),
                    encoding="utf-8",
                )
                errors = adr_metadata.collect_errors(fixture_root)
                self.assertTrue(any("future date" in error for error in errors), errors)

        def test_body_digest_uses_exact_context_suffix(self) -> None:
            payload = b"# ADR-999: Example\n\n## Context\n\nExact body.\n"
            body = adr_metadata.decision_body_bytes(payload)
            self.assertEqual(b"## Context\n\nExact body.\n", body)
            self.assertEqual(
                "c9e5f9b055e1d65ed6fbb2c8ff85f9f2d2bdcbeeb087cbbef5b63837f12dadd4",
                adr_metadata.sha256_hex(body),
            )
            for invalid in (b"\xef\xbb\xbf" + payload, payload.replace(b"\n", b"\r\n")):
                with self.subTest(payload=invalid[:8]):
                    with self.assertRaises(adr_metadata.AdrMetadataError):
                        adr_metadata.decision_body_bytes(invalid)

        def test_unknown_and_stale_unstructured_entries_fail_closed(self) -> None:
            with tempfile.TemporaryDirectory() as temporary:
                fixture_root = copy_adr_fixture(temporary)
                disable_git_bound_validation(fixture_root)
                adr_directory = fixture_root / "docs" / "adr"
                existing_numbers = [
                    int(path.name.split("-", 2)[1])
                    for path in adr_directory.glob("adr-[0-9][0-9][0-9]-*.md")
                ]
                unknown_number = max(existing_numbers) + 1
                unknown_id = f"ADR-{unknown_number:03d}"
                unknown = adr_directory / f"adr-{unknown_number:03d}-unlisted-record.md"
                unknown.write_text(
                    f"# {unknown_id} — Unlisted record\n\n## Context\n\nLegacy body.\n",
                    encoding="utf-8",
                )
                errors = adr_metadata.collect_errors(fixture_root)
                self.assertTrue(
                    any(
                        f"{unknown_id} is unstructured but not allowlisted" in error
                        for error in errors
                    ),
                    errors,
                )

                unknown.unlink()
                profile_path = fixture_root / "docs" / "adr" / "adr-profile.yaml"
                profile = adr_metadata.load_yaml(profile_path)
                profile["legacy"]["unstructured"] = ["ADR-081"]
                profile_path.write_text(
                    adr_metadata.yaml.safe_dump(profile, sort_keys=False), encoding="utf-8"
                )
                legacy_path = next((fixture_root / "docs" / "adr").glob("adr-081-*.md"))
                legacy_path.unlink()
                errors = adr_metadata.collect_errors(fixture_root)
                self.assertTrue(
                    any("stale legacy unstructured entry ADR-081" in error for error in errors),
                    errors,
                )

        def test_overlay_constraints_cannot_be_bypassed(self) -> None:
            with tempfile.TemporaryDirectory() as temporary:
                fixture_root = copy_adr_fixture(temporary)
                disable_git_bound_validation(fixture_root)
                overlay = (
                    fixture_root
                    / "docs"
                    / "adr"
                    / "schemas"
                    / "ruu-architecture-decision-record.schema.json"
                )
                overlay.write_text(
                    '{\n  "$id": '
                    '"urn:fanilosendrison:ruu:architecture-decision-record:0.1.0"\n}\n',
                    encoding="utf-8",
                )
                adr_path = next((fixture_root / "docs" / "adr").glob("adr-082-*.md"))
                adr_path.write_text(
                    adr_path.read_text(encoding="utf-8").replace(
                        'domain: "ruu"', 'domain: "wrong-domain"'
                    ),
                    encoding="utf-8",
                )
                errors = adr_metadata.collect_errors(fixture_root)
                self.assertTrue(
                    any("local overlay domain constraint mismatch" in error for error in errors),
                    errors,
                )
                self.assertTrue(any("domain" in error for error in errors), errors)

        def test_misnamed_adr_candidate_is_not_ignored(self) -> None:
            with tempfile.TemporaryDirectory() as temporary:
                fixture_root = copy_adr_fixture(temporary)
                disable_git_bound_validation(fixture_root)
                adr_path = next((fixture_root / "docs" / "adr").glob("adr-082-*.md"))
                shutil.copyfile(adr_path, fixture_root / "docs" / "adr" / "wrong-name.md")
                errors = adr_metadata.collect_errors(fixture_root)
                self.assertTrue(
                    any("wrong-name.md" in error and "filename" in error for error in errors),
                    errors,
                )

        def test_fabricated_migration_baseline_is_rejected(self) -> None:
            with tempfile.TemporaryDirectory() as temporary:
                fixture_root = copy_adr_fixture(temporary)
                disable_git_bound_validation(fixture_root)
                profile_path = fixture_root / "docs" / "adr" / "adr-profile.yaml"
                profile = adr_metadata.load_yaml(profile_path)
                profile["migration_evidence"] = {
                    "path": "docs/adr/metadata-migration-evidence.yaml",
                    "required": True,
                    "baseline_commit": "0" * 40,
                    "ids": ["ADR-082"],
                }
                profile_path.write_text(
                    adr_metadata.yaml.safe_dump(profile, sort_keys=False), encoding="utf-8"
                )
                adr_path = next((fixture_root / "docs" / "adr").glob("adr-082-*.md"))
                _, body = adr_metadata.parse_adr(adr_path)
                digest = adr_metadata.sha256_hex(body)
                payload = adr_metadata.preserved_payload_bytes(adr_path.read_bytes())
                evidence = {
                    "schema_version": 1,
                    "profile_version": "0.1.0",
                    "baseline_commit": "0" * 40,
                    "records": [
                        {
                            "id": "ADR-082",
                            "path": adr_path.relative_to(fixture_root).as_posix(),
                            "baseline_file_sha256": adr_metadata.sha256_hex(payload),
                            "baseline_payload_sha256": adr_metadata.sha256_hex(payload),
                            "migrated_payload_sha256": adr_metadata.sha256_hex(payload),
                            "before_decision_body_sha256": digest,
                            "after_decision_body_sha256": digest,
                        }
                    ],
                }
                (fixture_root / "docs" / "adr" / "metadata-migration-evidence.yaml").write_text(
                    adr_metadata.yaml.safe_dump(evidence, sort_keys=False), encoding="utf-8"
                )
                errors = adr_metadata.collect_errors(fixture_root)
                self.assertTrue(any("baseline commit" in error for error in errors), errors)


from adr_metadata_migration_tests import AdrMetadataMigrationTests

if __name__ == "__main__":
    unittest.main(verbosity=2)
