import base64, json, math, struct, os
from pathlib import Path
import numpy as np
import trimesh

OUT_GLB = Path('/mnt/data/orbit-mascot-wave-3d.glb')
OUT_GLTF = Path('/mnt/data/orbit-mascot-wave-3d.gltf')

def transform_mesh(mesh, matrix=None, scale=None, translate=None):
    m = mesh.copy()
    if scale is not None:
        S = np.eye(4)
        S[0,0], S[1,1], S[2,2] = scale
        m.apply_transform(S)
    if matrix is not None:
        m.apply_transform(matrix)
    if translate is not None:
        T = np.eye(4)
        T[:3,3] = translate
        m.apply_transform(T)
    return m

def sphere(scale, center=(0,0,0), subdivisions=3):
    m = trimesh.creation.icosphere(subdivisions=subdivisions, radius=1.0)
    return transform_mesh(m, scale=scale, translate=center)

def capsule_y(total_len, radius, center_y=None, center=(0,0,0), sections=24):
    cyl_h = max(0.001, total_len - 2*radius)
    m = trimesh.creation.capsule(height=cyl_h, radius=radius, count=[sections, sections])
    R = trimesh.transformations.rotation_matrix(math.radians(90), [1,0,0])
    m.apply_transform(R)
    cy = -total_len/2 if center_y is None else center_y
    m.apply_translation([center[0], center[1] + cy, center[2]])
    return m

def cylinder_y(length, radius, center=(0,0,0), sections=32):
    m = trimesh.creation.cylinder(radius=radius, height=length, sections=sections)
    R = trimesh.transformations.rotation_matrix(math.radians(90), [1,0,0])
    m.apply_transform(R)
    m.apply_translation([center[0], center[1], center[2]])
    return m

def torus(R=1.0, r=0.15, segR=64, segr=16, scale=(1,1,1), center=(0,0,0), arc=2*math.pi):
    verts=[]; faces=[]
    for i in range(segR+1):
        u = arc*i/segR
        cu,su=math.cos(u),math.sin(u)
        for j in range(segr):
            v=2*math.pi*j/segr
            cv,sv=math.cos(v),math.sin(v)
            x=(R+r*cv)*cu
            y=(R+r*cv)*su
            z=r*sv
            verts.append([x*scale[0]+center[0], y*scale[1]+center[1], z*scale[2]+center[2]])
    for i in range(segR):
        for j in range(segr):
            a=i*segr+j; b=i*segr+(j+1)%segr
            c=(i+1)*segr+(j+1)%segr; d=(i+1)*segr+j
            faces += [[a,b,c],[a,c,d]]
    return trimesh.Trimesh(vertices=np.array(verts), faces=np.array(faces), process=False)

def arc_tube(radius=0.22, tube=0.035, angle0=math.radians(205), angle1=math.radians(335), center=(0,0,0), seg=24, ring=10):
    verts=[]; faces=[]
    for i in range(seg+1):
        u=angle0 + (angle1-angle0)*i/seg
        radial=np.array([math.cos(u), math.sin(u), 0.0])
        binormal=np.array([0,0,1.0])
        p=np.array(center) + radius*radial
        for j in range(ring):
            v=2*math.pi*j/ring
            off=tube*(math.cos(v)*radial + math.sin(v)*binormal)
            verts.append((p+off).tolist())
    for i in range(seg):
        for j in range(ring):
            a=i*ring+j; b=i*ring+(j+1)%ring
            c=(i+1)*ring+(j+1)%ring; d=(i+1)*ring+j
            faces += [[a,b,c],[a,c,d]]
    return trimesh.Trimesh(vertices=np.array(verts), faces=np.array(faces), process=False)

