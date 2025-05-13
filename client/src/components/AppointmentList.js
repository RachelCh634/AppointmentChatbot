import React, { useState, useEffect } from 'react';
import { Box, Typography, Paper, CircularProgress, Button, Grid, Card, CardContent } from '@mui/material';
import axios from 'axios';
import Particles from "react-tsparticles";
import { loadFull } from "tsparticles";

const AppointmentList = ({ doctorName = 'Doctor' }) => {
  const [appointments, setAppointments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const particlesInit = async (main) => {
    await loadFull(main);
  };

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
            days: 30 // הצג תורים ל-30 יום קדימה
          }
        });
        
        // Handle the specific format returned from server
        // Ensure appointments is always an array
        let appointmentsData = response.data || [];
        
        // Check if appointmentsData is already an array
        if (!Array.isArray(appointmentsData)) {
          console.log('Response data is not an array:', appointmentsData);
          // If it's not an array, try to extract appointments from the response
          if (appointmentsData.appointments && Array.isArray(appointmentsData.appointments)) {
            appointmentsData = appointmentsData.appointments;
          } else {
            // If we can't find an array, use an empty array
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

  // Format date from ISO string
  const formatDate = (isoString) => {
    const date = new Date(isoString);
    return date.toLocaleDateString('he-IL', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  // Format time from ISO string
  const formatTime = (isoString) => {
    const date = new Date(isoString);
    return date.toLocaleTimeString('he-IL', {
      hour: '2-digit',
      minute: '2-digit',
      hour12: false
    });
  };

  // Get day of week
  const getDayOfWeek = (isoString) => {
    const date = new Date(isoString);
    const days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
    return days[date.getDay()];
  };

  if (loading) {
    return (
      <Box sx={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '100vh',
        background: '#f8f9fa'
      }}>
        <CircularProgress size={60} sx={{ color: '#6b5ce7' }} />
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={{ 
        display: 'flex', 
        flexDirection: 'column',
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '100vh',
        p: 3,
        background: '#f8f9fa'
      }}>
        <Typography variant="h5" color="error" gutterBottom>
          {error}
        </Typography>
        <Button 
          variant="contained" 
          onClick={() => window.location.reload()}
          sx={{
            mt: 2,
            backgroundColor: '#6b5ce7',
            '&:hover': { backgroundColor: '#5346c7' }
          }}
        >
          Try Again
        </Button>
      </Box>
    );
  }

  return (
    <Box sx={{ 
      minHeight: '100vh',
      background: '#f8f9fa',
      py: 6,
      px: 3,
      position: 'relative'
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

        <Typography variant="h3" sx={{ 
          mb: 5, 
          fontWeight: 800,
          color: '#6b5ce7',
          textAlign: 'center',
          letterSpacing: '-0.5px'
        }}>
          Upcoming Appointments
        </Typography>
        
        {!appointments || appointments.length === 0 ? (
          <Box sx={{ 
            p: 5, 
            textAlign: 'center', 
            borderRadius: 3,
            backgroundColor: 'rgba(107, 92, 231, 0.05)',
            border: '2px dashed rgba(107, 92, 231, 0.3)'
          }}>
            <Typography variant="h6" sx={{ color: '#6b5ce7', fontWeight: 500 }}>
              No upcoming appointments found
            </Typography>
          </Box>
        ) : (
          <Grid container spacing={3}>
            {Array.isArray(appointments) && appointments.map((appointment, index) => {
              const date = new Date(appointment.start);
              const today = new Date();
              const isToday = date.toDateString() === today.toDateString();
              const isTomorrow = new Date(today.setDate(today.getDate() + 1)).toDateString() === date.toDateString();
              
              let dateLabel = formatDate(appointment.start);
              if (isToday) dateLabel = "Today";
              if (isTomorrow) dateLabel = "Tomorrow";
              
              return (
                <Grid item xs={12} sm={6} md={4} key={index}>
                  <Card sx={{ 
                    height: '100%',
                    borderRadius: 4, 
                    background: 'white',
                    boxShadow: '0 10px 30px rgba(107, 92, 231, 0.1)',
                    transition: 'all 0.3s ease',
                    overflow: 'hidden',
                    position: 'relative',
                    '&:hover': {
                      transform: 'translateY(-5px)',
                      boxShadow: '0 15px 35px rgba(107, 92, 231, 0.2)'
                    },
                    display: 'flex',
                    flexDirection: 'column'
                  }}>
                    <Box sx={{
                      p: 2,
                      backgroundColor: '#6b5ce7',
                      color: 'white',
                      fontWeight: 'bold',
                      textAlign: 'center',
                      letterSpacing: '1px',
                      textTransform: 'uppercase',
                      fontSize: '0.8rem'
                    }}>
                      {isToday ? 'Today' : isTomorrow ? 'Tomorrow' : getDayOfWeek(appointment.start)}
                    </Box>
                    
                    <CardContent sx={{ 
                      p: 3,
                      flexGrow: 1,
                      display: 'flex',
                      flexDirection: 'column',
                      justifyContent: 'space-between'
                    }}>
                      <Box>
                        <Typography variant="h5" sx={{ 
                          fontWeight: 700, 
                          color: '#333',
                          mb: 1,
                          textAlign: 'center'
                        }}>
                          {appointment.user_name}
                        </Typography>
                        
                        <Typography variant="h4" sx={{ 
                          fontWeight: 800, 
                          color: '#6b5ce7',
                          textAlign: 'center',
                          fontSize: '2rem',
                          mb: 2
                        }}>
                          {formatTime(appointment.start)}
                        </Typography>
                      </Box>
                      
                      <Typography variant="body1" sx={{ 
                        color: '#666',
                        textAlign: 'center',
                        fontWeight: 500
                      }}>
                        {dateLabel}
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
              );
            })}
          </Grid>
        )}
    </Box>
  );
};

export default AppointmentList;
