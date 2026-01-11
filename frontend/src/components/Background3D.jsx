import React, { useRef, useState } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { Points, PointMaterial, Stars, PerspectiveCamera } from '@react-three/drei';
import * as THREE from 'three';

function StarField({ count = 5000 }) {
  const points = useRef();
  const [positions] = useState(() => {
    const pos = new Float32Array(count * 3);
    for (let i = 0; i < count; i++) {
      pos[i * 3] = (Math.random() - 0.5) * 20;
      pos[i * 3 + 1] = (Math.random() - 0.5) * 20;
      pos[i * 3 + 2] = (Math.random() - 0.5) * 20;
    }
    return pos;
  });

    useFrame((state, delta) => {
      if (points.current) {
        // Continuous smooth falling motion
        points.current.position.y -= delta * 0.2;
        // Slow rotation for added depth
        points.current.rotation.z += delta * 0.02;
        
        // Reset position for seamless loop
        if (points.current.position.y < -10) {
          points.current.position.y = 10;
        }
      }
    });

  return (
    <Points ref={points} positions={positions} stride={3} frustumCulled={false}>
      <PointMaterial
        transparent
        color="#a78bfa"
        size={0.02}
        sizeAttenuation={true}
        depthWrite={false}
        blending={THREE.AdditiveBlending}
      />
    </Points>
  );
}

const Background3D = () => {
  return (
    <div className="fixed inset-0 w-full h-full bg-[#030712]" style={{ zIndex: 0 }}>
      <Canvas dpr={[1, 2]}>
        <PerspectiveCamera makeDefault position={[0, 0, 8]} fov={75} />
        <color attach="background" args={['#030712']} />
        
        <ambientLight intensity={0.4} />
        <pointLight position={[10, 10, 10]} intensity={1.5} color="#8b5cf6" />
        <pointLight position={[-10, -10, -10]} intensity={0.5} color="#4c1d95" />
        
        {/* Deep space stars */}
        <Stars 
          radius={100} 
          depth={50} 
          count={7000} 
          factor={4} 
          saturation={0} 
          fade 
          speed={1.5} 
        />
        
        {/* Interactive foreground stars */}
        <StarField count={4000} />
        
        {/* Subtle fog for depth */}
        <fog attach="fog" args={['#030712', 5, 20]} />
      </Canvas>
    </div>
  );
};

export default Background3D;