class Builder:
    def __init__(self):
        self.doc = {
            'asset': {'version':'2.0','generator':'Orbit Mascot 3D Prototype Builder'},
            'scene':0, 'scenes':[{'nodes':[]}],
            'nodes':[], 'meshes':[], 'materials':[], 'accessors':[], 'bufferViews':[],
            'buffers':[{'byteLength':0}], 'animations':[],
            'extras': {
                'character':'Orbit Hoodie Mascot',
                'sampleAnimation':'wave',
                'durationSeconds':3.0,
                'notes':'True 3D articulated prototype; no Orbit logo; teal/cyan accents.'
            }
        }
        self.bin = bytearray()
        self.material_map={}
    def align(self, n=4):
        while len(self.bin)%n: self.bin.append(0)
    def add_bytes(self, data:bytes, target=None):
        self.align(4); off=len(self.bin); self.bin.extend(data); idx=len(self.doc['bufferViews'])
        bv={'buffer':0,'byteOffset':off,'byteLength':len(data)}
        if target is not None: bv['target']=target
        self.doc['bufferViews'].append(bv); return idx
    def accessor(self, arr, componentType, type_, target=None, normalized=False):
        arr=np.asarray(arr)
        bv=self.add_bytes(arr.tobytes(order='C'),target)
        count = len(arr)
        acc={'bufferView':bv,'byteOffset':0,'componentType':componentType,'count':count,'type':type_}
        if normalized: acc['normalized']=True
        if np.issubdtype(arr.dtype, np.floating):
            flat=arr.reshape((count,-1))
            acc['min']=flat.min(axis=0).astype(float).tolist(); acc['max']=flat.max(axis=0).astype(float).tolist()
        elif type_=='SCALAR':
            acc['min']=[int(arr.min())]; acc['max']=[int(arr.max())]
        idx=len(self.doc['accessors']); self.doc['accessors'].append(acc); return idx
    def material(self,name,base,metallic=0.0,roughness=0.6,emissive=None):
        if name in self.material_map: return self.material_map[name]
        mat={'name':name,'pbrMetallicRoughness':{'baseColorFactor':base,'metallicFactor':metallic,'roughnessFactor':roughness}}
        if emissive: mat['emissiveFactor']=emissive
        idx=len(self.doc['materials']); self.doc['materials'].append(mat); self.material_map[name]=idx; return idx
    def mesh(self,name,tm,material):
        verts=np.asarray(tm.vertices,dtype=np.float32)
        norms=np.asarray(tm.vertex_normals,dtype=np.float32)
        faces=np.asarray(tm.faces,dtype=np.uint32).reshape(-1)
        ap=self.accessor(verts,5126,'VEC3',34962)
        an=self.accessor(norms,5126,'VEC3',34962)
        ai=self.accessor(faces,5125,'SCALAR',34963)
        prim={'attributes':{'POSITION':ap,'NORMAL':an},'indices':ai,'material':material,'mode':4}
        idx=len(self.doc['meshes']); self.doc['meshes'].append({'name':name,'primitives':[prim]}); return idx
    def node(self,name,mesh=None,parent=None,translation=None,rotation=None,scale=None):
        n={'name':name}
        if mesh is not None:n['mesh']=mesh
        if translation is not None:n['translation']=translation
        if rotation is not None:n['rotation']=rotation
        if scale is not None:n['scale']=scale
        idx=len(self.doc['nodes']); self.doc['nodes'].append(n)
        if parent is None: self.doc['scenes'][0]['nodes'].append(idx)
        else: self.doc['nodes'][parent].setdefault('children',[]).append(idx)
        return idx
    def anim_channel(self, anim, node, path, times, values):
        ti=self.accessor(np.array(times,dtype=np.float32),5126,'SCALAR')
        vals=np.array(values,dtype=np.float32)
        typ={'translation':'VEC3','scale':'VEC3','rotation':'VEC4'}[path]
        vi=self.accessor(vals,5126,typ)
        samp=len(anim['samplers']); anim['samplers'].append({'input':ti,'output':vi,'interpolation':'LINEAR'})
        anim['channels'].append({'sampler':samp,'target':{'node':node,'path':path}})
    def save(self):
        self.doc['buffers'][0]['byteLength']=len(self.bin)
        gltf_doc=json.loads(json.dumps(self.doc))
        gltf_doc['buffers'][0]['uri']='data:application/octet-stream;base64,'+base64.b64encode(self.bin).decode('ascii')
        OUT_GLTF.write_text(json.dumps(gltf_doc,separators=(',',':')),encoding='utf-8')
        j=json.dumps(self.doc,separators=(',',':')).encode('utf-8')
        while len(j)%4:j+=b' '
        b=bytes(self.bin)
        while len(b)%4:b+=b'\x00'
        total=12+8+len(j)+8+len(b)
        with OUT_GLB.open('wb') as f:
            f.write(struct.pack('<4sII',b'glTF',2,total))
            f.write(struct.pack('<I4s',len(j),b'JSON')); f.write(j)
            f.write(struct.pack('<I4s',len(b),b'BIN\x00')); f.write(b)

B=Builder()
cream=B.material('Warm Ivory Hoodie',[0.93,0.90,0.86,1],0.0,0.72)
cream_dark=B.material('Hoodie Shadow',[0.73,0.69,0.66,1],0.0,0.8)
teal=B.material('Ocean Teal',[0.02,0.53,0.61,1],0.05,0.38)
teal_dark=B.material('Deep Teal',[0.01,0.22,0.27,1],0.05,0.35)
visor=B.material('Gloss Visor',[0.004,0.008,0.015,1],0.45,0.08)
eye=B.material('Expression Cyan',[0.03,0.95,1.0,1],0.0,0.18,[0.03,0.85,1.0])
sole=B.material('Soft Sole',[0.55,0.56,0.57,1],0.0,0.75)

