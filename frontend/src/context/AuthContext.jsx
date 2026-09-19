import React, { createContext, useContext, useState, useEffect } from 'react';
import api from '../services/api';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(() => {
    const saved = localStorage.getItem('sentinel_user');
    return saved ? JSON.parse(saved) : null;
  });
  const [token, setToken] = useState(() => localStorage.getItem('sentinel_token'));
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const verifyUser = async () => {
      if (token) {
        try {
          const response = await api.get('/auth/me');
          setUser(response.data);
          localStorage.setItem('sentinel_user', JSON.stringify(response.data));
        } catch (error) {
          console.error("Session verification failed:", error);
          logout();
        }
      }
      setLoading(false);
    };
    verifyUser();
  }, [token]);

  const login = async (email, password) => {
    const response = await api.post('/auth/login', { email, password });
    const { access_token, role, email: userEmail, full_name } = response.data;
    const userData = { email: userEmail, role, full_name };

    setToken(access_token);
    setUser(userData);
    localStorage.setItem('sentinel_token', access_token);
    localStorage.setItem('sentinel_user', JSON.stringify(userData));
    return userData;
  };

  const register = async (email, password, fullName, role = 'VIEWER') => {
    const response = await api.post('/auth/register', {
      email,
      password,
      full_name: fullName,
      role
    });
    const { access_token, role: userRole, email: userEmail, full_name } = response.data;
    const userData = { email: userEmail, role: userRole, full_name };

    setToken(access_token);
    setUser(userData);
    localStorage.setItem('sentinel_token', access_token);
    localStorage.setItem('sentinel_user', JSON.stringify(userData));
    return userData;
  };

  const logout = async () => {
    try {
      if (token) {
        await api.post('/auth/logout');
      }
    } catch (e) {
      // Ignore logout audit error
    } finally {
      setToken(null);
      setUser(null);
      localStorage.removeItem('sentinel_token');
      localStorage.removeItem('sentinel_user');
    }
  };

  const changePassword = async (oldPassword, newPassword) => {
    return await api.post('/auth/change-password', {
      old_password: oldPassword,
      new_password: newPassword
    });
  };

  return (
    <AuthContext.Provider value={{ user, token, loading, login, register, logout, changePassword }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
