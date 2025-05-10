import { useState, useRef, useEffect } from 'react';
import { TextField, Button, Box, Typography, Paper, Avatar } from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import { keyframes } from '@mui/system';
import SmartToyIcon from '@mui/icons-material/SmartToy';
import PersonIcon from '@mui/icons-material/Person';
import GoogleIcon from '@mui/icons-material/Google';
import Particles from "react-tsparticles";
import { loadSlim } from "tsparticles-slim";
import SideButtons from './SideButtons';

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

const typing = keyframes`
  0% { width: 0 }
  20% { width: 5px }
  40% { width: 10px }
  60% { width: 15px }
  80% { width: 20px }
  100% { width: 25px }
`;

const ChatBot = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef(null);
  const [isLoggedIn, setIsLoggedIn] = useState(!!localStorage.getItem('token'));

  const particlesInit = async (engine) => {
    await loadSlim(engine);
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleLoginSuccess = () => {
    setIsLoggedIn(true);
    setMessages(prevMessages => [
      ...prevMessages,
      { text: 'Welcome, you have successfully logged in, now you can make an appointment, write me the desired time.', sender: 'bot' }
    ]);
  };

  const handleLogout = () => {
    setIsLoggedIn(false);
    setMessages(prevMessages => [
      ...prevMessages,
      { text: 'You have successfully logged out.', sender: 'bot' }
    ]);
  };

  const handleSendMessage = async () => {
    if (input.trim()) {
      setMessages([...messages, { text: input, sender: 'user' }]);
      const userMessage = input;
      setInput('');

      if (!isLoggedIn) {
        setMessages((prevMessages) => [
          ...prevMessages,
          { text: "Oops! You're not logged in yet. To save your appointment, please sign in with Google.", sender: 'bot' },
        ]);
        return;
      }
      setIsTyping(true);
      try {
        const token = localStorage.getItem('token');
        const response = await fetch('http://localhost:5000/appointment', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`  
          },
          body: JSON.stringify({ text: userMessage }),
        });
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        const data = await response.json();
        setIsTyping(false);
        setMessages((prevMessages) => [
          ...prevMessages,
          { text: data.message, sender: 'bot' },
        ]);
      } catch (error) {
        console.error('Error:', error);
        setIsTyping(false);
        setMessages((prevMessages) => [
          ...prevMessages,
          { text: 'Sorry, I encountered an error. Please try again later.', sender: 'bot' },
        ]);
      }
    }
  };

  return (
    <>
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
        onLoginSuccess={handleLoginSuccess}
        onLogout={handleLogout}
      />

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
            <SmartToyIcon />
          </Avatar>
          <Box>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <Typography variant="h6" sx={{ fontWeight: 'bold', fontSize: '1.1rem', mr: 1 }}>
                MediBot
              </Typography>
            </Box>
            <Typography variant="body2" sx={{ opacity: 0.8 }}>
              Online | Ready to help
            </Typography>
          </Box>
          {isLoggedIn && (
            <Box sx={{ ml: 'auto', display: 'flex', alignItems: 'center' }}>
              <Typography variant="body2" sx={{ opacity: 0.8 }}>
                {localStorage.getItem('userName') || 'User'}
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
          )}
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
              <SmartToyIcon sx={{ fontSize: 60, color: '#6b5ce7', mb: 2 }} />
              <Typography variant="body1" sx={{ textAlign: 'center', color: '#666' }}>
                Send a message to start the conversation
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
                  padding: 1.5,
                  maxWidth: '75%',
                  backgroundColor: message.sender === 'user' ? '#6b5ce7' : '#f0f2f5',
                  color: message.sender === 'user' ? 'white' : 'black',
                  borderRadius: message.sender === 'user'
                    ? '18px 18px 4px 18px'
                    : '18px 18px 18px 4px',
                  boxShadow: '0 1px 2px rgba(0,0,0,0.1)',
                  wordBreak: 'break-word',
                  fontWeight: 400,
                }}
              >
                {message.text}
              </Box>

              {message.sender === 'user' && (
                <Avatar
                  sx={{
                    bgcolor: '#e91e63',
                    width: 32,
                    height: 32,
                    ml: 1,
                    alignSelf: 'flex-end',
                    mb: 0.5
                  }}
                >
                  <PersonIcon sx={{ fontSize: 18 }} />
                </Avatar>
              )}
            </Box>
          ))}

          {isTyping && (
            <Box
              sx={{
                display: 'flex',
                alignItems: 'center',
                animation: `${fadeIn} 0.3s ease-out`,
              }}
            >
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
              <Box
                sx={{
                  padding: 1.5,
                  backgroundColor: '#f0f2f5',
                  borderRadius: '18px 18px 18px 4px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  width: 60,
                }}
              >
                <Box
                  sx={{
                    display: 'flex',
                    gap: 0.5,
                    alignItems: 'center',
                  }}
                >
                  <Box
                    sx={{
                      width: 8,
                      height: 8,
                      backgroundColor: '#888',
                      borderRadius: '50%',
                      animation: `${typing} 1s infinite alternate`,
                      animationDelay: '0s',
                    }}
                  />
                  <Box
                    sx={{
                      width: 8,
                      height: 8,
                      backgroundColor: '#888',
                      borderRadius: '50%',
                      animation: `${typing} 1s infinite alternate`,
                      animationDelay: '0.3s',
                    }}
                  />
                  <Box
                    sx={{
                      width: 8,
                      height: 8,
                      backgroundColor: '#888',
                      borderRadius: '50%',
                      animation: `${typing} 1s infinite alternate`,
                      animationDelay: '0.6s',
                    }}
                  />
                </Box>
              </Box>
            </Box>
          )}
          <div ref={messagesEndRef} />
        </Paper>

        <Box
          sx={{
            display: 'flex',
            gap: 1,
            marginTop: 2,
            position: 'relative',
          }}
        >
          <TextField
            placeholder="Type your message..."
            variant="outlined"
            fullWidth
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => {
              if (e.key === 'Enter') {
                handleSendMessage();
              }
            }}
            sx={{
              '& .MuiOutlinedInput-root': {
                borderRadius: 3,
                backgroundColor: 'white',
                '&:hover .MuiOutlinedInput-notchedOutline': {
                  borderColor: '#6b5ce7',
                },
                '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
                  borderColor: '#6b5ce7',
                  borderWidth: '2px',
                },
              },
            }}
          />
          <Button
            variant="contained"
            onClick={handleSendMessage}
            disabled={!input.trim()}
            sx={{
              height: '56px',
              width: '56px',
              minWidth: '56px',
              borderRadius: '50%',
              backgroundColor: '#6b5ce7',
              '&:hover': {
                backgroundColor: '#5346c7',
              },
              transition: 'all 0.2s ease-in-out',
              boxShadow: '0 4px 10px rgba(107, 92, 231, 0.3)',
            }}
          >
            <SendIcon />
          </Button>
        </Box>
      </Box>
    </>
  );
};

export default ChatBot;

