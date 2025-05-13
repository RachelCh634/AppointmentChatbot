import { useState, useEffect } from 'react';
import { Button, Box, Typography, Paper, Tooltip, Fade, Popper, ClickAwayListener, TextField, InputAdornment, CircularProgress } from '@mui/material';
import AccessTimeIcon from '@mui/icons-material/AccessTime';
import GoogleIcon from '@mui/icons-material/Google';
import MedicalServicesIcon from '@mui/icons-material/MedicalServices';
import PersonIcon from '@mui/icons-material/Person';
import LockIcon from '@mui/icons-material/Lock';
import LogoutIcon from '@mui/icons-material/Logout';
import { useGoogleLogin } from '@react-oauth/google';
import axios from 'axios';

const SideButtons = ({ onLoginSuccess, onLogout }) => {
  const [openHours, setOpenHours] = useState(false);
  const [openDoctorLogin, setOpenDoctorLogin] = useState(false);
  const [anchorEl, setAnchorEl] = useState(null);
  const [doctorAnchorEl, setDoctorAnchorEl] = useState(null);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [loginError, setLoginError] = useState('');

  const isUserLoggedIn = !!localStorage.getItem('token');
  const isDoctorLoggedIn = !!localStorage.getItem('doctorToken');

  useEffect(() => {
    if (!openDoctorLogin) {
      setUsername('');
      setPassword('');
      setLoginError('');
    }
  }, [openDoctorLogin]);

  const login = useGoogleLogin({
    onSuccess: async (response) => {
      try {
        if (isDoctorLoggedIn) {
          handleDoctorLogout();
        }

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

  const handleDoctorLogout = () => {
    localStorage.removeItem('doctorToken');
    localStorage.removeItem('doctorName');
    localStorage.removeItem('doctorSpecialty');
    window.location.reload();
  };

  const handleOpenHoursClick = (event) => {
    setAnchorEl(event.currentTarget);
    setOpenHours(!openHours);
    setOpenDoctorLogin(false);
  };

  const handleClickAway = () => {
    setOpenHours(false);
    setOpenDoctorLogin(false);
  };

  const handleDoctorClick = (event) => {
    if (isDoctorLoggedIn) {
      handleDoctorLogout();
      return;
    }

    setDoctorAnchorEl(event.currentTarget);
    setOpenDoctorLogin(!openDoctorLogin);
    setOpenHours(false);
    setLoginError('');
  };

  const handleDoctorLogin = async () => {
    if (!username || !password) {
      setLoginError('Please enter both username and password');
      return;
    }

    setIsLoading(true);
    setLoginError('');

    try {
      if (isUserLoggedIn) {
        handleLogout();
      }

      const response = await axios.post('http://localhost:5000/doctor-login', {
        username,
        password
      });

      if (response.data.success) {
        localStorage.setItem('doctorToken', response.data.token);
        localStorage.setItem('doctorName', response.data.doctorName);

        setOpenDoctorLogin(false);
        setUsername('');
        setPassword('');
        window.location.reload();
      } else {
        setLoginError(response.data.message || 'Login failed');
      }
    } catch (error) {
      console.error('Doctor login error:', error);
      setLoginError(error.response?.data?.message || 'An error occurred during login');
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (event) => {
    if (event.key === 'Enter') {
      handleDoctorLogin();
    }
  };

  const isUserLoginDisabled = isDoctorLoggedIn;
  const isDoctorLoginDisabled = isUserLoggedIn;

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
        <Tooltip title={isDoctorLoggedIn ? "Sign out" : (isDoctorLoginDisabled ? "Please sign out first" : "Doctor Login")} placement="right">
          <span>
            <Button
              onClick={handleDoctorClick}
              disabled={!isDoctorLoggedIn && isDoctorLoginDisabled}
              sx={{
                width: '60px',
                height: '60px',
                borderRadius: '50%',
                backgroundColor: isDoctorLoggedIn ? '#4caf50' : '#6b5ce7',
                color: 'white',
                boxShadow: isDoctorLoggedIn
                  ? '0 4px 10px rgba(76, 175, 80, 0.3)'
                  : '0 4px 10px rgba(107, 92, 231, 0.3)',
                '&:hover': {
                  backgroundColor: isDoctorLoggedIn ? '#43a047' : '#5346c7',
                  transform: 'translateY(-3px)',
                  boxShadow: isDoctorLoggedIn
                    ? '0 6px 15px rgba(76, 175, 80, 0.4)'
                    : '0 6px 15px rgba(107, 92, 231, 0.4)',
                },
                '&.Mui-disabled': {
                  backgroundColor: '#bdbdbd',
                  color: '#757575',
                  boxShadow: 'none',
                },
                transition: 'all 0.3s ease-in-out',
              }}
            >
              {isDoctorLoggedIn ? <LogoutIcon fontSize="large" /> : <MedicalServicesIcon fontSize="large" />}
            </Button>
          </span>
        </Tooltip>

        <Tooltip title={isUserLoggedIn ? 'Sign out' : (isUserLoginDisabled ? 'Please sign out first' : 'Sign in with Google')} placement="right">
          <span>
            <Button
              onClick={isUserLoggedIn ? handleLogout : login}
              disabled={!isUserLoggedIn && isUserLoginDisabled}
              sx={{
                width: '60px',
                height: '60px',
                borderRadius: '50%',
                backgroundColor: '#6b5ce7',
                color: 'white',
                boxShadow: '0 4px 10px rgba(107, 92, 231, 0.3)',
                '&:hover': {
                  backgroundColor: '#5346c7',
                  transform: 'translateY(-3px)',
                  boxShadow: '0 6px 15px rgba(107, 92, 231, 0.4)',
                },
                '&.Mui-disabled': {
                  backgroundColor: '#bdbdbd',
                  color: '#757575',
                  boxShadow: 'none',
                },
                transition: 'all 0.3s ease-in-out',
              }}
            >
              <GoogleIcon fontSize="large" />
            </Button>
          </span>
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
                transform: 'translateY(-3px)',
                boxShadow: '0 6px 15px rgba(107, 92, 231, 0.4)',
              },
              transition: 'all 0.3s ease-in-out',
            }}
          >
            <AccessTimeIcon fontSize="large" />
          </Button>
        </Tooltip>

        <Popper
          open={openDoctorLogin && !isDoctorLoggedIn && !isUserLoggedIn}
          anchorEl={doctorAnchorEl}
          placement="right-start"
          transition
          sx={{ zIndex: 1200 }}
        >
          {({ TransitionProps }) => (
            <Fade {...TransitionProps} timeout={350}>
              <Paper
                elevation={8}
                sx={{
                  p: 3,
                  mt: 1.5,
                  ml: 1.5,
                  width: 300,
                  borderRadius: 3,
                  backgroundColor: 'white',
                  boxShadow: '0 10px 30px rgba(0, 0, 0, 0.15)',
                  border: '1px solid rgba(107, 92, 231, 0.1)',
                  overflow: 'hidden',
                  position: 'relative',
                  '&::before': {
                    content: '""',
                    position: 'absolute',
                    top: 0,
                    left: 0,
                    right: 0,
                    height: '4px',
                    background: 'linear-gradient(90deg, #6b5ce7, #a78bfa)',
                  }
                }}
              >
                <Typography variant="h6" sx={{
                  fontWeight: 600,
                  fontSize: '1.2rem',
                  color: '#6b5ce7',
                  mb: 3,
                  textAlign: 'center',
                  fontFamily: '"Poppins", "Segoe UI", Roboto, sans-serif',
                  letterSpacing: '0.5px'
                }}>
                  Doctor Login
                </Typography>
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2.5 }}>
                  <TextField
                    label="Username"
                    variant="outlined"
                    fullWidth
                    size="small"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    InputProps={{
                      startAdornment: (
                        <InputAdornment position="start">
                          <PersonIcon sx={{ color: '#6b5ce7' }} />
                        </InputAdornment>
                      ),
                      sx: {
                        borderRadius: 2,
                        '&:hover .MuiOutlinedInput-notchedOutline': {
                          borderColor: '#6b5ce7',
                        },
                        '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
                          borderColor: '#6b5ce7',
                        }
                      }
                    }}
                    sx={{
                      '& .MuiInputLabel-root.Mui-focused': {
                        color: '#6b5ce7',
                      }
                    }}
                    disabled={isLoading}
                  />
                  <TextField
                    label="Password"
                    type="password"
                    variant="outlined"
                    fullWidth
                    size="small"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    onKeyPress={handleKeyPress}
                    InputProps={{
                      startAdornment: (
                        <InputAdornment position="start">
                          <LockIcon sx={{ color: '#6b5ce7' }} />
                        </InputAdornment>
                      ),
                      sx: {
                        borderRadius: 2,
                        '&:hover .MuiOutlinedInput-notchedOutline': {
                          borderColor: '#6b5ce7',
                        },
                        '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
                          borderColor: '#6b5ce7',
                        }
                      }
                    }}
                    sx={{
                      '& .MuiInputLabel-root.Mui-focused': {
                        color: '#6b5ce7',
                      }
                    }}
                    disabled={isLoading}
                  />

                  {loginError && (
                    <Typography variant="caption" sx={{
                      color: '#f44336',
                      textAlign: 'center',
                      fontSize: '0.75rem',
                      fontWeight: 500,
                      mt: -1.5
                    }}>
                      {loginError}
                    </Typography>
                  )}

                  <Button
                    variant="contained"
                    fullWidth
                    onClick={handleDoctorLogin}
                    disabled={isLoading}
                    sx={{
                      mt: 1,
                      py: 1.2,
                      backgroundColor: '#6b5ce7',
                      borderRadius: 2,
                      textTransform: 'none',
                      fontWeight: 600,
                      letterSpacing: '0.5px',
                      boxShadow: '0 4px 10px rgba(107, 92, 231, 0.3)',
                      '&:hover': {
                        backgroundColor: '#5346c7',
                        boxShadow: '0 6px 15px rgba(107, 92, 231, 0.4)',
                      },
                      transition: 'all 0.3s ease',
                      position: 'relative',
                    }}
                  >
                    {isLoading ? (
                      <CircularProgress size={24} sx={{ color: 'white' }} />
                    ) : (
                      'Login'
                    )}
                  </Button>

                  <Typography variant="caption" sx={{
                    color: '#666',
                    textAlign: 'center',
                    fontSize: '0.75rem',
                    fontWeight: 400,
                    fontFamily: '"Poppins", "Segoe UI", Roboto, sans-serif',
                    mt: -1
                  }}>
                    Secure access for medical staff only
                  </Typography>
                </Box>
              </Paper>
            </Fade>
          )}
        </Popper>

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
                elevation={8}
                sx={{
                  p: 3,
                  mt: 1.5,
                  ml: 1.5,
                  width: 250,
                  borderRadius: 3,
                  backgroundColor: 'white',
                  boxShadow: '0 10px 30px rgba(0, 0, 0, 0.15)',
                  border: '1px solid rgba(107, 92, 231, 0.1)',
                  overflow: 'hidden',
                  position: 'relative',
                  '&::before': {
                    content: '""',
                    position: 'absolute',
                    top: 0,
                    left: 0,
                    right: 0,
                    height: '4px',
                    background: 'linear-gradient(90deg, #6b5ce7, #a78bfa)',
                  }
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
