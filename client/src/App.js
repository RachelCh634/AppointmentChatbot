import ChatBot from './components/ChatBot';
import { GoogleOAuthProvider } from '@react-oauth/google';
import AppointmentList from './components/AppointmentList';

const App = () => {
  return (
    <GoogleOAuthProvider clientId = "408459241479-s3qq87inio009nfiaoqejo00vagoeqik.apps.googleusercontent.com">
      <ChatBot />
    </GoogleOAuthProvider>
  );
}

export default App;
