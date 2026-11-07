"""Independent atomistic integration review: existing artifacts/mocks, NO MD."""
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
import zipfile

ROOT=Path('/workspace/scratch/48cb7a65c9c0/NanoLab-product-review')
sys.path.insert(0,str(ROOT/'scripts'))
from atomistic import api, budget
from atomistic.web import LocalApp, DEFAULT_CONFIG
EXAMPLE=ROOT/'examples/atomistic/runs/cu-emt-demo-r1-001'

class ProductFalsifiers(unittest.TestCase):
    def test_published_real_artifact_lineage_and_receipt(self):
        manifest=api.verify_run(EXAMPLE)
        source=manifest['subject']['git_head']
        tree=subprocess.check_output(['git','rev-parse',source+'^{tree}'],cwd=ROOT,text=True).strip()
        self.assertEqual(tree,manifest['subject']['git_tree'])
        self.assertFalse(manifest['subject']['dirty_tracked_files'])
        for name,record in manifest['subject']['adapter_sources'].items():
            before=subprocess.check_output(['git','show',source+':scripts/atomistic/'+name],cwd=ROOT)
            self.assertEqual({'sha256':hashlib.sha256(before).hexdigest(),'size_bytes':len(before)},record)
            self.assertEqual(api.digest(ROOT/'scripts/atomistic'/name),record)
        metrics=json.loads((EXAMPLE/'metrics.json').read_text());tr=json.loads((EXAMPLE/'trajectory.json').read_text())
        self.assertEqual(metrics['atom_count'],32);self.assertEqual(len(tr['frames']),11);self.assertEqual(len(metrics['series']),51)
        self.assertEqual(tr['frames'][-1]['step'],50)
        self.assertTrue(metrics['numerical_control']['passed']);self.assertTrue(metrics['relaxation']['converged'])
        self.assertLessEqual(metrics['relaxation']['final_potential_energy_ev'],metrics['relaxation']['initial_potential_energy_ev'])
        self.assertNotEqual(tr['frames'][0]['positions_angstrom'],tr['frames'][-1]['positions_angstrom'])

    def test_saved_zip_is_self_contained_and_verifiable(self):
        app=LocalApp('/tmp/unused-review-output')
        app.job={'run_id':'cu-emt-demo-r1-001','status':'completed','config':json.loads((EXAMPLE/'config.json').read_text())}
        app.result={name:json.loads((EXAMPLE/(name+'.json')).read_text()) for name in ('trajectory','metrics','manifest')}
        app.result['run_dir']=str(EXAMPLE)
        with tempfile.TemporaryDirectory() as tmp:
            with zipfile.ZipFile(io.BytesIO(app.export())) as archive:
                manifest=json.loads(archive.read('manifest.json'))
                missing=set(manifest['files'])-set(archive.namelist())
                mismatched=[name for name,expected in manifest['files'].items() if name in archive.namelist() and hashlib.sha256(archive.read(name)).hexdigest()!=expected['sha256']]
                print('export missing:',sorted(missing),'hash mismatch:',mismatched)
                archive.extractall(tmp)
            api.verify_run(tmp)

    def test_failed_run_id_cannot_be_reused_by_changing_output_root(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            with mock.patch.object(budget,'mission_directory',return_value=root/'ledger'), mock.patch.object(api,'_subject',return_value={}), mock.patch('atomistic.api.subprocess.Popen',side_effect=OSError('NO MD: mock launch failure')) as popen:
                with self.assertRaises(api.RunError):
                    api.run(DEFAULT_CONFIG,root/'first-output','reused-id')
                first_count=popen.call_count
                try:
                    api.run(DEFAULT_CONFIG,root/'second-output','reused-id')
                except (api.ValidationError,api.RunError):
                    pass
                ledger=json.loads((root/'ledger'/f'{budget.MISSION_ID}.json').read_text())
                print('same run ID: launch attempts',popen.call_count,'ledger rows',len(ledger['runs']))
                self.assertEqual(popen.call_count,first_count,'same failed ID launched again under another root')
                self.assertEqual(len(ledger['runs']),1)

    def test_budget_restart_block_and_ledger_shared_without_using_real_grant(self):
        with tempfile.TemporaryDirectory() as tmp, mock.patch.object(budget,'mission_directory',return_value=Path(tmp)):
            reservation=budget.reserve('/tmp/review-A',120,256*1024**2)
            with self.assertRaisesRegex(RuntimeError,'active reservation'):
                budget.reserve('/tmp/review-B',120,256*1024**2)
            budget.finish(reservation,'FAILED',0.01,100)
            for i in range(7):
                reservation=budget.reserve('/tmp/review-'+str(i),120,256*1024**2)
                budget.finish(reservation,'FAILED',0.01,100)
            with self.assertRaisesRegex(RuntimeError,'count exhausted'):
                budget.reserve('/tmp/review-new-root',120,256*1024**2)

if __name__=='__main__':
    unittest.main(verbosity=2)
