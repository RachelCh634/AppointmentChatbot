import React, { useState, useEffect } from 'react';
import ChatBot from './components/ChatBot';
import { GoogleOAuthProvider } from '@react-oauth/google';
import AppointmentList from './components/AppointmentList';

const App = () => {
  const [isDoctor, setIsDoctor] = useState(false);
  
  useEffect(() => {
    const doctorToken = localStorage.getItem('doctorToken');
    setIsDoctor(!!doctorToken); 
  }, []);

  return (
    <GoogleOAuthProvider clientId="408459241479-s3qq87inio009nfiaoqejo00vagoeqik.apps.googleusercontent.com">
        {isDoctor ? (
          <AppointmentList />
        ) : (
          <ChatBot />
        )}
    </GoogleOAuthProvider>
  );
}

export default App;
