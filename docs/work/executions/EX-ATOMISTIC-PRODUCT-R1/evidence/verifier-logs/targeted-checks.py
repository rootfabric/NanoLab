from atomistic.api import run,read_config,RunError,verify_run
from atomistic.web import LocalApp
from pathlib import Path
from unittest import mock
from html.parser import HTMLParser
from decimal import Decimal
import tempfile,json,zipfile,io,hashlib,subprocess
result={'subject':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'actual_calculator_runs':0}
with tempfile.TemporaryDirectory() as temp:
 root=Path(temp)
 with mock.patch('atomistic.api._subject',return_value={}),mock.patch('atomistic.budget.mission_directory',return_value=root/'ledger'),mock.patch('atomistic.api.subprocess.Popen',side_effect=OSError('verifier injected launch failure')) as launch:
  for output in [root/'first',root/'second']:
   try:run(read_config('examples/atomistic/cu-demo.json'),output,'verifier-reuse-probe')
   except RunError as exc:print(str(exc))
  ledger=json.loads((root/'ledger/WO-ATOMISTIC-PRODUCT-R1.json').read_text())
  result['run_id_reuse']={'mock_launch_attempts':launch.call_count,'ledger_rows':len(ledger['runs']),'second_manifest_failure':json.loads((root/'second/verifier-reuse-probe/manifest.json').read_text())['failure_class']}
  assert launch.call_count==1 and len(ledger['runs'])==1
source=Path('examples/atomistic/runs/cu-emt-demo-r1-001').absolute();app=LocalApp(source.parent)
app.job={'status':'completed','config':read_config(source/'config.json'),'run_id':source.name}
app.result={name:json.loads((source/(name+'.json')).read_text()) for name in ['trajectory','metrics','manifest']};app.result['run_dir']=str(source)
with zipfile.ZipFile(io.BytesIO(app.export())) as archive,tempfile.TemporaryDirectory() as temp:
 names=archive.namelist();assert len(names)==11
 assert all(archive.read(name)==(source/name).read_bytes() for name in names)
 archive.extractall(temp);verify_run(temp)
 result['zip_export']={'members':names,'all_original_bytes_match':True,'extracted_verify_run':'PASS'}
class Inputs(HTMLParser):
 def handle_starttag(self,tag,attrs):
  values=dict(attrs)
  if tag=='input' and values.get('id')=='friction':self.friction=values
parser=Inputs();parser.feed(Path('scripts/atomistic/static/index.html').read_text());attrs=parser.friction
valid=(Decimal(attrs['value'])-Decimal(attrs['min']))%Decimal(attrs['step'])==0
result['friction']={'attributes':attrs,'decimal_html_step_valid':valid};assert valid
print(json.dumps(result,indent=2))
