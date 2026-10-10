import * as THREE from '../vendor/three.module.js';
import {GLTFLoader} from '../vendor/loaders/GLTFLoader.js';
import {createCharacter} from './character.js';
/** Offline, licensed original glTF with authored animation clips. */
export async function loadCharacter({shirt='#e8dfc6',skin='#633f2e'}={}){
 try{const gltf=await new GLTFLoader().loadAsync((globalThis.__TOGO_AVATAR_URL__||new URL('../assets/avatar.gltf',import.meta.url).href));return fromGLTF(gltf,{shirt,skin});}
 catch(error){console.warn('Avatar glTF unavailable; original procedural rig used.',error);return createCharacter({shirt,skin});}
}
export function fromGLTF(gltf,{shirt='#e8dfc6',skin='#633f2e'}={}){
 const group=gltf.scene;let mesh;group.traverse(o=>{if(o.isSkinnedMesh){mesh=o;o.castShadow=true;o.receiveShadow=true;o.frustumCulled=false;}});if(!mesh)throw new Error('Avatar has no skeletal mesh');
 const attribute=mesh.geometry.getAttribute('color'),baseShirt=new THREE.Color('#e8dfc6'),baseSkin=new THREE.Color('#633f2e'),newShirt=new THREE.Color(shirt),newSkin=new THREE.Color(skin);
 for(let i=0;i<attribute.count;i++){const dr=Math.abs(attribute.getX(i)-baseShirt.r)+Math.abs(attribute.getY(i)-baseShirt.g)+Math.abs(attribute.getZ(i)-baseShirt.b),ds=Math.abs(attribute.getX(i)-baseSkin.r)+Math.abs(attribute.getY(i)-baseSkin.g)+Math.abs(attribute.getZ(i)-baseSkin.b);const c=dr<.001?newShirt:ds<.001?newSkin:null;if(c)attribute.setXYZ(i,c.r,c.g,c.b);}attribute.needsUpdate=true;
 const mixer=new THREE.AnimationMixer(group),actions={};for(const clip of gltf.animations)actions[clip.name]=mixer.clipAction(clip);if(!actions.Idle||!actions.Walk||!actions.Run)throw new Error('Avatar is missing animation clips');
 let state='Idle',disposed=false;actions.Idle.play();
 function update(dt,speed=0){if(disposed)return;dt=Math.max(0,Math.min(dt,.1));const next=speed<.08?'Idle':speed>2.8?'Run':'Walk';if(next!==state){const prev=actions[state],current=actions[next];current.reset().setEffectiveWeight(1).play();prev.crossFadeTo(current,.18,false);state=next;}if(state==='Walk')actions.Walk.setEffectiveTimeScale(Math.max(.1,speed/2.1));if(state==='Run')actions.Run.setEffectiveTimeScale(Math.max(.1,speed/4.5));mixer.update(dt);}
 return {group,mesh,skeleton:mesh.skeleton,update,get animationState(){return state;},dispose(){if(disposed)return;disposed=true;mixer.stopAllAction();mixer.uncacheRoot(group);group.traverse(o=>{if(o.geometry)o.geometry.dispose();if(o.material){const list=Array.isArray(o.material)?o.material:[o.material];list.forEach(m=>m.dispose());}if(o.skeleton)o.skeleton.dispose();});group.removeFromParent();}};
}
