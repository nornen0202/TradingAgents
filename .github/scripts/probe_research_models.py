import argparse,json,tempfile,subprocess,sys
from pathlib import Path
from tradingagents.llm_clients.codex_app_server import CodexAppServerSession
p=argparse.ArgumentParser()
p.add_argument('binary');p.add_argument('receipt')
a=p.parse_args()
result={'version':subprocess.check_output([a.binary,'--version'],text=True).strip(),'binary':a.binary,'turns':[]}
with tempfile.TemporaryDirectory() as d:
 s=CodexAppServerSession(codex_binary=a.binary,request_timeout=150,workspace_dir=d,cleanup_threads=True)
 try:
  s.start()
  assert s.account_read().get('account')
  models={m.get('model') for m in s.model_list()['data']}
  for model,effort in [('gpt-6.2-sol','medium'),('gpt-6.2-astra','high'),('gpt-6.2-sol','xhigh')]:
   assert model in models, (model,models)
   r=s.invoke(prompt='Use only the supplied test record. As of 2026-11-17, observations were 2026-11-16 value 17 and 2026-11-18 value 98. Return the last available value as of the cutoff.',model=model,reasoning_effort=effort,summary=None,personality=None,output_schema={'type':'object','properties':{'value':{'type':'integer'}},'required':['value'],'additionalProperties':False})
   assert json.loads(r.final_text)=={'value':17} and not any('rerout' in str(n.get('method','')).lower() for n in r.notifications)
   result['turns'].append(dict(model=model,effort=effort,observedValue=17,rerouteNotices=0))
   Path(a.receipt).write_text(json.dumps(result,indent=2),encoding='utf8')
 finally:s.close()