root=B.node('OrbitMascot_Root')
torso_mesh=B.mesh('HoodieTorso',sphere((0.86,1.02,0.55),subdivisions=3),cream)
torso=B.node('Torso',torso_mesh,root,translation=[0,2.35,0])
pocket_mesh=B.mesh('KangarooPocket',sphere((0.56,0.27,0.13),center=(0,-0.22,0),subdivisions=2),cream_dark)
B.node('KangarooPocket',pocket_mesh,torso,translation=[0,0,0.53])
for x,name in [(-0.72,'LeftSeamAccent'),(0.72,'RightSeamAccent')]:
    accent_mesh=B.mesh(name,capsule_y(0.58,0.055),teal)
    B.node(name,accent_mesh,torso,translation=[x,-0.05,0.48])
for x,name in [(-0.18,'LeftDrawstring'),(0.18,'RightDrawstring')]:
    s=B.mesh(name,cylinder_y(0.45,0.025),cream_dark)
    B.node(name,s,torso,translation=[x,0.72,0.5])
    tip=B.mesh(name+'Tip',sphere((0.06,0.08,0.06),subdivisions=2),teal)
    B.node(name+'Tip',tip,torso,translation=[x,0.49,0.5])

head=B.node('Head',parent=torso,translation=[0,1.55,0])
B.node('HeadShell',B.mesh('HeadShell',sphere((1.07,0.93,0.62),subdivisions=3),cream),head)
B.node('HoodRing',B.mesh('HoodRing',torus(R=0.88,r=0.17,segR=72,segr=18,scale=(1.08,0.88,0.72),center=(0,-0.02,0.40)),cream),head)
B.node('Visor',B.mesh('Visor',sphere((0.88,0.68,0.28),center=(0,-0.02,0.54),subdivisions=3),visor),head)
for x,name in [(-0.32,'Eye_L'),(0.32,'Eye_R')]:
    eye_parent=B.node(name,parent=head,translation=[x,0.03,0.84])
    e=B.mesh(name+'_Glow',arc_tube(radius=0.18,tube=0.035,angle0=math.radians(205),angle1=math.radians(335)),eye)
    B.node(name+'_Glow',e,eye_parent)

def arm_mesh(name,total=0.92,r=0.17): return B.mesh(name,capsule_y(total,r),cream)
def cuff_mesh(name): return B.mesh(name,cylinder_y(0.20,0.19),teal_dark)
def hand_mesh(name): return B.mesh(name,sphere((0.25,0.30,0.20),center=(0,-0.20,0),subdivisions=2),cream)

lua=B.node('UpperArm_L',arm_mesh('UpperArm_L_Mesh'),torso,translation=[-0.92,0.58,0.0],rotation=[0,0,math.sin(math.radians(-7)/2),math.cos(math.radians(-7)/2)])
lf=B.node('Forearm_L',arm_mesh('Forearm_L_Mesh',0.82,0.16),lua,translation=[0,-0.72,0])
B.node('Cuff_L',cuff_mesh('Cuff_L_Mesh'),lf,translation=[0,-0.58,0])
B.node('Hand_L',hand_mesh('Hand_L_Mesh'),lf,translation=[0,-0.71,0.03])

rua=B.node('UpperArm_R',arm_mesh('UpperArm_R_Mesh'),torso,translation=[0.92,0.58,0.0])
rf=B.node('Forearm_R',arm_mesh('Forearm_R_Mesh',0.78,0.16),rua,translation=[0,-0.70,0])
B.node('Cuff_R',cuff_mesh('Cuff_R_Mesh'),rf,translation=[0,-0.55,0])
hand_r=B.node('Hand_R',hand_mesh('Hand_R_Mesh'),rf,translation=[0,-0.69,0.02])
for i,(x,z) in enumerate([(-0.15,0.02),(-0.05,0.04),(0.05,0.04),(0.15,0.02)]):
    fm=B.mesh(f'Finger_R_{i}_Mesh',capsule_y(0.34,0.055),cream)
    B.node(f'Finger_R_{i}',fm,hand_r,translation=[x,-0.24,z])
thumb=B.mesh('Thumb_R_Mesh',capsule_y(0.28,0.065),cream)
B.node('Thumb_R',thumb,hand_r,translation=[-0.23,-0.11,0.0],rotation=[0,0,math.sin(math.radians(-45)/2),math.cos(math.radians(-45)/2)])

