"""Deterministic regression tests. Never invokes model runtimes or external services."""
import contextlib
import hashlib
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

sys.path.insert(0, os.environ.get('SKILL_SCRIPTS', str(Path(__file__).resolve().parents[1] / 'scripts')))
import quick_validate as q
import eval_manifest as e
import package_skill as p
import init_skill as init

class Regression(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.skill = self.base / 'test-skill'
        self.skill.mkdir()
        self.write()
        self.output = self.base / 'dist'
    def write(self, name='test-skill', description='A useful test skill.', extra='', body='# Test\n'):
        (self.skill / 'SKILL.md').write_text(f'---\nname: {json.dumps(name)}\ndescription: {json.dumps(description)}\n{extra}---\n\n{body}')
    def package(self, output=None, **kwargs):
        with contextlib.redirect_stdout(io.StringIO()):
            return p.package_skill(self.skill, output or self.output, **kwargs)
    def manifest(self, **changes):
        data={'skill':'test-skill','version':'2.1.0','cases':[{'id':'a','type':'positive','prompt':'A test request','expected_skill':'test-skill','status':'NOT_RUN'}]}
        data.update(changes)
        path=self.base/'manifest.json'; path.write_text(json.dumps(data)); return path
    def test_valid_control(self): self.assertTrue(q.validate_skill(self.skill)[0])
    def test_empty_name(self):
        self.write(name=''); self.assertFalse(q.validate_skill(self.skill)[0])
    def test_empty_description(self):
        self.write(description='   '); self.assertFalse(q.validate_skill(self.skill)[0])
    def test_name_must_match(self):
        self.write(name='another-name'); self.assertFalse(q.validate_skill(self.skill)[0])
    def test_invalid_name(self):
        self.write(name='BAD_NAME'); self.assertFalse(q.validate_skill(self.skill)[0])
    def test_compatibility(self):
        self.write(extra='compatibility: Requires Python 3\n'); self.assertTrue(q.validate_skill(self.skill)[0])
    def test_metadata_types(self):
        self.write(extra='metadata: []\n'); self.assertFalse(q.validate_skill(self.skill)[0])
    def test_missing_local_reference(self):
        self.write(body='Read [contract](references/missing.md).'); self.assertFalse(q.validate_skill(self.skill)[0])
    def test_illustrative_link(self):
        self.write(body='```md\n[Example](imaginary.md)\n```\n'); self.assertTrue(q.validate_skill(self.skill)[0])
    def test_required_file(self):
        self.write(extra='metadata:\n  required-files: missing.txt\n'); self.assertFalse(q.validate_skill(self.skill)[0])
    def test_codex_profile_missing_ui(self): self.assertFalse(q.validate_skill(self.skill, 'codex')[0])
    def test_ui_present_malformed(self):
        (self.skill/'agents').mkdir(); (self.skill/'agents/openai.yaml').write_text('[]')
        self.assertFalse(q.validate_skill(self.skill)[0])
    def test_init_no_path_escape(self):
        root=self.base/'requested'; root.mkdir()
        with contextlib.redirect_stdout(io.StringIO()): result=init.init_skill('../outside',root)
        self.assertIsNone(result); self.assertFalse((self.base/'outside').exists())
    def test_init_reject_absolute(self):
        target=self.base/'outside'
        with contextlib.redirect_stdout(io.StringIO()): result=init.init_skill(str(target),self.base/'requested')
        self.assertIsNone(result); self.assertFalse(target.exists())
    def test_init_reject_bad_name(self):
        with contextlib.redirect_stdout(io.StringIO()): result=init.init_skill('BAD_NAME',self.base/'requested')
        self.assertIsNone(result); self.assertFalse((self.base/'requested').exists())
    def test_init_valid_preserved(self):
        with contextlib.redirect_stdout(io.StringIO()): result=init.init_skill('new-skill',self.base/'requested')
        self.assertTrue(result.is_dir()); self.assertTrue((result/'agents/openai.yaml').is_file())
    def test_manifest_plan(self): self.assertEqual(e.validate(self.skill,self.manifest()),1)
    def test_manifest_wrong_id(self):
        with self.assertRaises(ValueError): e.validate(self.skill,self.manifest(skill='other'))
    def test_manifest_array_diagnostic(self):
        path=self.base/'manifest.json'; path.write_text('[]')
        with self.assertRaises(ValueError): e.validate(self.skill,path)
    def test_manifest_unhashable_diagnostic(self):
        path=self.manifest(); data=json.loads(path.read_text()); data['cases'][0]['type']=[]; path.write_text(json.dumps(data))
        with self.assertRaises(ValueError): e.validate(self.skill,path)
    def test_manifest_missing_evidence(self):
        path=self.manifest(); data=json.loads(path.read_text()); data['cases'][0]['evidence']='absent.json'; path.write_text(json.dumps(data))
        with self.assertRaises(ValueError): e.validate(self.skill,path)
    def test_release_requires_actual_hash(self):
        with self.assertRaises(ValueError): e.validate(self.skill,self.manifest(),release=True)
    def test_release_blocks_not_run(self):
        path=self.manifest(skill_sha256=hashlib.sha256((self.skill/'SKILL.md').read_bytes()).hexdigest())
        with self.assertRaises(ValueError): e.validate(self.skill,path,release=True)
    def test_release_pass_with_evidence(self):
        (self.base/'trace.json').write_text('{"test":"fixture only"}')
        path=self.manifest(skill_sha256=hashlib.sha256((self.skill/'SKILL.md').read_bytes()).hexdigest())
        data=json.loads(path.read_text()); data['cases'][0].update(status='PASS',evidence='trace.json'); path.write_text(json.dumps(data))
        self.assertEqual(e.validate(self.skill,path,release=True),1)
    def test_package_valid(self):
        result=self.package(); self.assertTrue(result.is_file())
        with zipfile.ZipFile(result) as z: self.assertEqual(z.namelist(),['test-skill/SKILL.md'])
    def test_package_external_symlink(self):
        outside=self.base/'fake.txt'; outside.write_text('FAKE_NOT_A_SECRET')
        (self.skill/'link.txt').symlink_to(outside)
        self.assertIsNone(self.package()); self.assertFalse(self.output.exists())
    def test_package_dotenv_filter(self):
        (self.skill/'.env').write_text('FAKE_KEY=fake'); (self.skill/'.env.example').write_text('KEY=')
        result=self.package()
        with zipfile.ZipFile(result) as z:
            self.assertNotIn('test-skill/.env',z.namelist()); self.assertIn('test-skill/.env.example',z.namelist())
    def test_package_referenced_sensitive_file_blocks(self):
        (self.skill/'secret.pem').write_text('FAKE_NOT_A_KEY')
        self.write(body='Read [resource](secret.pem).')
        self.assertIsNone(self.package()); self.assertFalse(self.output.exists())
    def test_package_reject_output_inside_root(self):
        self.assertIsNone(self.package(self.skill)); self.assertFalse((self.skill/'skill.zip').exists())
    def test_package_excludes_prior_archive_cache(self):
        (self.skill/'skill.zip').write_bytes(b'old'); (self.skill/'__pycache__').mkdir(); (self.skill/'__pycache__/x.pyc').write_bytes(b'cache')
        result=self.package()
        with zipfile.ZipFile(result) as z: self.assertEqual(z.namelist(),['test-skill/SKILL.md'])
    def test_package_size_limit_preserves_old(self):
        self.output.mkdir(); old=self.output/'skill.zip'; old.write_bytes(b'old-package')
        with patch.object(p,'MAX_SKILL_ZIP_BYTES',1): self.assertIsNone(self.package())
        self.assertEqual(old.read_bytes(),b'old-package'); self.assertEqual(list(self.output.iterdir()),[old])
    def test_dry_run_no_writes(self):
        self.assertIsNotNone(self.package(dry_run=True)); self.assertFalse(self.output.exists())

if __name__=='__main__': unittest.main()
