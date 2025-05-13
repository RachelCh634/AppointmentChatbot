import React from 'react';
import { Box } from '@mui/material';
import Particles from "react-tsparticles";
import { loadFull } from "tsparticles";
import SideButtons from './SideButtons';

const ParticlesBackground = ({ children, onLoginSuccess, onLogout }) => {
  const particlesInit = async (main) => {
    await loadFull(main);
  };

  return (
    <Box sx={{ 
      minHeight: '100vh',
      background: '#f8f9fa',
      position: 'relative',
      overflow: 'hidden'
    }}>
      <Particles
        id="tsparticles"
        init={particlesInit}
        options={{
          background: {
            color: {
              value: "#f8f9fa",
            },
          },
          fpsLimit: 60,
          particles: {
            color: {
              value: "#6b5ce7",
            },
            links: {
              color: "#6b5ce7",
              distance: 150,
              enable: true,
              opacity: 0.2,
              width: 1,
            },
            move: {
              enable: true,
              speed: 0.6,
              direction: "none",
              random: true,
              straight: false,
              outMode: "bounce",
              attract: {
                enable: false,
                rotateX: 600,
                rotateY: 1200
              }
            },
            number: {
              density: {
                enable: true,
                area: 800,
              },
              value: 100,
            },
            opacity: {
              value: 0.3,
              random: true,
            },
            size: {
              value: { min: 1, max: 3 },
              random: true,
            },
          },
          detectRetina: true,
        }}
        style={{
          position: "fixed",
          top: 0,
          left: 0,
          width: "100%",
          height: "100%",
          zIndex: -1,
        }}
      />
      <SideButtons
        onLoginSuccess={onLoginSuccess}
        onLogout={onLogout}
      />
      {children}
    </Box>
  );
};

export default ParticlesBackground;
