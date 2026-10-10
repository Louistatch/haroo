"""Real-input QA; run only on an executor allowing Chromium sockets.
No screenshots or performance claims exist until this script succeeds.
python tests/browser.py --url http://127.0.0.1:8000/dist/
"""
import argparse,json,time,math,traceback
from pathlib import Path
from playwright.sync_api import sync_playwright
parser=argparse.ArgumentParser();parser.add_argument('--url',default='http://127.0.0.1:8000/dist/');args=parser.parse_args()
output=Path(__file__).resolve().parents[1]/'artifacts';output.mkdir(exist_ok=True)
report={'status':'running','checks':[],'captures':[],'errors':[]}
def check(name,condition):
 report['checks'].append({'name':name,'pass':bool(condition)})
 if not condition:raise AssertionError(name)
try:
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-crashpad-for-testing','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader'])
  context=browser.new_context(viewport={'width':1440,'height':900},record_video_dir=str(output/'motion'))
  page=context.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.on('console',lambda m:errors.append(m.text) if m.type=='error' else None)
  start=time.monotonic();page.goto(args.url+'?qa=1',wait_until='networkidle');page.wait_for_selector('#start[open]');report['loadSeconds']=time.monotonic()-start
  page.select_option('#shirt','#217d7b');page.click('#startBtn');page.wait_for_selector('#start[open]',state='hidden');page.wait_for_timeout(300)
  def state():return page.evaluate('window.__THREE_GAME_DIAGNOSTICS__.state')
  initial=state()['player'];page.keyboard.down('w');page.wait_for_timeout(1400);page.keyboard.up('w');moved=state()['player'];check('walk changes position',math.hypot(initial['x']-moved['x'],initial['z']-moved['z'])>1)
  page.keyboard.down('Shift');page.keyboard.down('w');page.wait_for_timeout(1000);check('run state',state()['player']['animation']=='Run');page.keyboard.up('w');page.keyboard.up('Shift');page.wait_for_timeout(500);check('progressive stop',state()['player']['speed']<.1)
  def walk_to(x,z):
   end=time.monotonic()+40
   while time.monotonic()<end:
    pos=state()['player'];dx=x-pos['x'];dz=z-pos['z'];dist=math.hypot(dx,dz)
    if dist<.65:return
    ix=dx*math.cos(.2)-dz*math.sin(.2);iz=dx*math.sin(.2)+dz*math.cos(.2)
    chosen=[]
    if abs(ix)>.35*dist:chosen.append('d' if ix>0 else 'a')
    if abs(iz)>.35*dist:chosen.append('s' if iz>0 else 'w')
    for key in chosen:page.keyboard.down(key)
    page.wait_for_timeout(160)
    for key in chosen:page.keyboard.up(key)
   raise AssertionError('real-input route blocked')
  walk_to(-7,0);walk_to(-15,0);page.keyboard.press('e');page.get_by_role('button',name='Acheter 4 produits').click();check('market buy debits 1400 F',state()['simulation']['money']==13600)
  walk_to(-7,0);walk_to(-7,25);walk_to(-13,25);page.keyboard.press('e');page.get_by_role('button',name='Ouvrir mon comptoir').click();page.keyboard.press('e');page.get_by_role('button',name='Déposer mon sac').click();check('physical delivery stocks kiosk',state()['simulation']['stock']==4)
  page.wait_for_timeout(24000);check('demand makes sales',state()['simulation']['sales']>0)
  page.screenshot(path=str(output/'desktop-active.png'));report['captures'].append('desktop-active.png');before=state()['npcs'];page.wait_for_timeout(2000);after=state()['npcs'];check('NPC routines move',any(abs(a['z']-b['z'])>.1 for a,b in zip(before,after)))
  page.click('#pauseBtn');before=state()['simulation'];page.wait_for_timeout(1000);check('pause freezes economy',state()['simulation']==before);page.get_by_role('button',name='Reprendre',exact=True).click()
  report['desktop']=state();report['renderer']=page.evaluate('({calls:window.__THREE_GAME_DIAGNOSTICS__.renderer.render.calls,triangles:window.__THREE_GAME_DIAGNOSTICS__.renderer.render.triangles,memory:window.__THREE_GAME_DIAGNOSTICS__.renderer.memory})')
  saved=state()['simulation'];page.reload(wait_until='networkidle');page.click('#continueBtn');check('save restores appearance',state()['simulation']['appearance']==saved['appearance']);check('save restores business',state()['simulation']['biz']==True)
  check('no console/page errors',not errors);report['errors']=errors;context.close()
  mobile=browser.new_context(viewport={'width':390,'height':844},device_scale_factor=1.5,is_mobile=True,has_touch=True);page=mobile.new_page();page.goto(args.url+'?qa=1',wait_until='networkidle');page.click('#startBtn');page.wait_for_timeout(600);initial=state()['player']
  joy=page.locator('#joystick').bounding_box();page.dispatch_event('#joystick','pointerdown',{'pointerId':7,'pointerType':'touch','clientX':joy['x']+55,'clientY':joy['y']+18});page.wait_for_timeout(1200);page.dispatch_event('#joystick','pointercancel',{'pointerId':7,'pointerType':'touch'});page.wait_for_timeout(500)
  check('mobile joystick changes position',math.hypot(initial['x']-state()['player']['x'],initial['z']-state()['player']['z'])>.5);check('pointercancel stops movement',state()['player']['speed']<.1);check('responsive width',page.evaluate('document.documentElement.scrollWidth<=innerWidth'))
  page.screenshot(path=str(output/'mobile-active.png'));report['captures'].append('mobile-active.png');report['mobile']=state();report['status']='pass';mobile.close();browser.close()
except Exception as e:
 report['status']='blocked' if 'BrowserType.launch' in str(e) else 'failed';report['errors'].append(str(e));report['traceback']=traceback.format_exc()
finally:
 (output/'browser-results.json').write_text(json.dumps(report,indent=2,ensure_ascii=False));print(json.dumps({'status':report['status'],'checks':len(report['checks']),'captures':report['captures']}))
 if report['status']!='pass':raise SystemExit(1)
