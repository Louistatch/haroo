import {test} from 'node:test';import assert from 'node:assert/strict';import {move,blocked,angleTowards} from '../src/controller.js';
const walls=[{x:0,z:0,w:4,d:4}],bounds={minX:-20,maxX:20,minZ:-20,maxZ:20};
test('swept substeps prevent wall tunneling at run speed',()=>{const p={x:-5,z:0};move(p,20,0,1,walls,bounds);assert.ok(p.x< -2.31);assert.equal(blocked(p.x,p.z,walls),false)});
test('wall contact permits sliding',()=>{const p={x:-2.4,z:0};move(p,3,2,1,walls,bounds);assert.ok(p.z>1.9);assert.ok(p.x< -2.31)});
test('turn takes shortest arc across pi',()=>{const a=angleTowards(3.1,-3.1,.05);assert.ok(a>3.1&&a<3.19)});
test('camera proxy shortens camera segment at wall without raycasting render geometry',async()=>{const {cameraDistance}=await import('../src/controller.js');const hit=cameraDistance({x:-4,z:0,y:1.2},{x:5,z:0,y:3},walls);assert.ok(hit>.15&&hit<.3);assert.ok(cameraDistance({x:-4,z:-4,y:1},{x:5,z:-4,y:3},walls)>.9)});
