import fs from 'node:fs';
import * as THREE from '../vendor/three.module.js';
import {GLTFExporter} from '../vendor/exporters/GLTFExporter.js';
import {createCharacter} from '../src/character.js';
globalThis.FileReader=class {async readAsDataURL(blob){const b=await blob.arrayBuffer();this.result='data:'+blob.type+';base64,'+Buffer.from(b).toString('base64');this.onloadend?.();}async readAsArrayBuffer(blob){this.result=await blob.arrayBuffer();this.onloadend?.();}};
const avatar=createCharacter({shirt:'#e8dfc6',skin:'#633f2e'});const clips=[];
for(const [name,speed,duration]of [['Idle',0,2],['Walk',2.1,.7/2.1],['Run',4.5,1.35/4.5]]){
 const sample=createCharacter({shirt:'#e8dfc6',skin:'#633f2e'});for(let i=0;i<300;i++)sample.update(1/60,speed);
 const times=[],values=Object.fromEntries(Object.keys(sample.joints).map(k=>[k,[]])),pelvis=[];
 for(let i=0;i<=32;i++){const t=i/32*duration;times.push(t);sample.update(i?duration/32:0,speed);if(name==='Idle')sample.joints.chest.rotation.x=Math.sin(t*Math.PI)*.008;for(const [k,b]of Object.entries(sample.joints))values[k].push(...b.quaternion.toArray());pelvis.push(...sample.joints.pelvis.position.toArray());}
 const tracks=[];for(const [k,data]of Object.entries(values)){data.splice(-4,4,...data.slice(0,4));tracks.push(new THREE.QuaternionKeyframeTrack(k+'.quaternion',times,data));}pelvis.splice(-3,3,...pelvis.slice(0,3));tracks.push(new THREE.VectorKeyframeTrack('pelvis.position',times,pelvis));clips.push(new THREE.AnimationClip(name,duration,tracks));sample.dispose();
}
const result=await new GLTFExporter().parseAsync(avatar.group,{binary:false,animations:clips,trs:true});result.asset.copyright='TOGO LIFE Studio — original avatar, MIT';result.asset.extras={source:'scripts/export-avatar.mjs',limitations:'Original stylised articulated volumes; no mocap or foot IK.'};fs.writeFileSync(new URL('../assets/avatar.gltf',import.meta.url),JSON.stringify(result));avatar.dispose();console.log(JSON.stringify({file:'assets/avatar.gltf',bytes:fs.statSync(new URL('../assets/avatar.gltf',import.meta.url)).size,joints:result.skins[0].joints.length,clips:result.animations.map(a=>a.name)}));
