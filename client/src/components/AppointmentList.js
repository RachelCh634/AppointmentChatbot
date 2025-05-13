import { useState, useRef, useEffect } from 'react';
import { Box, Typography, Paper, Avatar, CircularProgress } from '@mui/material';
import { keyframes } from '@mui/system';
import SmartToyIcon from '@mui/icons-material/SmartToy';
import PersonIcon from '@mui/icons-material/Person';
import GoogleIcon from '@mui/icons-material/Google';
import EventIcon from '@mui/icons-material/Event';
import axios from 'axios';
import ParticlesBackground from './ParticlesBackground';

const fadeIn = keyframes`
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
`;

const AppointmentList = () => {
  const [appointments, setAppointments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const messagesEndRef = useRef(null);

  const handleLoginSuccess = (userData) => {
    console.log('Login successful:', userData);
    window.location.reload();
  };

  const handleLogout = () => {
    console.log('Logged out');
    localStorage.removeItem('doctorToken');
    window.location.href = '/';
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [appointments]);

  useEffect(() => {
    const fetchAppointments = async () => {
      try {
        const token = localStorage.getItem('doctorToken');

        if (!token) {
          setError('Authentication required');
          setLoading(false);
          return;
        }

        const response = await axios.get('http://localhost:5000/upcoming-appointments', {
          headers: {
            Authorization: `Bearer ${token}`
          },
          params: {
            days: 30
          }
        });

        let appointmentsData = response.data || [];

        if (!Array.isArray(appointmentsData)) {
          if (appointmentsData.appointments && Array.isArray(appointmentsData.appointments)) {
            appointmentsData = appointmentsData.appointments;
          } else {
            appointmentsData = [];
          }
        }

        setAppointments(appointmentsData);
        setLoading(false);
      } catch (err) {
        console.error('Error fetching appointments:', err);
        setError('Failed to load appointments');
        setLoading(false);
      }
    };

    fetchAppointments();
  }, []);

  const formatDate = (isoString) => {
    const date = new Date(isoString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const formatTime = (isoString) => {
    const date = new Date(isoString);
    return date.toLocaleTimeString('he-IL', {
      hour: '2-digit',
      minute: '2-digit',
      hour12: false
    });
  };

  const getDayOfWeek = (isoString) => {
    const date = new Date(isoString);
    const days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
    return days[date.getDay()];
  };

  const createMessages = () => {
    const messages = [];

    messages.push({
      text: 'Hello Doctor! Here are your upcoming appointments for the next 30 days.',
      sender: 'bot'
    });

    if (!appointments || appointments.length === 0) {
      messages.push({
        text: 'You don\'t have any upcoming appointments scheduled.',
        sender: 'bot'
      });
    } else {
      appointments.forEach(appointment => {
        const date = new Date(appointment.start);
        const today = new Date();
        const isToday = date.toDateString() === today.toDateString();
        const isTomorrow = new Date(today.setDate(today.getDate() + 1)).toDateString() === date.toDateString();

        let dateLabel = formatDate(appointment.start);
        if (isToday) dateLabel = "Today";
        if (isTomorrow) dateLabel = "Tomorrow";

        const appointmentText = `Patient: ${appointment.user_name}\nTime: ${formatTime(appointment.start)}\nDate: ${dateLabel} (${getDayOfWeek(appointment.start)})`;

        messages.push({
          text: appointmentText,
          sender: 'user',
          appointment: true
        });
      });

      messages.push({
        text: `That's all for now. You have ${appointments.length} upcoming appointment${appointments.length !== 1 ? 's' : ''}.`,
        sender: 'bot'
      });
    }

    return messages;
  };

  if (loading) {
    return (
      <ParticlesBackground onLoginSuccess={handleLoginSuccess} onLogout={handleLogout}>
        <Box sx={{
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
          alignItems: 'center',
          height: '100vh',
          gap: 3
        }}>
          <CircularProgress 
            size={60} 
            thickness={4} 
            sx={{ 
              color: '#6b5ce7',
              animation: 'pulse 1.5s ease-in-out infinite',
              '@keyframes pulse': {
                '0%': { opacity: 0.6, transform: 'scale(0.95)' },
                '50%': { opacity: 1, transform: 'scale(1.05)' },
                '100%': { opacity: 0.6, transform: 'scale(0.95)' },
              }
            }} 
          />
          <Typography 
            variant="h5" 
            sx={{ 
              color: '#6b5ce7', 
              fontWeight: 500,
              textAlign: 'center',
              animation: 'fadeIn 1.5s infinite alternate',
              '@keyframes fadeIn': {
                '0%': { opacity: 0.7 },
                '100%': { opacity: 1 },
              }
            }}
          >
          </Typography>
        </Box>
      </ParticlesBackground>
    );
  }

  if (error) {
    return (
      <ParticlesBackground onLoginSuccess={handleLoginSuccess} onLogout={handleLogout}>
        <Box sx={{
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
          alignItems: 'center',
          height: '100vh',
          p: 3
        }}>
          <Typography variant="h5" color="error" gutterBottom>
            {error}
          </Typography>
        </Box>
      </ParticlesBackground>
    );
  }

  const messages = createMessages();

  return (
    <ParticlesBackground onLoginSuccess={handleLoginSuccess} onLogout={handleLogout}>
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
          height: '85vh',
          maxWidth: '450px',
          margin: 'auto',
          backgroundColor: 'rgba(248, 249, 250, 0.85)',
          padding: 2,
          borderRadius: 4,
          boxShadow: '0 10px 30px rgba(0, 0, 0, 0.1)',
          marginTop: '7vh',
          fontFamily: '"Segoe UI", Roboto, "Helvetica Neue", sans-serif',
          backdropFilter: 'blur(5px)',
        }}
      >
        <Box
          sx={{
            display: 'flex',
            alignItems: 'center',
            padding: 2,
            borderRadius: '16px 16px 0 0',
            backgroundColor: '#6b5ce7',
            color: 'white',
            boxShadow: '0 2px 5px rgba(0,0,0,0.1)',
            marginBottom: 2,
          }}
        >
          <Avatar sx={{ bgcolor: '#5346c7', marginRight: 2 }}>
            <EventIcon />
          </Avatar>
          <Box>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <Typography variant="h6" sx={{ fontWeight: 500, fontSize: '1.1rem', mr: 1 }}>
                Appointment List
              </Typography>
            </Box>
            <Typography variant="body2" sx={{ opacity: 0.8 }}>
              Your upcoming schedule
            </Typography>
          </Box>
          <Box sx={{ ml: 'auto', display: 'flex', alignItems: 'center' }}>
            <Typography variant="body2" sx={{ opacity: 0.8 }}>
              {localStorage.getItem('doctorName') || 'Doctor'}
            </Typography>
            <Avatar
              sx={{
                bgcolor: '#4285F4',
                width: 24,
                height: 24,
                ml: 1,
                fontSize: '0.8rem'
              }}
            >
              <GoogleIcon sx={{ fontSize: 14 }} />
            </Avatar>
          </Box>
        </Box>

        <Paper
          elevation={0}
          sx={{
            padding: 2,
            flexGrow: 1,
            overflowY: 'auto',
            backgroundColor: 'rgba(255, 255, 255, 0.8)',
            borderRadius: 3,
            display: 'flex',
            flexDirection: 'column',
            gap: 1.5,
            '&::-webkit-scrollbar': {
              width: '8px',
            },
            '&::-webkit-scrollbar-thumb': {
              backgroundColor: '#d1d1d1',
              borderRadius: '4px',
            },
          }}
        >
          {messages.length === 0 && (
            <Box
              sx={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                height: '100%',
                opacity: 0.7,
              }}
            >
              <EventIcon sx={{ fontSize: 60, color: '#6b5ce7', mb: 2 }} />
              <Typography variant="body1" sx={{ textAlign: 'center', color: '#666' }}>
                Loading your appointments...
              </Typography>
            </Box>
          )}

          {messages.map((message, index) => (
            <Box
              key={index}
              sx={{
                display: 'flex',
                justifyContent: message.sender === 'user' ? 'flex-end' : 'flex-start',
                animation: `${fadeIn} 0.3s ease-out`,
              }}
            >
              {message.sender === 'bot' && (
                <Avatar
                  sx={{
                    bgcolor: '#6b5ce7',
                    width: 32,
                    height: 32,
                    mr: 1,
                    alignSelf: 'flex-end',
                    mb: 0.5
                  }}
                >
                  <SmartToyIcon sx={{ fontSize: 18 }} />
                </Avatar>
              )}

              <Box
                sx={{
                  padding: 1.2,
                  maxWidth: '75%',
                  backgroundColor: message.sender === 'user' ? '#6b5ce7' : '#f0f2f5',
                  color: message.sender === 'user' ? 'white' : 'black',
                  borderRadius: message.sender === 'user'
                    ? '18px 18px 4px 18px'
                    : '18px 18px 18px 4px',
                  boxShadow: '0 1px 2px rgba(0,0,0,0.1)',
                  wordBreak: 'break-word',
                  fontWeight: 300,
                  fontSize: '0.9rem',
                  fontFamily: '"Poppins", "Segoe UI", Roboto, sans-serif',
                  whiteSpace: 'pre-wrap',
                }}
              >
                {message.text}
              </Box>

              {message.sender === 'user' && (
                <Avatar
                  sx={{
                    bgcolor: message.appointment ? '#4caf50' : '#e91e63',
                    width: 32,
                    height: 32,
                    ml: 1,
                    alignSelf: 'flex-end',
                    mb: 0.5
                  }}
                >
                  {message.appointment ? <EventIcon sx={{ fontSize: 18 }} /> : <PersonIcon sx={{ fontSize: 18 }} />}
                </Avatar>
              )}
            </Box>
          ))}
          <div ref={messagesEndRef} />
        </Paper>

        <Box
          sx={{
            display: 'flex',
            gap: 1,
            marginTop: 2,
            position: 'relative',
            justifyContent: 'center',
            padding: 1,
            backgroundColor: '#f5f5f5',
            borderRadius: 2,
          }}
        >
        </Box>
      </Box>
    </ParticlesBackground>
  );
};

export default AppointmentList;
