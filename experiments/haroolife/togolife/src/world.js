import * as THREE from '../vendor/three.module.js';

/** Original art: a stylised Lomé neighbourhood, not a surveyed reconstruction. */
export function buildWorld(scene,{city='lome',quality='high'}={}) {
  const root=new THREE.Group(); root.name='Quartier original — '+city; scene.add(root);
  const colliders=[], places=[], batches=new Map(), textures=[], materials=[];
  const kara=city==='kara';
  function mat(color,roughness=.86,metalness=0){const m=new THREE.MeshStandardMaterial({color,roughness,metalness});materials.push(m);return m;}
  const sand=mat(kara?'#b16a45':'#d4b08a'), curb=mat('#cabca8'), asphalt=mat('#414c50'), cream=mat('#e6d6b6'), terracotta=mat('#ba6849'), teal=mat('#357f80'), roof=mat('#697c79',.55,.35), wood=mat('#85614a'), dark=mat('#253e43'), leaf=mat('#416f47'), steel=mat('#394747',.5,.5), white=mat('#e9e6d2'), yellow=mat('#dfb735'), red=mat('#b3503e');
  const boxG=new THREE.BoxGeometry(1,1,1), cylG=new THREE.CylinderGeometry(1,1,1,8), sphereG=new THREE.SphereGeometry(1,8,6);
  const dummy=new THREE.Object3D();
  function part(g,m,x,y,z,sx,sy,sz,ry=0,rz=0){const key=g.uuid+m.uuid;if(!batches.has(key))batches.set(key,{g,m,transforms:[]});dummy.position.set(x,y,z);dummy.scale.set(sx,sy,sz);dummy.rotation.set(0,ry,rz);dummy.updateMatrix();batches.get(key).transforms.push(dummy.matrix.clone());}
  const box=(m,x,y,z,w,h,d,ry=0)=>part(boxG,m,x,y,z,w,h,d,ry);
  function texture(base,type){const c=document.createElement('canvas');c.width=c.height=256;const ctx=c.getContext('2d');ctx.fillStyle=base;ctx.fillRect(0,0,256,256);let seed=37;for(let i=0;i<16000;i++){seed=(seed*16807)%2147483647;let x=seed%256;seed=(seed*16807)%2147483647;let y=seed%256;ctx.fillStyle=i%2?'rgba(0,0,0,.035)':'rgba(255,255,255,.055)';ctx.fillRect(x,y,2,2);}if(type==='roof'){ctx.strokeStyle='rgba(20,35,35,.3)';for(let x=0;x<256;x+=16){ctx.beginPath();ctx.moveTo(x,0);ctx.lineTo(x,256);ctx.stroke();}}const t=new THREE.CanvasTexture(c);t.wrapS=t.wrapT=THREE.RepeatWrapping;t.repeat.set(type==='road'?8:3,8);t.colorSpace=THREE.SRGBColorSpace;textures.push(t);return t;}
  asphalt.map=texture('#465052','road');sand.map=texture(kara?'#b47b53':'#cfad85');cream.map=texture('#e0cfb0');roof.map=texture('#788a83','roof');
  box(sand,0,-.22,0,110,.4,100);box(asphalt,0,.015,0,10,.08,90);
  for(const x of [-6.7,6.7]){box(curb,x,.1,0,3.4,.25,90);box(cream,Math.sign(x)*5.08,.2,0,.18,.34,90);}
  for(let z=-43;z<44;z+=6)box(white,0,.065,z,.12,.015,2.6);
  // Cross streets connect the district to a larger city without loading it all.
  for(const z of [-24,29]){box(asphalt,0,.021,z,100,.07,6);for(let x=-48;x<49;x+=6)box(white,x,.069,z,2.3,.015,.1);}
  function sign(text,x,y,z,w=4,color='#183e42',rotation=0){const c=document.createElement('canvas');c.width=512;c.height=96;const ctx=c.getContext('2d');ctx.fillStyle=color;ctx.fillRect(0,0,512,96);ctx.fillStyle='#f7ead0';ctx.font='bold 34px sans-serif';ctx.textAlign='center';ctx.textBaseline='middle';ctx.fillText(text,256,49,482);const t=new THREE.CanvasTexture(c);t.colorSpace=THREE.SRGBColorSpace;textures.push(t);const m=new THREE.MeshBasicMaterial({map:t});materials.push(m);const p=new THREE.Mesh(new THREE.PlaneGeometry(w,w*96/512),m);p.position.set(x,y,z);p.rotation.y=rotation;root.add(p);}
  function building(x,z,w,d,h,color,label,open=false){const m=mat(color);box(m,x,h/2,z,w,h,d);box(cream,x,h+.16,z,w+.2,.32,d+.2);box(roof,x,h+.5,z,w+.9,.28,d+1);const front=z+d/2+.035;
    // Facade: framed glazing, shutters, recessed shop frontage, plaster cornice.
    box(cream,x,.28,front,w,.35,.22);box(cream,x,h-.7,front,w,.18,.2);
    for(let i=-1;i<=1;i++){const wx=x+i*w*.29;box(dark,wx,1.9,front+.04,w*.21,1.8,.08);box(wood,wx-w*.115,1.9,front+.13,.15,1.95,.15);box(wood,wx+w*.115,1.9,front+.13,.15,1.95,.15);for(let j=0;j<6;j++)box(teal,wx,1.25+j*.24,front+.16,w*.19,.08,.09);}
    if(h>5)for(let i=-1;i<=1;i++){box(dark,x+i*w*.29,h-2,front+.04,1.4,1.5,.08);box(cream,x+i*w*.29,h-2.9,front+.2,1.6,.15,.4);}
    box(teal,x,3.25,front+.9,w+.3,.18,1.8);for(const px of [x-w/2,x+w/2])part(cylG,steel,px,1.65,front+1.5,.055,3.3,.055);
    if(label)sign(label,x,3.8,front+.12,w*.92);
    if(!open)colliders.push({x,z,w,d});
  }
  building(-17,-13,15,9,6.8,'#bca082','ATELIER • COUTURE');building(-16,-36,14,10,4.5,'#dfcfa9','MAISON DES ARTISANS');building(16,-13,15,10,7,'#d5bc9e','PHARMACIE DU QUARTIER');building(18,-36,18,11,5.2,'#a77960','CAFÉ • LE PALMIER');building(-16,19,11,7,4.3,'#ccb590','COMPTOIR DE LOMÉ');
  // Walkable courtyard house: individual walls preserve an actual doorway.
  const hx=16,hz=17;box(cream,hx,.05,hz,13,.15,11);box(terracotta,hx,2,hz-5.5,13,4,.35);box(terracotta,hx-6.5,2,hz,.35,4,11);box(terracotta,hx+6.5,2,hz,.35,4,11);for(const dx of [-4.25,4.25]){box(terracotta,hx+dx,2,hz+5.5,4.5,4,.35);colliders.push({x:hx+dx,z:hz+5.5,w:4.5,d:.4});}for(const [x,z,w,d] of [[hx,hz-5.5,13,.4],[hx-6.5,hz,.4,11],[hx+6.5,hz,.4,11]])colliders.push({x,z,w,d});
  box(roof,hx,4.3,hz-3,14,.25,5.5);box(wood,hx+3,.45,hz-2,3,.8,1.5);box(white,hx+3,.91,hz-2,3,.15,1.5);box(teal,hx-3,.8,hz-2,2,1.4,1);box(wood,hx,1.1,hz-4,2.3,.12,1);sign('VOTRE COUR • AKOÉ',hx,3.3,hz+5.72,7);
  // Market canopies, woven crates, produce and fabric. Fully original geometry.
  const produce=[mat('#dca449'),mat('#9cbb55'),mat('#c65539'),mat('#6d9047')];
  for(let i=0;i<7;i++){const x=-12-(i%4)*4.5,z=-2+Math.floor(i/4)*5;box(wood,x,.75,z,3.5,1.3,1.8);box(i%2?terracotta:teal,x,2.8,z,4,.16,3.2);for(const dx of [-1.8,1.8])for(const dz of [-1.3,1.3])part(cylG,wood,x+dx,1.45,z+dz,.05,2.9,.05);for(let k=0;k<3;k++){box(wood,x-1.1+k*1.1,1.5,z,.95,.25,1.45);for(let j=0;j<7;j++)part(sphereG,produce[(i+k)%4],x-1.35+k*1.1+(j%3)*.24,1.76,z-.4+Math.floor(j/3)*.27,.13,.11,.16);}for(let k=0;k<5;k++)box(wood,x,.4,z-.6+k*.3,3.6,.06,.05);colliders.push({x,z,w:3.5,d:1.8,height:1.7});}
  sign('MARCHÉ • PRODUITS LOCAUX',-17,3.7,3.3,10,'#77412e');
  function palm(x,z,height=8){colliders.push({x,z,w:.4,d:.4,height});part(cylG,wood,x,height/2,z,.17,height,.24,0,.06);for(let i=0;i<8;i++){let a=i*Math.PI/4;const points=[];for(let j=0;j<5;j++){const r=j*.8;points.push(new THREE.Vector3(x+Math.cos(a)*r,height+.45-Math.pow(j/4,2)*1.6,z+Math.sin(a)*r));}const curve=new THREE.CatmullRomCurve3(points);const mesh=new THREE.Mesh(new THREE.TubeGeometry(curve,7,.12,3,false),leaf);root.add(mesh);} }
  for(const [x,z] of [[-8,9],[8,-6],[-8,-19],[8,27],[-24,23],[25,5],[-26,-15],[26,-28]])palm(x,z,kara?6.5:8);
  // Street furniture and drainage give the streets human scale.
  for(let z=-40;z<41;z+=16){for(const x of [-7.6,7.6]){part(cylG,steel,x,3,z,.065,6,.065);box(steel,x+Math.sign(x)*-.55,5.9,z,1.2,.09,.12);box(white,x+Math.sign(x)*-.9,5.8,z,.6,.1,.28);}for(const x of [-5.5,5.5])for(let k=0;k<4;k++)box(dark,x,.242,z+k*.17,.8,.014,.055);}
  for(const x of [-9,9]){colliders.push({x,z:10,w:1.8,d:.6,height:1.3});box(wood,x,.6,10,1.8,.14,.5);box(wood,x,.95,10.25,1.8,.6,.1);for(const dx of [-.65,.65])box(steel,x+dx,.32,10,.07,.6,.4);}
  function vehicle(x,z,moving=false){const g=new THREE.Group();root.add(g);g.position.set(x,0,z);const add=(geo,m,px,py,pz,sx,sy,sz)=>{const o=new THREE.Mesh(geo,m);o.position.set(px,py,pz);o.scale.set(sx,sy,sz);o.castShadow=true;g.add(o);};add(boxG,yellow,0,.65,0,1.65,.6,3.4);add(boxG,yellow,0,1.12,-.15,1.48,.6,1.9);add(boxG,dark,0,1.21,.84,1.32,.42,.035);add(boxG,dark,0,1.21,-1.11,1.32,.42,.035);for(const xx of [-.751,.751])add(boxG,dark,xx,1.22,-.1,.015,.38,1.6);for(const xx of [-.8,.8])for(const zz of [-1.05,1.05]){const o=new THREE.Mesh(cylG,dark);o.rotation.z=Math.PI/2;o.position.set(xx,.4,zz);o.scale.set(.35,.16,.35);g.add(o);}for(const xx of [-.52,.52])add(boxG,white,xx,.7,1.72,.38,.17,.05);return {g,moving};}
  const cars=[vehicle(2.7,-30,true),vehicle(-2.7,25,true),vehicle(8.3,5)];for(const car of cars){car.collider={x:car.g.position.x,z:car.g.position.z,w:1.9,d:3.5,height:1.6};colliders.push(car.collider);}
  sign('TAXI • DÉPARTS',8.5,2.8,6,3,'#396b68');
  for(let i=0;i<5;i++){let x=-9.4-i*.9,z=7;box(dark,x,.62,z,.36,.23,1.3);box(red,x,.72,z-.15,.3,.35,.6);for(const dz of [-.6,.6]){const o=new THREE.Mesh(new THREE.TorusGeometry(.29,.07,6,12),dark);o.position.set(x,.32,z+dz);o.rotation.y=Math.PI/2;root.add(o);}part(cylG,steel,x,1,z+.45,.025,.65,.025,0,-.22);box(steel,x,1.24,z+.4,.7,.035,.035);}
  places.push({id:'market',name:'Marché des produits locaux',x:-15,z:0,radius:6},{id:'kiosk',name:'Comptoir de Lomé',x:-13,z:25,radius:4},{id:'home',name:'Votre logement',x:16,z:23,radius:4},{id:'taxi',name:'Arrêt de taxi',x:7,z:6,radius:4},{id:'studio',name:'Atelier · livraison',x:-17,z:-7,radius:4});
  // Merge repeated details into GPU instances instead of hundreds of scene nodes.
  for(const {g,m,transforms} of batches.values()){const mesh=new THREE.InstancedMesh(g,m,transforms.length);transforms.forEach((t,i)=>mesh.setMatrixAt(i,t));mesh.castShadow=true;mesh.receiveShadow=true;mesh.computeBoundingSphere();root.add(mesh);}
  return {root,colliders,places,bounds:{minX:-45,maxX:45,minZ:-42,maxZ:42},spawn:{x:-7,z:12},traffic:{update(dt){for(let i=0;i<2;i++){const c=cars[i].g;c.position.z+=dt*(i===0?3.8:-3.3);c.rotation.y=i===0?0:Math.PI;if(c.position.z>43)c.position.z=-43;if(c.position.z< -43)c.position.z=43;cars[i].collider.z=c.position.z;}}},dispose(){scene.remove(root);const geos=new Set();root.traverse(o=>{if(o.geometry)geos.add(o.geometry)});geos.forEach(g=>g.dispose());materials.forEach(m=>m.dispose());textures.forEach(t=>t.dispose());}};
}