def leg(name): return B.mesh(name,capsule_y(1.0,0.20),cream_dark)
def shoe(name): return B.mesh(name,sphere((0.43,0.25,0.58),subdivisions=2),cream)
def sole_mesh(name): return B.mesh(name,sphere((0.41,0.09,0.55),subdivisions=2),sole)
for x,suffix in [(-0.42,'L'),(0.42,'R')]:
    B.node('Leg_'+suffix,leg('Leg_'+suffix+'_Mesh'),root,translation=[x,1.40,0])
    sh=B.node('Shoe_'+suffix,shoe('Shoe_'+suffix+'_Mesh'),root,translation=[x,0.46,0.16])
    B.node('Sole_'+suffix,sole_mesh('Sole_'+suffix+'_Mesh'),sh,translation=[0,-0.20,0.02])
    strap=B.mesh('ShoeAccent_'+suffix+'_Mesh',torus(R=0.25,r=0.055,segR=30,segr=10,scale=(1.1,0.48,1),arc=math.radians(155)),teal)
    B.node('ShoeAccent_'+suffix,strap,sh,translation=[0,0.03,0.53],rotation=[0,0,math.sin(math.radians(12)/2),math.cos(math.radians(12)/2)])

def quat_xyz(rx,ry,rz):
    cx,sx=math.cos(rx/2),math.sin(rx/2); cy,sy=math.cos(ry/2),math.sin(ry/2); cz,sz=math.cos(rz/2),math.sin(rz/2)
    return [sx*cy*cz + cx*sy*sz, cx*sy*cz - sx*cy*sz, cx*cy*sz + sx*sy*cz, cx*cy*cz - sx*sy*sz]

anim={'name':'Wave_Hello_3s','samplers':[],'channels':[],'extras':{'state':'wave','loopRecommended':False}}
B.anim_channel(anim,torso,'translation',[0,0.55,1.1,1.7,2.3,3.0],[[0,2.35,0],[0,2.40,0],[0,2.35,0],[0,2.39,0],[0,2.35,0],[0,2.35,0]])
B.anim_channel(anim,head,'rotation',[0,0.45,1.0,1.55,2.2,3.0],[quat_xyz(0,0,0),quat_xyz(0,0,math.radians(-4)),quat_xyz(math.radians(2),0,math.radians(3)),quat_xyz(0,0,math.radians(-3)),quat_xyz(0,0,0),quat_xyz(0,0,0)])
B.anim_channel(anim,rua,'rotation',[0,0.35,0.7,2.35,2.75,3.0],[quat_xyz(0,0,0),quat_xyz(math.radians(-8),0,math.radians(30)),quat_xyz(math.radians(-10),0,math.radians(38)),quat_xyz(math.radians(-10),0,math.radians(38)),quat_xyz(math.radians(-5),0,math.radians(18)),quat_xyz(0,0,0)])
B.anim_channel(anim,rf,'rotation',[0,0.35,0.7,1.0,1.3,1.6,1.9,2.2,2.4,2.75,3.0],[quat_xyz(0,0,0),quat_xyz(0,0,math.radians(85)),quat_xyz(0,0,math.radians(125)),quat_xyz(0,0,math.radians(115)),quat_xyz(0,0,math.radians(140)),quat_xyz(0,0,math.radians(112)),quat_xyz(0,0,math.radians(138)),quat_xyz(0,0,math.radians(115)),quat_xyz(0,0,math.radians(128)),quat_xyz(0,0,math.radians(70)),quat_xyz(0,0,0)])
B.anim_channel(anim,hand_r,'rotation',[0,0.7,0.95,1.2,1.45,1.7,1.95,2.2,2.45,2.75,3.0],[quat_xyz(0,0,0),quat_xyz(0,math.radians(-8),math.radians(-8)),quat_xyz(0,math.radians(8),math.radians(16)),quat_xyz(0,math.radians(-8),math.radians(-16)),quat_xyz(0,math.radians(8),math.radians(16)),quat_xyz(0,math.radians(-8),math.radians(-16)),quat_xyz(0,math.radians(8),math.radians(16)),quat_xyz(0,math.radians(-8),math.radians(-12)),quat_xyz(0,0,0),quat_xyz(0,0,0),quat_xyz(0,0,0)])
for eye_name in ['Eye_L','Eye_R']:
    idx=next(i for i,n in enumerate(B.doc['nodes']) if n.get('name')==eye_name)
    B.anim_channel(anim,idx,'scale',[0,1.15,1.23,1.31,2.05,2.13,2.21,3.0],[[1,1,1],[1,1,1],[1,0.12,1],[1,1,1],[1,1,1],[1,0.12,1],[1,1,1],[1,1,1]])
B.doc['animations'].append(anim)
B.save()
print(OUT_GLB, OUT_GLTF)