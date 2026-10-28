import contextlib
import importlib.machinery
import importlib.util
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / 'bin/jlab-workers'
loader = importlib.machinery.SourceFileLoader('workers', str(SCRIPT))
spec = importlib.util.spec_from_loader(loader.name, loader)
w = importlib.util.module_from_spec(spec)
loader.exec_module(w)


class WorkersTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.base = self.root / '.jlab-workers'
        self.base_patch = patch.object(w, 'BASE', self.base)
        self.base_patch.start()
        w.private(self.base)
        w.private(self.base / 'credentials')
        self.cfg = dict(hosts=['test-host'], binaries={'codex': '/bin/echo', 'claude': '/bin/echo'},
                        models={'codex': 'test/codex', 'claude': 'test/claude'})
        w.write_new(self.base / 'config.json', json.dumps(self.cfg))
        self.rec = dict(project='femtomind', worker='example', engine='codex', model='test/codex',
                        host='test-host', cwd=str(self.root), tmux='jlab-femtomind-example', slurm=False)

    def tearDown(self):
        self.base_patch.stop()
        self.tmp.cleanup()

    def key(self):
        path = self.base / 'credentials/femtomind.key'
        w.write_new(path, 'test-only-not-a-real-secret\n')
        return path

    def test_default_and_explicit_engines(self):
        self.assertEqual(w.parser().parse_args(['start', 'femtomind', 'x', '--cwd', '/tmp']).engine, 'codex')
        self.assertEqual(w.parser().parse_args(['start', 'quantom', 'x', '--cwd', '/tmp', '--engine', 'claude']).engine, 'claude')

    def test_no_funding_fallback(self):
        self.key()
        with self.assertRaises(SystemExit), patch.dict(os.environ, {'JLAB_LITELLM_API_KEY': 'wrong'}):
            w.get_key('quantom')

    def test_private_key_permissions_and_symlink(self):
        p = self.key()
        self.assertEqual(w.get_key('femtomind'), 'test-only-not-a-real-secret')
        p.chmod(0o644)
        with self.assertRaises(SystemExit):
            w.get_key('femtomind')
        p.unlink()
        p.symlink_to(self.base / 'config.json')
        with self.assertRaises(OSError):
            w.get_key('femtomind')

    def test_no_key_overwrite(self):
        p = self.key()
        with self.assertRaises(FileExistsError):
            w.write_new(p, 'replacement')
        self.assertEqual(w.get_key('femtomind'), 'test-only-not-a-real-secret')

    def test_noninteractive_enrollment_refused(self):
        with patch.object(w.sys.stdin, 'isatty', return_value=False), self.assertRaises(SystemExit):
            w.store_key('femtomind')

    def test_provider_routing_and_secret_not_in_argv(self):
        inherited = {'ANTHROPIC_API_KEY': 'stale', 'OPENAI_API_KEY': 'stale',
                     'CLAUDE_CODE_USE_BEDROCK': '1', 'CODEX_HOME': '/wrong',
                     'JLAB_LITELLM_API_KEY': 'stale'}
        with patch.dict(os.environ, inherited):
            for engine in ('codex', 'claude'):
                cmd, env, generated = w.launch_spec(dict(self.rec, engine=engine), self.cfg, 'test-secret', self.root)
                self.assertNotIn('test-secret', ' '.join(cmd) + generated[1])
                self.assertNotIn('stale', json.dumps(env))
                self.assertNotIn('OPENAI_API_KEY', env)
                if engine == 'codex':
                    self.assertEqual(env['JLAB_LITELLM_API_KEY'], 'test-secret')
                    self.assertIn('requires_openai_auth=false', ' '.join(cmd))
                    self.assertIn('enabled = false', generated[1])
                else:
                    self.assertEqual(env['ANTHROPIC_AUTH_TOKEN'], 'test-secret')
                    self.assertEqual(env['ANTHROPIC_BASE_URL'], w.ROOT)
                    self.assertNotIn('CLAUDE_CODE_USE_BEDROCK', env)
                    self.assertIn('--setting-sources', cmd)
                    self.assertNotIn('--dangerously-skip-permissions', cmd)

    def test_slurm_is_explicit_codex_opt_in(self):
        _, _, (_, config) = w.launch_spec(dict(self.rec, slurm=True), self.cfg, 'test', self.root)
        self.assertIn('munge.socket.2', config)
        self.assertIn('enabled = true', config)

    def test_scoped_log_grants_preserve_literal_alias_and_deny_broad_access(self):
        actual = self.root / 'actual_logs'
        userdir = actual / w.getpass.getuser()
        userdir.mkdir(parents=True)
        alias = self.root / 'farm_out'
        alias.symlink_to(actual)
        leaf = userdir / 'sidis_b002'
        leaf.mkdir(mode=0o700)
        rec = dict(self.rec, slurm=True)
        self.cfg['worker_log_directories'] = {rec['tmux']: [str(alias / userdir.name / leaf.name)]}
        with patch.object(w, 'FARM_OUT_ROOT', alias):
            _, _, (_, config) = w.launch_spec(rec, self.cfg, 'test', self.root)
            self.assertIn(json.dumps(str(alias / userdir.name / leaf.name)) + ' = "write"', config)
            self.assertIn(json.dumps(str(leaf.resolve())) + ' = "write"', config)
            self.assertNotIn(json.dumps(str(userdir)) + ' = "write"', config)
            self.assertIn(json.dumps(str(self.base / 'credentials')) + ' = "deny"', config)
            for bad in (str(alias), str(alias / userdir.name), str(alias / 'someone_else' / leaf.name), str(alias / userdir.name / 'missing')):
                self.cfg['worker_log_directories'][rec['tmux']] = [bad]
                with self.assertRaises(SystemExit):
                    w.log_directory_grants(rec, self.cfg)
            self.cfg['worker_log_directories'][rec['tmux']] = [str(alias / userdir.name / leaf.name)]
            leaf.chmod(0o777)
            with self.assertRaises(SystemExit):
                w.log_directory_grants(rec, self.cfg)
            leaf.chmod(0o700)
            with self.assertRaises(SystemExit):
                w.log_directory_grants(dict(rec, slurm=False), self.cfg)
            self.assertEqual(w.log_directory_grants(dict(rec, tmux='another-worker'), self.cfg), [])

    def test_sandbox_can_read_resolved_standalone_helpers(self):
        package = self.root / 'packages/v1/bin'
        package.mkdir(parents=True)
        exe = package / 'codex'
        exe.write_text('#!/bin/sh\nexit 0\n')
        exe.chmod(0o700)
        link = self.root / 'codex'
        link.symlink_to(exe)
        self.cfg['binaries']['codex'] = str(link)
        _, _, (_, config) = w.launch_spec(self.rec, self.cfg, 'test', self.root)
        self.assertIn(json.dumps(str(package.resolve())) + ' = "read"', config)
        self.assertIn(json.dumps(str(self.base / 'credentials')) + ' = "deny"', config)

    def test_host_and_engine_identity_cannot_change(self):
        self.key()
        w.write_new(w.identity_path(self.rec['tmux']), json.dumps(self.rec))
        args = w.parser().parse_args(['start', 'femtomind', 'example', '--cwd', str(self.root), '--engine', 'claude'])
        with patch.object(w, 'host_check', return_value='test-host'), patch.object(w.shutil, 'which', return_value='/bin/tmux'), patch.object(w, 'tmux') as tmux:
            with self.assertRaises(SystemExit):
                w.start(args)
            tmux.assert_not_called()
        with patch.object(w.socket, 'gethostname', return_value='unknown-host'), self.assertRaises(SystemExit):
            w.host_check(self.cfg)

    def test_argv_launch_preserves_spaces_without_shell(self):
        self.key()
        args = w.parser().parse_args(['start', 'femtomind', 'example', '--cwd', str(self.root)])
        with patch.object(w, 'host_check', return_value='test-host'), patch.object(w.shutil, 'which', return_value='/bin/tmux'), patch.object(w, 'tmux') as tmux, contextlib.redirect_stdout(io.StringIO()):
            w.start(args)
            argv = tmux.call_args.args
            end = argv.index(';')
            self.assertEqual(argv[end-3:end], (w.SCRIPT, '_run', 'jlab-femtomind-example'))
            self.assertEqual(argv[end+1:], ('set-option', '-w', '-t', '=jlab-femtomind-example:', 'remain-on-exit', 'on'))
            self.assertNotIn('JLAB_LITELLM_API_KEY', tmux.call_args.kwargs['env'])

    def test_usage_redaction_and_denial(self):
        for data, scope in [({'info': {'spend': 12.5, 'key': 'secret', 'token': 'secret'}}, 'key'),
                            ({'user_info': {'spend': 15, 'keys': ['secret']}}, 'user'),
                            ({'unavailable': True, 'http_status': 403}, 'key')]:
            out = io.StringIO()
            with patch.object(w, 'api_get', return_value=data), contextlib.redirect_stdout(out):
                w.usage('femtomind', scope)
            result = json.loads(out.getvalue())
            self.assertNotIn('secret', out.getvalue())
            if data.get('unavailable'):
                self.assertNotIn('spend', result)
                self.assertTrue(result['unavailable'])
            else:
                self.assertIsNone(result['max_budget'])

    def test_unknown_api_shape_is_not_zero(self):
        out = io.StringIO()
        with patch.object(w, 'api_get', return_value={'different_version': {}}), contextlib.redirect_stdout(out):
            w.usage('femtomind')
        self.assertTrue(json.loads(out.getvalue())['unavailable'])

    def test_status_distinguishes_remote_unknown_and_exited(self):
        w.write_new(w.identity_path(self.rec['tmux']), json.dumps(self.rec))
        other = dict(self.rec, host='other-host', worker='other', tmux='jlab-femtomind-other')
        w.write_new(w.identity_path(other['tmux']), json.dumps(other))
        for dead, expected in [(False, 1), (True, 0)]:
            out = io.StringIO()
            with patch.object(w, 'host_check', return_value='test-host'), patch.object(w, 'panes', return_value={self.rec['tmux']: [{'dead': dead}]}), contextlib.redirect_stdout(out):
                w.status()
            status = json.loads(out.getvalue())
            self.assertEqual(status['running_registered'], expected)
            self.assertEqual(status['workers'][1]['state'], 'other-host-unchecked')

    def test_ssh_no_auth_fallback_or_shell_injection(self):
        flags = w.ssh_args('ifarm2401')
        for flag in ('BatchMode=yes', 'ProxyCommand=false', 'StrictHostKeyChecking=yes', 'ForwardAgent=no'):
            self.assertIn(flag, flags)
        for host in ('-oProxyCommand=bad', 'host;echo bad', 'user@host'):
            with self.assertRaises(SystemExit):
                w.ssh_args(host)

    def test_internal_identity_path_validation(self):
        with self.assertRaises(SystemExit):
            w.identity_path('../../unexpected')

    def test_no_ssh_master_stops_dispatch(self):
        args = w.parser().parse_args(['remote', 'example-host', '--', 'status'])
        with patch.object(w.subprocess, 'run', side_effect=subprocess.CalledProcessError(255, 'ssh')), patch.object(w.subprocess, 'call') as call:
            with self.assertRaises(subprocess.CalledProcessError):
                w.remote(args)
            call.assert_not_called()

    def test_connect_requires_configured_socket(self):
        with patch.object(w.subprocess, 'run', return_value=subprocess.CompletedProcess([], 0, 'hostname host\ncontrolpath none\n')), patch.object(w.subprocess, 'call') as call:
            with self.assertRaises(SystemExit):
                w.connect('example-host')
            call.assert_not_called()

    @unittest.skipUnless(shutil.which('ssh'), 'OpenSSH required for template parsing')
    def test_single_login_alias_and_explicit_host_share_master(self):
        config = SCRIPT.parents[1] / 'examples/ssh_config'
        def effective(host, extra=()):
            result = subprocess.run(['ssh', '-F', str(config), *extra, '-G', host],
                                    capture_output=True, text=True, check=True)
            return dict(line.split(' ', 1) for line in result.stdout.splitlines())
        login = effective('ifarm')
        pinned = effective('jlab-ifarm2401')
        gateway = effective('jlab-gateway')
        self.assertEqual(login['hostname'], 'ifarm2401.jlab.org')
        self.assertEqual(login['proxyjump'], 'jlab-gateway')
        self.assertEqual(login['controlpath'], pinned['controlpath'])
        for cfg in (login, gateway):
            self.assertEqual(cfg['controlmaster'], 'auto')
            self.assertEqual(cfg['controlpersist'], '28800')
            self.assertNotEqual(cfg['batchmode'], 'yes')
        automated = effective('ifarm', ['-o', 'ProxyCommand=false', '-o', 'ProxyJump=none',
                                       '-S', login['controlpath']])
        self.assertEqual(automated['controlpath'], login['controlpath'])

    def test_dispatch_pins_original_socket_before_disabling_transport(self):
        args = w.parser().parse_args(['remote', 'ifarm', '--', 'status'])
        with patch.object(w, 'control_path', return_value='/private/original-socket'), patch.object(w.subprocess, 'run') as run, patch.object(w.subprocess, 'call', return_value=0) as call:
            with self.assertRaises(SystemExit) as outcome:
                w.remote(args)
            self.assertEqual(outcome.exception.code, 0)
            for argv in (run.call_args.args[0], call.call_args.args[0]):
                self.assertEqual(argv[argv.index('-S') + 1], '/private/original-socket')
                self.assertIn('ProxyCommand=false', argv)
                self.assertIn('BatchMode=yes', argv)

    def test_tmux_failure_is_not_zero_workers(self):
        with patch.object(w.subprocess, 'run', return_value=subprocess.CompletedProcess([], 1, '', 'Permission denied')):
            with self.assertRaises(SystemExit):
                w.panes()

    def test_http_error_body_is_withheld(self):
        self.key()
        exc = w.urllib.error.HTTPError('https://example.invalid', 403, 'denied', {}, io.BytesIO(b'secret-response'))
        with patch.object(w.urllib.request, 'build_opener') as opener:
            opener.return_value.open.side_effect = exc
            data = w.api_get('femtomind', '/key/info')
        self.assertEqual(data, {'unavailable': True, 'http_status': 403})

    def test_cli_init_smoke_without_real_home(self):
        env = dict(os.environ, HOME=str(self.root))
        # Use another home to avoid replacing this test's existing private config.
        home = self.root / 'home'
        home.mkdir()
        env['HOME'] = str(home)
        result = subprocess.run([w.sys.executable, str(SCRIPT), 'init'], env=env, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        cfg = json.loads((home / '.jlab-workers/config.json').read_text())
        self.assertIsNone(cfg['models']['claude'])
        again = subprocess.run([w.sys.executable, str(SCRIPT), 'init'], env=env, capture_output=True, text=True)
        self.assertNotEqual(again.returncode, 0)


if __name__ == '__main__':
    unittest.main()
