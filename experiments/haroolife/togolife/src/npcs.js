import {createCharacter} from './character.js';
import {angleTowards} from './controller.js';
// Authored graph: sidewalks and a single crossing at the southern cross street.
const nodes=[[-7,-18],[-7,-7],[-7,1],[-10,1],[-7,12],[-7,23],[-7,29],[7,29],[7,23],[7,6],[7,-7],[7,-18]];
const links=[[0,1],[1,2],[2,3],[2,4],[4,5],[5,6],[6,7],[7,8],[8,9],[9,10],[10,11]];
const adjacency=nodes.map(()=>[]);for(const [a,b]of links){adjacency[a].push(b);adjacency[b].push(a);}
function path(from,to){const queue=[[from]],seen=new Set([from]);while(queue.length){const p=queue.shift(),last=p.at(-1);if(last===to)return p;for(const next of adjacency[last])if(!seen.has(next)){seen.add(next);queue.push([...p,next]);}}return [from];}
function nearestNode(pos){let best=0,d=Infinity;nodes.forEach(([x,z],i)=>{const n=(x-pos.x)**2+(z-pos.z)**2;if(n<d){d=n;best=i;}});return best;}
export function createResidents(scene){const names=['Ama','Kodjo','Abla','Sena','Koffi','Yawa','Mensah','Akossiwa'];
 const people=names.map((name,i)=>{const c=createCharacter({shirt:['#b9563e','#247c7a','#d5ac57','#dbcdb5'][i%4],skin:i%2?'#936044':'#633f2e',trousers:i%2?'#4b4546':'#223f45',scale:i%2?.96:1});scene.add(c.group);const start=nodes[(i*2)%nodes.length];c.group.position.set(start[0],.24,start[1]);return {id:'resident-'+i,name,character:c,index:i,route:[],purpose:null,state:'idle',speed:1+(i%3)*.15,visits:0,job:i%4===0?'vendeuse':i%4===1?'artisan':i%4===2?'commerçante':'étudiant'};});
 function update(dt,time){for(const p of people){const h=(time+p.index*.12)%24,purpose=h<7||h>=19?'home':h<10?'buy':h<16?'work':h<18?'waitTaxi':'talk';const target=purpose==='home'?(p.index%2?8:5):purpose==='buy'?3:purpose==='work'?(p.index%2?10:1):purpose==='waitTaxi'?9:4;
 if(p.purpose!==purpose){p.purpose=purpose;p.route=path(nearestNode(p.character.group.position),target);p.state='walk';}
 const pos=p.character.group.position,node=p.route[0];if(node===undefined){p.state=purpose;p.character.update(dt,0);continue;}
 const [x,z]=nodes[node],dx=x-pos.x,dz=z-pos.z,d=Math.hypot(dx,dz);if(d<.10){p.route.shift();if(!p.route.length){p.state=purpose;p.visits++;}p.character.update(dt,0);continue;}
 p.state='walk';const step=Math.min(d,p.speed*dt);pos.x+=dx/d*step;pos.z+=dz/d*step;p.character.group.rotation.y=angleTowards(p.character.group.rotation.y,Math.atan2(dx,dz),dt);p.character.update(dt,p.speed);
 }}return {people,update,dispose(){people.forEach(p=>{scene.remove(p.character.group);p.character.dispose();});}};
}
