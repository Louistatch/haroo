import * as THREE from '../vendor/three.module.js';

/** Original articulated adult avatar. Metres, feet at y=0, forward +Z.
 * No third-party models. The single body mesh uses an actual GPU skinning rig.
 * Synchronous API: {group, mesh, skeleton, update(dt, metresPerSecond), dispose}.
 */
export function createCharacter({skin='#70432e', shirt='#e3b24d', trousers='#263a47', hair='#171211', scale=1}={}) {
  const group=new THREE.Group(); group.name='TogoLifeAvatar'; group.scale.setScalar(scale);
  const bones=[], joints={};
  function joint(name,parent,x,y,z=0){const b=new THREE.Bone();b.name=name;b.position.set(x,y,z);if(parent)parent.add(b);bones.push(b);joints[name]=b;return b;}
  const root=joint('root',null,0,0,0), pelvis=joint('pelvis',root,0,.91), spine=joint('spine',pelvis,0,.18), chest=joint('chest',spine,0,.22), neck=joint('neck',chest,0,.17), head=joint('head',neck,0,.1);
  for(const [side,s] of [['left',1],['right',-1]]){
    const hip=joint(side+'Hip',pelvis,s*.105,-.03), knee=joint(side+'Knee',hip,0,-.40), ankle=joint(side+'Ankle',knee,0,-.40), foot=joint(side+'Foot',ankle,0,-.035,.045);
    const shoulder=joint(side+'Shoulder',chest,s*.22,.025), elbow=joint(side+'Elbow',shoulder,s*.09,-.265), wrist=joint(side+'Wrist',elbow,s*.035,-.235);
    joint(side+'Hand',wrist,0,-.07);
  }
  group.add(root);group.updateMatrixWorld(true);
  const positions=[],normals=[],indices=[],skinIndices=[],skinWeights=[],colors=[];
  const c=new THREE.Color(), v=new THREE.Vector3(), n=new THREE.Vector3();
  function part(bone, center, size, color, detail=12){
    const g=new THREE.SphereGeometry(1,detail,Math.max(6,Math.floor(detail*.7)));
    const p=g.attributes.position, normal=g.attributes.normal, offset=positions.length/3, bi=bones.indexOf(bone);c.set(color);
    const origin=new THREE.Vector3();bone.getWorldPosition(origin);
    for(let i=0;i<p.count;i++){
      v.fromBufferAttribute(p,i).multiply(new THREE.Vector3(...size)).add(new THREE.Vector3(...center)).add(origin);
      positions.push(v.x,v.y,v.z); n.fromBufferAttribute(normal,i); n.set(n.x/size[0],n.y/size[1],n.z/size[2]).normalize();normals.push(n.x,n.y,n.z);
      skinIndices.push(bi,0,0,0);skinWeights.push(1,0,0,0);colors.push(c.r,c.g,c.b);
    }
    for(const idx of g.index.array)indices.push(offset+idx);g.dispose();
  }
  // Anatomical volumes overlap at the articulation; clothes follow the same skeleton.
  part(pelvis,[0,0,0],[.165,.14,.105],trousers);
  part(spine,[0,.055,0],[.17,.18,.10],shirt,16);
  part(chest,[0,0,0],[.215,.17,.115],shirt,16);
  part(neck,[0,.015,0],[.055,.085,.055],skin);
  part(head,[0,.035,0],[.102,.14,.092],skin,20);
  part(head,[0,.112,-.009],[.105,.075,.095],hair,18);
  part(head,[0,-.015,.091],[.021,.028,.025],skin); // bridge and nose
  part(head,[0,-.065,.071],[.047,.014,.022],skin);
  for(const [side,s] of [['left',1],['right',-1]]){
    part(joints[side+'Hip'],[0,-.19,0],[.085,.23,.085],trousers);
    part(joints[side+'Knee'],[0,-.19,0],[.061,.215,.060],trousers);
    part(joints[side+'Foot'],[0,-.012,.035],[.071,.048,.125],'#ded7c9');
    part(joints[side+'Foot'],[0,-.041,.04],[.073,.014,.128],'#393a36');
    part(joints[side+'Shoulder'],[s*.035,-.065,0],[.077,.12,.080],shirt);
    part(joints[side+'Shoulder'],[s*.064,-.17,0],[.047,.14,.047],skin);
    part(joints[side+'Elbow'],[s*.015,-.12,0],[.038,.145,.04],skin);
    part(joints[side+'Hand'],[0,-.008,0],[.035,.067,.025],skin);
    part(joints[side+'Hand'],[-s*.025,.015,.012],[.018,.034,.019],skin);
    part(head,[s*.105,.021,-.005],[.021,.036,.018],skin);
    // Eyes inset in the face; dark irises, brow and subtle mouth avoid cartoon proportions.
    part(head,[s*.041,.047,.083],[.023,.008,.01],'#e5ddd3');
    part(head,[s*.041,.047,.092],[.006,.006,.003],'#211b18');
    part(head,[s*.041,.065,.083],[.027,.005,.006],hair);
  }
  part(head,[0,-.037,.09],[.026,.004,.003],'#41261f');
  const geometry=new THREE.BufferGeometry();geometry.setAttribute('position',new THREE.Float32BufferAttribute(positions,3));geometry.setAttribute('normal',new THREE.Float32BufferAttribute(normals,3));geometry.setAttribute('color',new THREE.Float32BufferAttribute(colors,3));geometry.setAttribute('skinIndex',new THREE.Uint16BufferAttribute(skinIndices,4));geometry.setAttribute('skinWeight',new THREE.Float32BufferAttribute(skinWeights,4));geometry.setIndex(indices);
  const material=new THREE.MeshStandardMaterial({vertexColors:true,roughness:.85});
  const mesh=new THREE.SkinnedMesh(geometry,material);mesh.name='OriginalAdultSkinnedBody';mesh.castShadow=true;mesh.receiveShadow=true;mesh.frustumCulled=false;group.add(mesh);group.updateMatrixWorld(true);
  const skeleton=new THREE.Skeleton(bones);mesh.bind(skeleton);
  let phase=0, blend=0, runBlend=0, state='Idle';
  function update(dt,speed=0){
    dt=Math.min(Math.max(dt,0),.06);speed=Math.max(0,Math.abs(speed));const moving=speed>.08;
    blend=THREE.MathUtils.damp(blend,moving?1:0,9,dt);runBlend=THREE.MathUtils.damp(runBlend,THREE.MathUtils.clamp((speed-2)/2,0,1),6,dt);
    state=!moving?'Idle':speed>2.8?'Run':'Walk';
    // Cadence derives from travelled distance and stride length, avoiding a fixed-rate glide.
    phase+=dt*speed/(.70+runBlend*.65)*Math.PI*2;
    const swing=(.38+runBlend*.32)*blend;
    for(const [side,offset] of [['left',0],['right',Math.PI]]){
      const p=phase+offset, stride=Math.sin(p), recovery=Math.max(0,-stride);
      joints[side+'Hip'].rotation.x=stride*swing;
      joints[side+'Knee'].rotation.x=-recovery*(.60+runBlend*.65)*blend;
      joints[side+'Ankle'].rotation.x=-stride*swing*.28;
      joints[side+'Shoulder'].rotation.x=-stride*swing*.8;
      joints[side+'Shoulder'].rotation.z=side==='left'?.08:-.08;
      joints[side+'Elbow'].rotation.x=-.12-runBlend*.7+stride*.09*blend;
    }
    pelvis.position.y=.91+Math.abs(Math.sin(phase))*.018*blend;
    spine.rotation.x=runBlend*.10;chest.rotation.y=Math.sin(phase)*.035*blend;
    head.rotation.y=-Math.sin(phase)*.02*blend;
    if(!moving){const breath=Math.sin(performance.now()*.0018)*.003;chest.scale.set(1,1+breath,1+breath);}
    else chest.scale.setScalar(1);
    group.userData.animationState=state;
  }
  update(0,0);
  return {group,mesh,skeleton,joints,update,get animationState(){return state;},dispose(){geometry.dispose();material.dispose();skeleton.dispose();group.removeFromParent();}};
}
