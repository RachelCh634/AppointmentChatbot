import { useState } from 'react';
import { Button, Box, Typography, Paper, Tooltip, Fade, Popper, ClickAwayListener } from '@mui/material';
import AccessTimeIcon from '@mui/icons-material/AccessTime';
import GoogleIcon from '@mui/icons-material/Google';
import { useGoogleLogin } from '@react-oauth/google';
import axios from 'axios';

const SideButtons = ({ onLoginSuccess, onLogout }) => {
  const [openHours, setOpenHours] = useState(false);
  const [anchorEl, setAnchorEl] = useState(null);
  const isLoggedIn = !!localStorage.getItem('token');

  const login = useGoogleLogin({
    onSuccess: async (response) => {
      try {
        const serverResponse = await axios.post('http://localhost:5000/google-login', {
          googleToken: response.access_token
        });
        const token = serverResponse.data.token;
        const userName = serverResponse.data.userName;
        localStorage.setItem('userName', userName);
        localStorage.setItem('token', token);
        onLoginSuccess();
      } catch (error) {
        console.error('Login error:', error);
      }
    },
    onError: () => {
      console.error('Google login error');
    }
  });

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('userName');
    onLogout();
  };

  const handleOpenHoursClick = (event) => {
    setAnchorEl(event.currentTarget);
    setOpenHours(!openHours);
  };

  const handleClickAway = () => {
    setOpenHours(false);
  };

  return (
    <ClickAwayListener onClickAway={handleClickAway}>
      <Box
        sx={{
          position: 'fixed',
          left: '30px',
          top: '50%',
          transform: 'translateY(-50%)',
          zIndex: 10,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          gap: 2,
        }}
      >
        <Tooltip title={isLoggedIn ? 'Sign out' : 'Sign in with Google'} placement="right">
          <Button
            onClick={isLoggedIn ? handleLogout : login}
            sx={{
              width: '60px',
              height: '60px',
              borderRadius: '50%',
              backgroundColor: '#6b5ce7',
              color: 'white',
              boxShadow: '0 4px 10px rgba(107, 92, 231, 0.3)',
              '&:hover': {
                backgroundColor: '#5346c7',
              },
              transition: 'all 0.2s ease-in-out',
            }}
          >
            <GoogleIcon fontSize="large" />
          </Button>
        </Tooltip>

        <Tooltip title="Opening Hours" placement="right">
          <Button
            onClick={handleOpenHoursClick}
            sx={{
              width: '60px',
              height: '60px',
              borderRadius: '50%',
              backgroundColor: '#6b5ce7',
              color: 'white',
              boxShadow: '0 4px 10px rgba(107, 92, 231, 0.3)',
              '&:hover': {
                backgroundColor: '#5346c7',
              },
              transition: 'all 0.2s ease-in-out',
            }}
          >
            <AccessTimeIcon fontSize="large" />
          </Button>
        </Tooltip>

        <Popper
          open={openHours}
          anchorEl={anchorEl}
          placement="right-start"
          transition
          sx={{ zIndex: 1200 }}
        >
          {({ TransitionProps }) => (
            <Fade {...TransitionProps} timeout={350}>
              <Paper
                elevation={4}
                sx={{
                  p: 3,
                  mt: 1.5,
                  ml: 1.5,
                  width: 250,
                  borderRadius: 3,
                  backgroundColor: 'white',
                  boxShadow: '0 10px 30px rgba(0, 0, 0, 0.1)',
                }}
              >
                <Typography variant="h6" sx={{
                  fontWeight: 500,
                  fontSize: '1rem',
                  color: '#6b5ce7',
                  mb: 2,
                  textAlign: 'center',
                  fontFamily: '"Poppins", "Segoe UI", Roboto, sans-serif',
                  letterSpacing: '0.5px'
                }}>
                  Opening Hours
                </Typography>
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.8 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                    <Typography variant="body2" sx={{
                      fontWeight: 500,
                      fontSize: '0.85rem',
                      fontFamily: '"Poppins", "Segoe UI", Roboto, sans-serif'
                    }}>
                      Sunday - Thursday:
                    </Typography>
                    <Typography variant="body2" sx={{
                      fontSize: '0.85rem',
                      fontWeight: 400,
                      fontFamily: '"Poppins", "Segoe UI", Roboto, sans-serif'
                    }}>
                      08:00 - 19:00
                    </Typography>
                  </Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                    <Typography variant="body2" sx={{
                      fontWeight: 500,
                      fontSize: '0.85rem',
                      fontFamily: '"Poppins", "Segoe UI", Roboto, sans-serif'
                    }}>
                      Friday:
                    </Typography>
                    <Typography variant="body2" sx={{
                      fontSize: '0.85rem',
                      fontWeight: 400,
                      fontFamily: '"Poppins", "Segoe UI", Roboto, sans-serif'
                    }}>
                      08:00 - 12:00
                    </Typography>
                  </Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                    <Typography variant="body2" sx={{
                      fontWeight: 500,
                      fontSize: '0.85rem',
                      fontFamily: '"Poppins", "Segoe UI", Roboto, sans-serif'
                    }}>
                      Saturday:
                    </Typography>
                    <Typography variant="body2" sx={{
                      fontSize: '0.85rem',
                      fontWeight: 400,
                      fontFamily: '"Poppins", "Segoe UI", Roboto, sans-serif'
                    }}>
                      Closed
                    </Typography>
                  </Box>
                  <Box sx={{ mt: 1.5, pt: 1.5, borderTop: '1px solid #eee' }}>
                    <Typography variant="body2" sx={{
                      color: '#666',
                      textAlign: 'center',
                      fontSize: '0.75rem',
                      fontWeight: 400,
                      fontFamily: '"Poppins", "Segoe UI", Roboto, sans-serif'
                    }}>
                      Customer Service: 03-1234567
                    </Typography>
                  </Box>
                </Box>
              </Paper>
            </Fade>
          )}
        </Popper>
      </Box>
    </ClickAwayListener>
  );
};

export default SideButtons;
