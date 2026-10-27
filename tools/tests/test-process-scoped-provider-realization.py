#!/usr/bin/env python3
"""Hostile tests for the experimental process-scoped provider realization."""
from __future__ import annotations
from concurrent.futures import ThreadPoolExecutor
from contextlib import ExitStack, contextmanager
import hashlib, importlib.util, json, os, subprocess, sys, tempfile, threading, unittest
from pathlib import Path
from unittest import mock
ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))
import proto_ring_execution_custody as custody  # noqa: E402
import proto_ring_executable_binding as boundary  # noqa: E402
def load_checker():
    path = TOOLS / "check-proto-ring-provider.py"
    spec = importlib.util.spec_from_file_location("b1_provider_checker", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module
checker = load_checker()
EXPECTED = "4ae1a2a549d7dae8e4cce7f727b9bc5330f3823f"
OTHER = "b" * 40
class ProcessScopedProviderRealizationTests(unittest.TestCase):
    def setUp(self) -> None:
        boundary._clear_process_realizations_for_tests()
        self.temporary = tempfile.TemporaryDirectory()
        base = Path(self.temporary.name)
        self.root = base / "root"
        self.root.mkdir()
        self.binary = base / "proto-ring-compat"
        self.binary.write_bytes(b"exact-provider")
        self.binary.chmod(0o500)
        self.digest = hashlib.sha256(b"exact-provider").hexdigest()
        self.binding = boundary.ExecutableProviderBinding("fanilosendrison/proto-ring", EXPECTED)
        self.realization = boundary.Realization(self.binary, {"binary_sha256": self.digest})
    def tearDown(self) -> None:
        boundary._clear_process_realizations_for_tests()
        self.temporary.cleanup()
    @contextmanager
    def admitted_boundary(self, roots: tuple[Path, ...] | None = None):
        roots = roots or (self.root,)
        bindings = {root.resolve(): self.binding for root in roots}
        def load(root: Path):
            return bindings[root.resolve()]
        response = {"transport_version": 1, "operation": "adr-metadata.parse",
            "outcome": "result", "value": {"sha256": "0" * 64}}
        with ExitStack() as stack:
            load_mock = stack.enter_context(mock.patch.object(boundary, "load_executable_provider_binding", side_effect=load))
            realized_mock = stack.enter_context(mock.patch.object(boundary, "realized_provider", return_value=self.realization))
            identity_mock = stack.enter_context(mock.patch.object(boundary, "_verified_identity"))
            operation_mock = stack.enter_context(mock.patch.object(boundary, "_invoke_binary", return_value=response))
            yield bindings, load_mock, realized_mock, identity_mock, operation_mock
    def invoke(self, root: Path | None = None):
        return boundary.invoke_compat(root or self.root, "adr-metadata.parse", {"mode": "sha256", "bytes_hex": "00"})
    def admitted(self, root: Path | None = None):
        return boundary._PROCESS_REALIZATIONS[(root or self.root).resolve()]
    def assert_session_survives_external_mutation(self, mutation) -> None:
        with self.admitted_boundary() as (_bindings, _load, realized, _identity, op):
            self.invoke()
            snapshot = self.admitted().master_snapshot
            mutation()
            self.invoke()
            self.assertNotEqual(snapshot, op.call_args.args[0])
            self.assertEqual(1, realized.call_count)
    def assert_fresh_currentness_rejects(self) -> None:
        with mock.patch.object(checker, "load_executable_provider_binding", return_value=self.binding), mock.patch.object(checker, "realized_provider", side_effect=boundary.ProtoRingExecutableError("invalid external realization")):
            self.assertEqual(["invalid external realization"], checker.check(self.root))
    def test_B1_H01_authoritative_binding_changes_after_admission(self) -> None:
        with self.admitted_boundary() as (bindings, _load, _realized, _identity, op):
            self.invoke()
            op.reset_mock()
            bindings[self.root.resolve()] = boundary.ExecutableProviderBinding(
                "fanilosendrison/proto-ring", OTHER
            )
            with self.assertRaisesRegex(boundary.ProtoRingExecutableError, "binding changed"):
                self.invoke()
            op.assert_not_called()
    def test_B1_H02_manifest_malformed_before_admission(self) -> None:
        manifest = Path(self.temporary.name) / "realization.json"
        manifest.write_text("not-json")
        with self.assertRaises(boundary.ProtoRingExecutableError):
            boundary._read_manifest(manifest)
        self.assertEqual({}, boundary._PROCESS_REALIZATIONS)
    def test_B1_H03_manifest_changes_after_admission(self) -> None:
        manifest = Path(self.temporary.name) / "realization.json"
        manifest.write_text("before")
        self.assert_session_survives_external_mutation(
            lambda: manifest.write_text("malformed")
        )
        self.assert_fresh_currentness_rejects()
    def test_B1_H04_tracked_source_changes_after_admission(self) -> None:
        source = Path(self.temporary.name) / "tracked.rs"
        source.write_text("before")
        self.assert_session_survives_external_mutation(lambda: source.write_text("after"))
        self.assert_fresh_currentness_rejects()
    def test_B1_H05_untracked_source_after_admission(self) -> None:
        untracked = Path(self.temporary.name) / "untracked"
        self.assert_session_survives_external_mutation(lambda: untracked.write_text("x"))
        self.assert_fresh_currentness_rejects()
    def test_B1_H06_ignored_source_after_admission(self) -> None:
        ignored = Path(self.temporary.name) / "ignored"
        self.assert_session_survives_external_mutation(lambda: ignored.write_text("x"))
        self.assert_fresh_currentness_rejects()
    def test_B1_H07_cached_binary_replaced_after_admission(self) -> None:
        with self.admitted_boundary() as (_bindings, _load, realized, _identity, op):
            self.invoke()
            snapshot = self.admitted().master_snapshot
            self.binary.chmod(0o700)
            self.binary.write_bytes(b"replacement")
            self.invoke()
            self.assertEqual(b"exact-provider", snapshot.read_bytes())
            self.assertNotEqual(snapshot, op.call_args.args[0])
            self.assertEqual(1, realized.call_count)
        self.assert_fresh_currentness_rejects()
    def test_B1_H08_private_snapshot_byte_mutation(self) -> None:
        with self.admitted_boundary() as (_bindings, _load, _realized, _identity, op):
            self.invoke()
            snapshot = self.admitted().master_snapshot
            snapshot.chmod(0o700)
            snapshot.write_bytes(b"mutation")
            snapshot.chmod(0o500)
            op.reset_mock()
            with self.assertRaisesRegex(boundary.ProtoRingExecutableError, "digest"):
                self.invoke()
            op.assert_not_called()
    def test_B1_H09_private_snapshot_mode_mutation(self) -> None:
        with self.admitted_boundary() as (_bindings, _load, _realized, _identity, op):
            self.invoke()
            self.admitted().master_snapshot.chmod(0o700)
            op.reset_mock()
            with self.assertRaisesRegex(boundary.ProtoRingExecutableError, "mode"):
                self.invoke()
            op.assert_not_called()
    def test_B1_H10_private_snapshot_symlink_replacement(self) -> None:
        with self.admitted_boundary() as (_bindings, _load, _realized, _identity, op):
            self.invoke()
            snapshot = self.admitted().master_snapshot
            snapshot.unlink()
            snapshot.symlink_to(self.binary)
            op.reset_mock()
            with self.assertRaises(boundary.ProtoRingExecutableError):
                self.invoke()
            op.assert_not_called()
    def test_B1_H11_wrong_identity_rejects_admission(self) -> None:
        with mock.patch.object(boundary, "load_executable_provider_binding", return_value=self.binding), mock.patch.object(
            boundary, "realized_provider", return_value=self.realization
        ), mock.patch.object(
            boundary, "_verified_identity", side_effect=boundary.ProtoRingExecutableError("identity")
        ):
            with self.assertRaisesRegex(boundary.ProtoRingExecutableError, "identity"):
                self.invoke()
        self.assertEqual({}, boundary._PROCESS_REALIZATIONS)
    def test_B1_H12_wrong_digest_rejects_admission(self) -> None:
        wrong = boundary.Realization(self.binary, {"binary_sha256": "0" * 64})
        with mock.patch.object(boundary, "load_executable_provider_binding", return_value=self.binding), mock.patch.object(
            boundary, "realized_provider", return_value=wrong
        ):
            with self.assertRaisesRegex(boundary.ProtoRingExecutableError, "digest"):
                self.invoke()
        self.assertEqual({}, boundary._PROCESS_REALIZATIONS)
    def test_B1_H13_concurrent_external_replacement(self) -> None:
        replacement = Path(self.temporary.name) / "replacement"
        replacement.write_bytes(b"new-cache")
        with self.admitted_boundary() as (_bindings, _load, realized, _identity, op):
            self.invoke()
            snapshot = self.admitted().master_snapshot
            self.binary.chmod(0o700)
            replacement.replace(self.binary)
            self.invoke()
            self.assertEqual(b"exact-provider", snapshot.read_bytes())
            self.assertNotEqual(snapshot, op.call_args.args[0])
            self.assertEqual(1, realized.call_count)
        self.assert_fresh_currentness_rejects()
    def test_B1_H14_two_roots_have_distinct_realizations(self) -> None:
        second = Path(self.temporary.name) / "second-root"
        second.mkdir()
        with self.admitted_boundary((self.root, second)):
            self.invoke(self.root)
            self.invoke(second)
            first_snapshot = self.admitted(self.root).master_snapshot
            second_snapshot = self.admitted(second).master_snapshot
            self.assertNotEqual(first_snapshot, second_snapshot)
            self.assertEqual(2, len(boundary._PROCESS_REALIZATIONS))
    def test_B1_H15_binding_mutation_does_not_auto_admit(self) -> None:
        self.test_B1_H01_authoritative_binding_changes_after_admission()
        self.assertEqual(1, len(boundary._PROCESS_REALIZATIONS))
    def test_B1_H16_nested_python_admits_own_realization(self) -> None:
        self.invoke_real_provider()
        parent_snapshot = next(iter(boundary._PROCESS_REALIZATIONS.values())).master_snapshot
        script = (
            "import pathlib,sys;sys.path.insert(0,sys.argv[1]);"
            "import proto_ring_executable_binding as b;"
            "r=pathlib.Path(sys.argv[2]);"
            "b.invoke_compat_result(r,'adr-metadata.parse',{'mode':'sha256','bytes_hex':'00'});"
            "print(next(iter(b._PROCESS_REALIZATIONS.values())).master_snapshot)"
        )
        completed = subprocess.run(
            [sys.executable, "-c", script, str(TOOLS), str(ROOT)],
            check=True,
            capture_output=True,
            text=True,
            env=dict(os.environ),
        )
        self.assertNotEqual(str(parent_snapshot), completed.stdout.strip())
        self.assertTrue(parent_snapshot.exists())
    @unittest.skipUnless(hasattr(os, "fork"), "fork is unavailable")
    def test_B1_H17_fork_child_admits_own_realization(self) -> None:
        self.invoke_real_provider()
        parent_snapshot = next(iter(boundary._PROCESS_REALIZATIONS.values())).master_snapshot
        reader, writer = os.pipe()
        pid = os.fork()
        if pid == 0:
            os.close(reader)
            try:
                self.invoke_real_provider()
                child = next(iter(boundary._PROCESS_REALIZATIONS.values())).master_snapshot
                os.write(writer, f"{child}\n{parent_snapshot.exists()}".encode())
            finally:
                os._exit(0)
        os.close(writer)
        payload = os.read(reader, 4096).decode().splitlines()
        _, status = os.waitpid(pid, 0)
        self.assertEqual(0, status)
        self.assertNotEqual(str(parent_snapshot), payload[0])
        self.assertEqual("True", payload[1])
        self.assertTrue(parent_snapshot.exists())
        self.invoke_real_provider()
    def test_B1_H18_twenty_calls_use_one_admission(self) -> None:
        with self.admitted_boundary() as (_bindings, _load, realized, _identity, op), mock.patch.object(
            boundary, "execution_snapshot_from_private_master",
            wraps=custody.execution_snapshot_from_private_master,
        ) as capture:
            for _ in range(20):
                self.invoke()
            self.assertEqual(1, realized.call_count)
            self.assertEqual(20, op.call_count)
            self.assertEqual(20, capture.call_count)
    def test_B1_H19_master_path_replacement_rejects(self) -> None:
        with self.admitted_boundary() as (_b, _l, _r, _i, op):
            self.invoke(); master = self.admitted().master_snapshot; op.reset_mock()
            replacement = Path(self.temporary.name) / "replacement-master"
            replacement.write_bytes(b"replacement"); replacement.chmod(0o500)
            replacement.replace(master)
            with self.assertRaisesRegex(boundary.ProtoRingExecutableError, "digest"):
                self.invoke()
            op.assert_not_called()
    def test_B1_H20_master_mode_mutation_rejects(self) -> None:
        with self.admitted_boundary() as (_b, _l, _r, _i, op):
            self.invoke(); self.admitted().master_snapshot.chmod(0o700); op.reset_mock()
            with self.assertRaisesRegex(boundary.ProtoRingExecutableError, "master mode"):
                self.invoke()
            op.assert_not_called()
    def test_B1_H21_master_symlink_replacement_rejects(self) -> None:
        with self.admitted_boundary() as (_b, _l, _r, _i, op):
            self.invoke(); master = self.admitted().master_snapshot; master.unlink()
            master.symlink_to(self.binary); op.reset_mock()
            with self.assertRaisesRegex(boundary.ProtoRingExecutableError, "cannot be opened"):
                self.invoke()
            op.assert_not_called()
    def test_B1_H22_per_call_copy_digest_failure_rejects(self) -> None:
        with self.admitted_boundary() as (_b, _l, _r, _i, op):
            self.invoke(); admitted = self.admitted(); op.reset_mock()
            object.__setattr__(admitted, "expected_sha256", "0" * 64)
            with self.assertRaisesRegex(boundary.ProtoRingExecutableError, "digest"):
                self.invoke()
            op.assert_not_called()
    def test_B1_H23_master_path_is_never_executed(self) -> None:
        real_invoke = boundary._invoke_binary
        executed: list[Path] = []
        def run(argv, *, input, **_kwargs):
            request = json.loads(input)
            executed.append(Path(argv[0]))
            response = {"transport_version": 1, "operation": request["operation"],
                "outcome": "result", "value": {"sha256": "0" * 64}}
            return subprocess.CompletedProcess(argv, 0, (json.dumps(response) + "\n").encode(), b"")
        with self.admitted_boundary() as (_b, _l, _r, _i, op), mock.patch.object(
            boundary.subprocess, "run", side_effect=run
        ):
            op.side_effect = real_invoke
            for _ in range(5): self.invoke()
            master = self.admitted().master_snapshot
            self.assertEqual(0, sum(path == master for path in executed))
            self.assertEqual(5, len(set(executed)))
            self.assertTrue(all("ruu-proto-ring-call-execution-" in str(path.parent) for path in executed))
    def test_B1_H24_execution_snapshots_are_distinct_and_cleaned(self) -> None:
        with self.admitted_boundary() as (_b, _l, _r, _i, op):
            self.invoke(); self.invoke(); master = self.admitted().master_snapshot
            first, second = (call.args[0] for call in op.call_args_list)
            self.assertNotEqual(first, second); self.assertFalse(first.exists()); self.assertFalse(second.exists()); self.assertTrue(master.exists())
    def test_B1_H25_concurrent_threads_share_one_admission(self) -> None:
        with self.admitted_boundary() as (_b, _l, realized, _i, op):
            barrier = threading.Barrier(8)
            def worker(): barrier.wait(); return [self.invoke() for _ in range(5)]
            with ThreadPoolExecutor(max_workers=8) as pool:
                futures = [pool.submit(worker) for _ in range(8)]
                results = [value for future in futures for value in future.result()]
            master = self.admitted().master_snapshot
            paths = [call.args[0] for call in op.call_args_list]
            self.assertEqual(1, realized.call_count); self.assertEqual(40, len(paths))
            self.assertEqual(40, len(set(paths))); self.assertNotIn(master, paths)
            self.assertTrue(all(value == results[0] for value in results)); self.assertTrue(all(not path.exists() for path in paths)); self.assertTrue(master.exists())
    def memo_input(self, operation, value="00"):
        if operation == "adr-metadata.parse": return {"mode": "sha256", "bytes_hex": value}
        return {"mode": "require_string", "value": {"type": "string", "value": value}}
    def memo_response(self, operation, value=None):
        result = value or ({"sha256": "0" * 64} if operation.endswith("parse") else {"text": "x"})
        return {"transport_version": 1, "operation": operation, "outcome": "result", "value": result}
    def admit_reset(self, load, execute, operation):
        boundary._admitted_process_realization(self.root); load.reset_mock(); execute.reset_mock()
        execute.return_value = self.memo_response(operation)
    def memo_call(self, operation, value="00", root=None):
        return boundary.invoke_compat_result(root or self.root, operation, self.memo_input(operation, value))
    def test_B1_H26_parse_result_memoization(self) -> None:
        stdin=[]; real_invoke=boundary._invoke_binary
        def run(argv,*,input,**_kw): stdin.append(input); return subprocess.CompletedProcess(argv,0,(json.dumps(self.memo_response("adr-metadata.parse"))+"\n").encode(),b"")
        with self.admitted_boundary() as (_b, load, _r, _i, op), mock.patch.object(boundary, "verify_executable_snapshot", wraps=custody.verify_executable_snapshot) as verify, mock.patch.object(boundary.subprocess,"run",side_effect=run):
            self.admit_reset(load, op, "adr-metadata.parse"); op.side_effect=real_invoke; verify.reset_mock(); results=[self.memo_call("adr-metadata.parse") for _ in range(10)]
            key=boundary._compat_request_bytes("adr-metadata.parse",self.memo_input("adr-metadata.parse")); self.assertEqual((1,10,9,1),(op.call_count,load.call_count,verify.call_count,len(self.admitted().result_cache))); self.assertTrue(all(x==results[0] for x in results)); self.assertEqual([key],stdin)
    def test_B1_H27_validation_result_memoization(self) -> None:
        with self.admitted_boundary() as (_b, load, _r, _i, op):
            self.admit_reset(load, op, "adr-metadata.validation"); results=[self.memo_call("adr-metadata.validation") for _ in range(10)]
            self.assertEqual((1,10,1),(op.call_count,load.call_count,len(self.admitted().result_cache))); self.assertTrue(all(x==results[0] for x in results))
    def test_B1_H28_exact_request_bytes_distinguish_keys(self) -> None:
        with self.admitted_boundary() as (_b, load, _r, _i, op):
            self.admit_reset(load, op, "adr-metadata.parse")
            for value in ("00","01","00","01"): self.memo_call("adr-metadata.parse",value)
            self.assertEqual((2,2),(op.call_count,len(self.admitted().result_cache)))
    def test_B1_H29_non_allowlisted_operation_never_cached(self) -> None:
        identity={"source_repository":self.binding.repository,"source_commit":EXPECTED,"transport_version":1}
        with self.admitted_boundary() as (_b, load, _r, _i, op):
            self.admit_reset(load,op,"engine.identity"); op.return_value=self.memo_response("engine.identity",identity)
            for _ in range(2): boundary.invoke_compat_result(self.root,"engine.identity",{})
            self.assertEqual((2,0),(op.call_count,len(self.admitted().result_cache)))
    def test_B1_H30_controlled_failure_never_cached(self) -> None:
        failure={"transport_version":1,"operation":"adr-metadata.parse","outcome":"controlled_failure","error":{"category":"rejected","stage":None,"detail":"x"}}
        with self.admitted_boundary() as (_b, load, _r, _i, op):
            self.admit_reset(load,op,"adr-metadata.parse"); op.return_value=failure
            for _ in range(2):
                with self.assertRaises(boundary.ProtoRingControlledFailure): self.memo_call("adr-metadata.parse")
            self.assertEqual((2,0),(op.call_count,len(self.admitted().result_cache)))
    def test_B1_H31_binding_mutation_before_cache_hit(self) -> None:
        with self.admitted_boundary() as (bindings, load, _r, _i, op):
            self.admit_reset(load,op,"adr-metadata.parse"); self.memo_call("adr-metadata.parse"); op.reset_mock(); bindings[self.root.resolve()]=boundary.ExecutableProviderBinding("fanilosendrison/proto-ring",OTHER)
            with self.assertRaisesRegex(boundary.ProtoRingExecutableError,"binding changed"): self.memo_call("adr-metadata.parse")
            op.assert_not_called()
    def test_B1_H32_master_byte_mutation_before_cache_hit(self) -> None:
        self.assert_cache_hit_master_mutation("bytes")
    def test_B1_H33_master_mode_mutation_before_cache_hit(self) -> None:
        self.assert_cache_hit_master_mutation("mode")
    def test_B1_H34_master_symlink_before_cache_hit(self) -> None:
        self.assert_cache_hit_master_mutation("symlink")
    def assert_cache_hit_master_mutation(self, kind):
        with self.admitted_boundary() as (_b, load, _r, _i, op):
            self.admit_reset(load,op,"adr-metadata.parse"); self.memo_call("adr-metadata.parse"); master=self.admitted().master_snapshot; op.reset_mock()
            if kind=="bytes": master.chmod(0o700); master.write_bytes(b"bad"); master.chmod(0o500)
            elif kind=="mode": master.chmod(0o700)
            else: master.unlink(); master.symlink_to(self.binary)
            with self.assertRaises(boundary.ProtoRingExecutableError): self.memo_call("adr-metadata.parse")
            op.assert_not_called()
    def test_B1_H35_caller_mutation_cannot_poison_cache(self) -> None:
        with self.admitted_boundary() as (_b, load, _r, _i, op):
            self.admit_reset(load,op,"adr-metadata.parse"); first=self.memo_call("adr-metadata.parse"); original=dict(first); first["sha256"]="bad"; second=self.memo_call("adr-metadata.parse")
            self.assertEqual(original,second); self.assertNotEqual(first,second); self.assertEqual(1,op.call_count); self.admitted().result_cache[next(iter(self.admitted().result_cache))]=b"bad"
            with self.assertRaisesRegex(boundary.ProtoRingExecutableError,"internal memoized"): self.memo_call("adr-metadata.parse")
    def test_B1_H36_cache_is_root_local(self) -> None:
        second=Path(self.temporary.name)/"second"; second.mkdir()
        with self.admitted_boundary((self.root,second)) as (_b,_l,_r,_i,op):
            op.return_value=self.memo_response("adr-metadata.parse"); self.memo_call("adr-metadata.parse",root=self.root); self.memo_call("adr-metadata.parse",root=second)
            self.assertEqual(2,op.call_count); self.assertEqual([1,1],[len(self.admitted(x).result_cache) for x in (self.root,second)])
    def test_B1_H37_cache_does_not_cross_process_boundary(self) -> None:
        boundary.invoke_compat_result(ROOT,"adr-metadata.parse",{"mode":"sha256","bytes_hex":"00"}); parent=len(self.admitted(ROOT).result_cache)
        script="import pathlib,sys;sys.path.insert(0,sys.argv[1]);import proto_ring_executable_binding as b;r=pathlib.Path(sys.argv[2]);b.invoke_compat_result(r,'adr-metadata.parse',{'mode':'sha256','bytes_hex':'00'});print(len(next(iter(b._PROCESS_REALIZATIONS.values())).result_cache))"
        child=subprocess.run([sys.executable,"-c",script,str(TOOLS),str(ROOT)],check=True,capture_output=True,text=True,env=dict(os.environ)); self.assertEqual((1,"1"),(parent,child.stdout.strip()))
        if hasattr(os,"fork"): self.test_B1_H17_fork_child_admits_own_realization()
    def test_B1_H38_cache_lru_bound(self) -> None:
        with self.admitted_boundary() as (_b,_l,_r,_i,_op):
            admitted=boundary._admitted_process_realization(self.root)
            for i in range(4097): boundary._cache_store(admitted,str(i).encode(),b"v")
            self.assertEqual(4096,len(admitted.result_cache)); self.assertNotIn(b"0",admitted.result_cache); boundary._cache_get(admitted,b"1"); boundary._cache_store(admitted,b"4097",b"v"); self.assertNotIn(b"2",admitted.result_cache); self.assertIn(b"1",admitted.result_cache)
    def test_B1_H39_concurrent_identical_requests_are_safe(self) -> None:
        with self.admitted_boundary() as (_b,load,_r,_i,op):
            self.admit_reset(load,op,"adr-metadata.parse"); barrier=threading.Barrier(8)
            def worker(): barrier.wait(); return [self.memo_call("adr-metadata.parse") for _ in range(5)]
            with ThreadPoolExecutor(max_workers=8) as pool: results=[x for f in [pool.submit(worker) for _ in range(8)] for x in f.result()]
            calls=op.call_count; self.assertTrue(all(x==results[0] for x in results)); self.assertGreaterEqual(calls,1); self.assertEqual(1,len(self.admitted().result_cache)); self.memo_call("adr-metadata.parse"); self.assertEqual(calls,op.call_count)
    def invoke_real_provider(self) -> None:
        boundary.invoke_compat_result(ROOT, "adr-metadata.parse", {"mode": "sha256", "bytes_hex": "00"})
if __name__ == "__main__":
    unittest.main(verbosity=2)
