import React from 'react';
import { useGoogleLogin } from '@react-oauth/google';
import axios from 'axios';

const GoogleAuth = ({ onSuccess }) => {
    const login = useGoogleLogin({
        onSuccess: async (response) => {
            try {
                const serverResponse = await axios.post('http://localhost:5000/google-login', {
                    googleToken: response.access_token
                });
                const token = serverResponse.data.token;
                localStorage.setItem('token', token);
            } catch (error) {
                console.error('Login error:', error);
            }
        },
    });
    React.useEffect(() => {
        onSuccess();
        login();
    }, []);
    return null;
};

export default GoogleAuth;
