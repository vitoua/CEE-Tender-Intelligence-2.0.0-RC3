import os,tempfile,unittest,asyncio,json
os.environ['DATA_DIR']=tempfile.mkdtemp()
from unittest.mock import patch
from fastapi.testclient import TestClient
from app import core,engine,apify_settings as cfg
from app.main import app
from app.connectors import ekap
class SettingsTests(unittest.TestCase):
 def setUp(self):
  self.env=patch.dict(os.environ,{'ADMIN_TOKEN':'admin-test','APIFY_API_TOKEN':'','APIFY_ACTOR_ID':'','APIFY_INPUT_JSON':''});self.env.start()
  cfg.delete();engine.JOB['running']=False
  self.c=TestClient(app);self.h={'X-Admin-Token':'admin-test'}
  self.data={'token':'synthetic-secret-token','actor_id':'owner~actor','input_json':'{"query":"SSD"}'}
 def tearDown(self):self.env.stop()
 def save(self):return self.c.post('/api/settings/apify',data=self.data,headers=self.h)
 def test_auth(self):
  self.assertEqual(self.c.get('/api/settings/apify').status_code,401)
  self.assertEqual(self.c.post('/api/settings/apify',data=self.data).status_code,401)
  os.environ.pop('ADMIN_TOKEN');self.assertEqual(self.c.get('/api/settings/apify').status_code,403)
 def test_encrypted_no_disclosure(self):
  self.assertEqual(self.save().status_code,200)
  with core.connect() as c:raw=c.execute("SELECT value FROM config WHERE key='apify_encrypted'").fetchone()[0]
  self.assertNotIn(self.data['token'],raw)
  r=self.c.get('/api/settings/apify',headers=self.h)
  self.assertTrue(r.json()['token_configured']);self.assertNotIn(self.data['token'],r.text)
  self.assertEqual(r.headers['cache-control'],'no-store')
  self.assertNotIn(self.data['token'],self.c.get('/settings').text)
  self.assertNotIn(self.data['token'],core.redact(self.data['token']))
 def test_blank_preserves(self):
  self.save();self.data['token']='';self.assertEqual(self.save().status_code,200)
  self.assertEqual(cfg.effective()['APIFY_API_TOKEN'],'synthetic-secret-token')
 def test_validation(self):
  for key,value in [('input_json','[]'),('input_json','bad'),('actor_id','https://invalid'),('token','bad token')]:
   with self.subTest(key=key,value=value):
    d=dict(self.data);d[key]=value;self.assertEqual(self.c.post('/api/settings/apify',data=d,headers=self.h).status_code,400)
 def test_cross_origin(self):
  self.assertEqual(self.c.post('/api/settings/apify',data=self.data,headers={**self.h,'Origin':'https://evil.example'}).status_code,403)
 def test_delete_and_fallback(self):
  self.save();self.assertEqual(self.c.post('/api/settings/apify/delete',headers=self.h).status_code,200)
  self.assertFalse(cfg.public()['token_configured'])
  os.environ['APIFY_API_TOKEN']='env-token';self.assertTrue(cfg.public()['token_configured'])
 def test_running_lock(self):
  engine.JOB['running']=True
  self.assertEqual(self.save().status_code,409)
  self.assertEqual(self.c.post('/api/settings/apify/delete',headers=self.h).status_code,409)
 def test_connector_uses_saved_config(self):
  self.save()
  class Response:
   def json(self):return []
  class Net:
   async def request(inner,method,url,**kw):
    self.assertNotIn('synthetic-secret-token',url)
    self.assertEqual(kw['headers']['Authorization'],'Bearer synthetic-secret-token')
    self.assertEqual(kw['json'],{'query':'SSD'})
    return Response()
  items,stats=asyncio.run(ekap.fetch(Net(),['TUR'],core.now(),{}));self.assertEqual(items,[])
 def test_clear_label(self):
  text=self.c.get('/').text
  self.assertNotIn('built-in method',text)
  self.assertIn('Зняти вибір',text)
if __name__=='__main__':unittest.main(verbosity=2)
