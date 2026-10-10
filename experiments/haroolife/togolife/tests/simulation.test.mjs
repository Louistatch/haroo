import test from 'node:test';
import assert from 'node:assert/strict';
import { Simulation, createState } from '../src/simulation.js';
const at=location=>({location});
test('trade requires money, carrying capacity and physical endpoints',()=>{
 const s=new Simulation();assert.equal(s.act('buy',at('kiosk')).ok,false);
 assert.equal(s.act({type:'buy',quantity:13},at('market')).ok,false);
 assert.equal(s.act({type:'buy',quantity:12},at('market')).ok,true);assert.equal(s.state.money,10800);
 assert.equal(s.act('deposit',at('kiosk')).ok,false);assert.equal(s.act('invest',at('kiosk')).ok,true);
 assert.equal(s.act('deposit',at('market')).ok,false);assert.equal(s.act('deposit',at('kiosk')).ok,true);
 assert.equal(s.state.stock,12);assert.equal(s.state.carried,0);
 s.act({type:'price',price:450},at('kiosk'));s.tick(60);assert.equal(s.state.sales,5);assert.equal(s.state.stock,7);assert.equal(s.state.money,4050);
});
test('high prices reduce sales and cannot create money without stock',()=>{
 const s=new Simulation();s.tick(60);assert.equal(s.state.money,15000);s.act('invest',at('kiosk'));s.act({type:'buy',quantity:4},at('market'));s.act('deposit',at('kiosk'));s.act({type:'price',price:1100},at('kiosk'));s.tick(60);assert.equal(s.state.sales,0);assert.equal(s.state.stock,4);
});
test('contracts require collection then separate destination, dialogue cannot farm reputation',()=>{
 const s=new Simulation();assert.equal(s.act('deliver',at('studio')).ok,false);s.act('contract',at('market'));assert.equal(s.act('deliver',at('market')).ok,false);assert.equal(s.act('contract',at('market')).ok,false);s.act('deliver',at('studio'));assert.equal(s.state.money,16200);assert.equal(s.act('deliver',at('studio')).ok,false);
 s.act('talk',{npcId:'ama'});assert.equal(s.act('talk',{npcId:'ama'}).ok,false);assert.equal(s.state.rep,2);
});
test('time creates rent debt, needs decay and expired deliveries are removed',()=>{
 const s=new Simulation();s.act('contract',at('market'));for(let i=0;i<25;i++)s.tick(60);assert.ok(s.state.day>=3);assert.ok(s.state.debt>=1600);assert.equal(s.state.contract,null);assert.ok(s.state.food<90);assert.equal(s.act('rest',at('home')).ok,false);assert.equal(s.act('rent',at('home')).ok,true);assert.equal(s.state.debt,0);
});
test('strict saves roundtrip, reject malicious values atomically and migrate legacy conservatively',()=>{
 const s=new Simulation();s.act('contract',at('market'));const snap=s.snapshot();assert.equal(new Simulation().load(JSON.stringify(snap)),true);
 for(const bad of [{...snap,money:Infinity},{...snap,carried:99},{...snap,price:0},{...snap,contract:{reward:9999}},{...snap,conversations:['x'.repeat(100)]},{...snap,day:1.2}]){const before=s.snapshot();assert.equal(s.load(bad),false);assert.deepEqual(s.snapshot(),before);}
 assert.equal(s.load({money:1234,name:'Ama',biz:true,stock:1000}),true);assert.equal(s.state.money,1234);assert.equal(s.state.biz,false);assert.equal(s.state.stock,0);assert.equal(s.load('{broken'),false);assert.equal(createState().version,2);
});
test('appearance and position survive a save, invalid appearance and coordinates reject atomically',()=>{const s=new Simulation();s.state.appearance={shirt:'#217d7b',skin:'#936044'};s.state.position={x:16,z:24};const saved=s.snapshot(),t=new Simulation();assert.equal(t.load(saved),true);assert.deepEqual(t.state.appearance,s.state.appearance);assert.deepEqual(t.state.position,s.state.position);assert.equal(t.load({...saved,position:{x:Infinity,z:0}}),false);assert.equal(t.load({...saved,appearance:{shirt:'red',skin:'red'}}),false)});
test('delivery is available only once per game day',()=>{const s=new Simulation();s.act('contract',at('market'));s.act('deliver',at('studio'));assert.equal(s.act('contract',at('market')).ok,false);for(let i=0;i<9;i++)s.tick(60);assert.equal(s.state.day,2);assert.equal(s.act('contract',at('market')).ok,true)});
