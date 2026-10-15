import os,json,re
from cryptography.fernet import Fernet,InvalidToken
from app import core
KEYS=('APIFY_API_TOKEN','APIFY_ACTOR_ID','APIFY_INPUT_JSON')
def cipher():
 key=os.getenv('SETTINGS_ENCRYPTION_KEY','')
 if not key:
  path=core.DATA/'.settings.key'
  try:fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
  except FileExistsError:key=path.read_text().strip()
  else:
   key=Fernet.generate_key().decode()
   with os.fdopen(fd,'w') as f:f.write(key)
 try:return Fernet(key.encode())
 except (ValueError,TypeError):raise ValueError('Invalid SETTINGS_ENCRYPTION_KEY') from None
def stored():
 with core.connect() as c:row=c.execute("SELECT value FROM config WHERE key='apify_encrypted'").fetchone()
 if not row:return {}
 try:return json.loads(cipher().decrypt(row[0].encode()))
 except (InvalidToken,ValueError):raise ValueError('Cannot decrypt Apify settings; restore original encryption key') from None
def effective():
 saved=stored();cfg={k:saved.get(k) or os.getenv(k,'') for k in KEYS}
 if cfg[KEYS[0]]:core.RUNTIME_SECRETS.add(cfg[KEYS[0]])
 return cfg
def public():
 cfg=effective()
 return {'token_configured':bool(cfg[KEYS[0]]),'actor_id':cfg[KEYS[1]],'input_json':cfg[KEYS[2]],'configured':all(cfg.values())}
def save(token,actor,input_json):
 token=token.strip();actor=actor.strip()
 if not re.fullmatch(r'[A-Za-z0-9_~-]+',actor):raise ValueError('Actor ID: use ID or username~actor-name')
 if len(input_json)>100000:raise ValueError('Input JSON too large')
 try:payload=json.loads(input_json)
 except ValueError:raise ValueError('Invalid Input JSON') from None
 if not isinstance(payload,dict):raise ValueError('Input JSON must be an object')
 if len(token)>4096 or any(c.isspace() for c in token):raise ValueError('Invalid token format')
 token=token or effective()[KEYS[0]]
 if not token:raise ValueError('Enter an Apify token')
 cfg=dict(zip(KEYS,(token,actor,json.dumps(payload,ensure_ascii=False))))
 encrypted=cipher().encrypt(json.dumps(cfg,ensure_ascii=False).encode()).decode()
 with core.connect() as c:c.execute('INSERT OR REPLACE INTO config VALUES (?,?)',('apify_encrypted',encrypted))
 core.RUNTIME_SECRETS.add(token)
def delete():
 with core.connect() as c:c.execute("DELETE FROM config WHERE key='apify_encrypted'")
