import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import translations from '../translations';
import '../styles/HomePage.css';

// Backend URL configuration
const BACKEND_URL = 'https://redcamptalesbackend-409594015641.europe-north1.run.app';
const HomePage = () => {
  // Authentication state - determined by JWT in localStorage
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [userData, setUserData] = useState(null);
  const [loadingUserData, setLoadingUserData] = useState(false);
  
  // Check for JWT token on component mount and fetch user data if authenticated
  useEffect(() => {
    const token = localStorage.getItem('token');
    const isAuth = !!token;
    setIsAuthenticated(isAuth);
    
    if (isAuth) {
      fetchUserData();
    }
  }, []);

  // Fetch user data for authenticated users
  const fetchUserData = async () => {
    setLoadingUserData(true);
    try {
      const token = localStorage.getItem('token');
      const headers = { 'Authorization': `Bearer ${token}` };

      const response = await fetch(`${BACKEND_URL}/api/v1/user/me`, {
        method: 'GET',
        headers: headers
      });
      
      if (!response.ok) {
        // If unauthorized, token is likely expired
        if (response.status === 401) {
          localStorage.removeItem('token');
          setIsAuthenticated(false);
          setUserData(null);
          return;
        }
        throw new Error('Failed to fetch user data');
      }
      
      const data = await response.json();
      setUserData(data);
    } catch (error) {
      console.error('Error fetching user data:', error);
      // On error, clear authentication
      localStorage.removeItem('token');
      setIsAuthenticated(false);
      setUserData(null);
    } finally {
      setLoadingUserData(false);
    }
  };
  
  // Form visibility states
  const [showLoginForm, setShowLoginForm] = useState(false);
  const [showRegisterForm, setShowRegisterForm] = useState(false);
  
  // Form data states
  const [loginData, setLoginData] = useState({ username: '', password: '' });
  const [registerData, setRegisterData] = useState({ 
    name: '', 
    password: '', 
    confirmPassword: '',
    game_name: '', 
    game_biography: '' 
  });
  const [isRegistering, setIsRegistering] = useState(false); // For registration loading state
  
  // Error and success messages
  const [loginError, setLoginError] = useState('');
  const [registerError, setRegisterError] = useState('');
  const [registerSuccess, setRegisterSuccess] = useState('');
  const [mainSuccessMessage, setMainSuccessMessage] = useState('');
  
  // Get language from URL params and set up navigation
  const { lang } = useParams();
  const navigate = useNavigate();
  const currentLang = lang && (lang === 'en' || lang === 'ru') ? lang : 'ru';
  const t = translations[currentLang] || translations.en;
  
  // Logout function
  const handleLogout = () => {
    localStorage.removeItem('token');
    setIsAuthenticated(false);
    setUserData(null);
    setShowAccountModal(false); // Close the account modal
  };

  // Switch language
  const switchLanguage = (newLang) => {
    navigate(`/${newLang}`);
  };
  
  // Show login form and hide register form
  const handleShowLoginForm = () => {
    setShowLoginForm(true);
    setShowRegisterForm(false);
    // Reset any previous messages
    setLoginError('');
    setRegisterError('');
    setRegisterSuccess('');
  };
  
  // Show register form and hide login form
  const handleShowRegisterForm = () => {
    setShowRegisterForm(true);
    setShowLoginForm(false);
    // Reset any previous messages
    setLoginError('');
    setRegisterError('');
    setRegisterSuccess('');
  };
  
  // Close all forms
  const handleCloseForm = () => {
    setShowLoginForm(false);
    setShowRegisterForm(false);
    // Reset form data
    setLoginData({ username: '', password: '' });
    setRegisterData({ 
      name: '', 
      password: '', 
      confirmPassword: '',
      game_name: '', 
      game_biography: '' 
    });
    // Reset any messages
    setLoginError('');
    setRegisterError('');
    // Don't clear register success message here to allow it to be displayed on the main screen
    // after account deletion or data truncation
  };
  
  // Handle login form input changes
  const handleLoginChange = (e) => {
    const { name, value } = e.target;
    setLoginData(prev => ({ ...prev, [name]: value }));
  };
  
  // Handle register form input changes
  const handleRegisterChange = (e) => {
    const { name, value } = e.target;
    setRegisterData(prev => ({ ...prev, [name]: value }));
  };
  
  // Submit login form
  const handleLoginSubmit = async (e) => {
    e.preventDefault();
    setLoginError('');
    
    try {
      // Create form data for OAuth2 password flow
      const formData = new FormData();
      formData.append('username', loginData.username);
      formData.append('password', loginData.password);
      
      const response = await fetch(`${BACKEND_URL}/api/v1/user/login`, {
        method: 'POST',
        body: formData,
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Login failed');
      }
      
      const data = await response.json();
      // Store token in localStorage
      localStorage.setItem('token', data.access_token);
      // Update authentication state
      setIsAuthenticated(true);
      // Fetch user data
      await fetchUserData();
      // Close the form
      handleCloseForm();
      // Automatically show account modal after successful login
      setTimeout(() => {
        handleMyAccountClick();
      }, 100);
    } catch (error) {
      setLoginError(error.message || 'Login failed. Please try again.');
    }
  };
  
  // Submit register form
  const handleRegisterSubmit = async (e) => {
    e.preventDefault();
    setRegisterError('');
    setRegisterSuccess('');
    setIsRegistering(true); // Start loading
    
    // Validate password match
    if (registerData.password !== registerData.confirmPassword) {
      setRegisterError(currentLang === 'en' ? 'Passwords do not match' : 'Пароли не совпадают');
      return;
    }
    
    // Map currentLang to backend expected values
    const apiLanguage = currentLang === 'en' ? 'english' : 'russian';
    
    try {
      // Prepare data for API
      const apiData = {
        name: registerData.name,
        password: registerData.password,
        game_name: registerData.game_name,
        game_biography: registerData.game_biography,
        language: apiLanguage // Use mapped language
      };
      
      const response = await fetch(`${BACKEND_URL}/api/v1/user`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(apiData)
      });
      
      if (!response.ok) {
        // Handle specific error codes
        if (response.status === 409) {
          throw new Error(currentLang === 'en' ? 'User already exists' : 'Пользователь уже существует');
        }
        throw new Error(currentLang === 'en' ? 'Registration failed' : 'Регистрация не удалась');
      }
      
      // Registration successful
      setRegisterSuccess(currentLang === 'en' ? 'Registration successful! You can now log in.' : 'Регистрация успешна! Теперь вы можете войти.');
      
      // Reset form data
      setRegisterData({ 
        name: '', 
        password: '', 
        confirmPassword: '',
        game_name: '', 
        game_biography: '' 
      });
      
      // Automatically show login form after successful registration
      setTimeout(() => {
        handleShowLoginForm();
      }, 1000);
      
    } catch (error) {
      setRegisterError(error.message || 'Registration failed. Please try again.');
    } finally {
      setIsRegistering(false); // Stop loading
    }
  };

  const [newGameLoading, setNewGameLoading] = useState(false);

  // Start a new game
  const handleNewGame = async () => {
    setNewGameLoading(true);
    try {
      const token = localStorage.getItem('token');
      const headers = token ? {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      } : {
        'Content-Type': 'application/json'
      };
      
      // Call API to create a new game
      const response = await fetch(`${BACKEND_URL}/api/v1/game_state/new`, {
        method: 'POST',
        headers: headers
      });
      
      if (!response.ok) {
        throw new Error('Failed to create new game');
      }
      
      // Navigate to the game page
      navigate(`/${currentLang}/game`);
    } catch (error) {
      console.error('Error creating new game:', error);
    } finally {
      setNewGameLoading(false);
    }
  };

  // State for modals
  const [showContactsModal, setShowContactsModal] = useState(false);
  const [showAccountModal, setShowAccountModal] = useState(false);
  const [showSaves, setShowSaves] = useState(false);
  const [showHelpModal, setShowHelpModal] = useState(false);
  
  // Loading and error states
  const [savesLoading, setSavesLoading] = useState(false);
  const [savesError, setSavesError] = useState('');
  const [savingGame, setSavingGame] = useState(false);
  const [loadingSave, setLoadingSave] = useState(false);
  
  // Account state
  const [accountFormData, setAccountFormData] = useState({});
  const [updateSuccess, setUpdateSuccess] = useState('');
  const [updateError, setUpdateError] = useState('');
  const [isUpdatingAccount, setIsUpdatingAccount] = useState(false); // For account update loading state
  const [deleteConfirm, setDeleteConfirm] = useState(false);
  const [truncateConfirm, setTruncateConfirm] = useState(false);
  const [saves, setSaves] = useState([]);
  const [saveDescription, setSaveDescription] = useState('');
  const [editingSaveId, setEditingSaveId] = useState(null);

  // Function to handle contacts button click
  const handleContactsClick = () => {
    setShowContactsModal(true);
  };

  // Function to close contacts modal
  const handleCloseContacts = () => {
    setShowContactsModal(false);
  };
  
  // Function to handle my account button click
  const handleMyAccountClick = async () => {
    // For authenticated users, just show the account modal with current data
    setUpdateError('');
    setUpdateSuccess('');
    
    if (userData) {
      // Use the displayed fields directly and the user's actual language preference
      setAccountFormData({
        game_name: userData.user_biography_displayed_name || '',
        game_biography: userData.user_biography_displayed_description || '',
        narrative_preference: userData.user_narrative_displayed_preference || '',
        language: userData.language || 'auto' // Use the user's actual language preference
      });
    }
    
    setShowAccountModal(true);
  };

  // Function to close account modal
  const handleCloseAccount = () => {
    setShowAccountModal(false);
    setDeleteConfirm(false);
    setTruncateConfirm(false);
    setUpdateError('');
  };
  
  // Handle account update form changes
  const handleAccountUpdateChange = (e) => {
    const { name, value } = e.target;
    setAccountFormData(prev => ({ ...prev, [name]: value }));
  };
  
  // Handle account update submission
  const handleAccountUpdateSubmit = async (e) => {
    e.preventDefault();
    setUpdateError('');
    setUpdateSuccess('');
    setIsUpdatingAccount(true); // Start loading
    
    try {
      const token = localStorage.getItem('token');
      const headers = { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' };
      
      // Use the selected language from the form instead of mapping currentLang
      const payload = {
        game_name: accountFormData.game_name,
        game_biography: accountFormData.game_biography,
        narrative_preference: accountFormData.narrative_preference,
        language: accountFormData.language // Use the language selected in the form
      };

      const response = await fetch(`${BACKEND_URL}/api/v1/user`, {
        method: 'PUT',
        headers: headers,
        body: JSON.stringify(payload)
      });
      
      if (!response.ok) {
        throw new Error(currentLang === 'en' ? 'Failed to update account' : 'Не удалось обновить аккаунт');
      }
      
      const updatedUserData = await response.json(); // Backend returns the full User object
      setUserData(updatedUserData);

      // Use the displayed fields from the updated user data
      setAccountFormData({
        game_name: updatedUserData.user_biography_displayed_name || '',
        game_biography: updatedUserData.user_biography_displayed_description || '',
        narrative_preference: updatedUserData.user_narrative_displayed_preference || '',
        language: accountFormData.language // Keep the selected language
      });
      setUpdateSuccess(currentLang === 'en' ? 'Account updated successfully!' : 'Аккаунт успешно обновлен!');
      
      // Clear success message after 3 seconds
      setTimeout(() => {
        setUpdateSuccess('');
      }, 3000);
    } catch (error) {
      setUpdateError(error.message);
      
      // Clear error message after 3 seconds
      setTimeout(() => {
        setUpdateError('');
      }, 3000);
    } finally {
      setIsUpdatingAccount(false); // Stop loading
    }
  };

  // Handle account deletion
  const handleDeleteAccount = async () => {
    if (!deleteConfirm) {
      setDeleteConfirm(true);
      return;
    }

    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${BACKEND_URL}/api/v1/user`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) {
        throw new Error(currentLang === 'en' ? 'Failed to delete account' : 'Не удалось удалить аккаунт');
      }

      // Create a success message that will be shown on the main page
      const successMessage = currentLang === 'en' ? 'Account deleted successfully' : 'Аккаунт успешно удален';
      
      // Clear token and authentication state
      localStorage.removeItem('token');
      setIsAuthenticated(false);
      setDeleteConfirm(false);
      
      // Close the account modal and show success message on the main screen
      setShowAccountModal(false);
      
      // Use a global success message instead of register-specific one
      setMainSuccessMessage(successMessage);
      
      // Clear success message after 3 seconds
      setTimeout(() => {
        setMainSuccessMessage('');
      }, 3000);
    } catch (error) {
      setUpdateError(error.message);
      
      // Clear error message after 3 seconds
      setTimeout(() => {
        setUpdateError('');
      }, 3000);
    }
  };

  // Handle truncating user data (deleting all user data while keeping the account)
  const handleTruncateUserData = async () => {
    if (!truncateConfirm) {
      setTruncateConfirm(true);
      return;
    }

    try {
      const token = localStorage.getItem('token');
      // Only include Authorization header if token exists
      const headers = token ? { 'Authorization': `Bearer ${token}` } : {};
      
      const response = await fetch(`${BACKEND_URL}/api/v1/user/truncate`, {
        method: 'POST',
        headers: headers
      });

      if (!response.ok) {
        throw new Error(currentLang === 'en' ? 'Failed to delete user data' : 'Не удалось удалить данные пользователя');
      }

      // Create a success message that will be shown on the main page
      const successMessage = currentLang === 'en' ? 'All user data has been deleted successfully' : 'Все данные пользователя успешно удалены';
      
      // Close the account modal and reset confirmation state
      setShowAccountModal(false);
      setTruncateConfirm(false);
      
      // Use a global success message instead of register-specific one
      setMainSuccessMessage(successMessage);
      
      // Clear success message after 3 seconds
      setTimeout(() => {
        setMainSuccessMessage('');
      }, 3000);
    } catch (error) {
      setUpdateError(error.message);
      
      // Clear error message after 3 seconds
      setTimeout(() => {
        setUpdateError('');
      }, 3000);
    }
  };

  // Saves modal handlers
  const handleSavesClick = async () => {
    setShowSaves(true);
    await fetchSaves();
  };
  
  const handleCloseSaves = () => {
    setShowSaves(false);
    setSaveDescription('');
    setEditingSaveId(null);
  };
  
  const fetchSaves = async () => {
    setSavesLoading(true);
    setSavesError(null);
    
    try {
      let token = localStorage.getItem('token');
      
      // Make sure token doesn't already have 'Bearer ' prefix
      if (token && token.startsWith('Bearer ')) {
        token = token.substring(7);
      }
      
      const headers = { 'Authorization': token ? `Bearer ${token}` : '' };
      
      const response = await fetch(`${BACKEND_URL}/api/v1/saves`, {
        method: 'GET',
        headers: headers
      });
      
      if (!response.ok) {
        throw new Error(`Error: ${response.status}`);
      }
      
      const data = await response.json();
      setSaves(data);
    } catch (err) {
      setSavesError(err.message || 'Failed to fetch saves');
      console.error('Error fetching saves:', err);
    } finally {
      setSavesLoading(false);
    }
  };
  
  const handleUpdateSave = async () => {
    if (!editingSaveId) return;
    
    setSavingGame(true);
    setSavesError(null);
    
    try {
      const token = localStorage.getItem('token');
      const headers = {
        'Authorization': token ? `Bearer ${token}` : '',
        'Content-Type': 'application/json'
      };
      
      const response = await fetch(`${BACKEND_URL}/api/v1/save/${editingSaveId}`, {
        method: 'PUT',
        headers: headers,
        body: JSON.stringify({
          description: saveDescription
        })
      });
      
      if (!response.ok) {
        throw new Error(`Error: ${response.status}`);
      }
      
      // Refresh saves list
      await fetchSaves();
      setSaveDescription('');
      setEditingSaveId(null);
    } catch (err) {
      setSavesError(err.message || 'Failed to update save');
      console.error('Error updating save:', err);
    } finally {
      setSavingGame(false);
    }
  };
  
  const handleDeleteSave = async (saveId) => {
    setSavingGame(true);
    setSavesError(null);
    
    try {
      const token = localStorage.getItem('token');
      const headers = {
        'Authorization': token ? `Bearer ${token}` : ''
      };
      
      const response = await fetch(`${BACKEND_URL}/api/v1/save/${saveId}`, {
        method: 'DELETE',
        headers: headers
      });
      
      if (!response.ok) {
        throw new Error(`Error: ${response.status}`);
      }
      
      // Refresh saves list
      await fetchSaves();
    } catch (err) {
      setSavesError(err.message || 'Failed to delete save');
      console.error('Error deleting save:', err);
    } finally {
      setSavingGame(false);
    }
  };
  
  const handleLoadSave = async (gameStateId) => {
    setLoadingSave(true);
    setSavesError(null);
    
    try {
      const token = localStorage.getItem('token');
      const headers = {
        'Authorization': token ? `Bearer ${token}` : ''
      };
      
      // Load the game state
      const response = await fetch(`${BACKEND_URL}/api/v1/game_state/${gameStateId}`, {
        method: 'GET',
        headers: headers
      });
      
      if (!response.ok) {
        throw new Error(`Error: ${response.status}`);
      }
      
      // Navigate to game page after successful load
      navigate(`/${currentLang}/game`);
      handleCloseSaves();
    } catch (err) {
      setSavesError(err.message || 'Failed to load save');
      console.error('Error loading save:', err);
    } finally {
      setLoadingSave(false);
    }
  };
  
  const handleEditSave = (save) => {
    setEditingSaveId(save.id);
    setSaveDescription(save.description);
  };

  // Help Modal handlers
  const handleHelpClick = () => {
    setShowHelpModal(true);
  };

  const handleCloseHelpModal = () => {
    setShowHelpModal(false);
  };

  // Styles for the global loading overlay
  const loadingOverlayStyles = {
    position: 'fixed',
    top: 0,
    left: 0,
    width: '100vw',
    height: '100vh',
    backgroundColor: 'rgba(0, 0, 0, 0.6)', // Dark semi-transparent background
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    zIndex: 2000, // High z-index to be on top
    color: 'white',
    fontSize: '2em',
    textAlign: 'center'
  };

  return (
    <div className="home-page" style={{ backgroundImage: `url(https://storage.googleapis.com/redcamptalesstatic/static/ext_road_night.jpg)` }}>
      {/* Global Loading Overlay */}
      {(isRegistering || isUpdatingAccount) && (
        <div style={loadingOverlayStyles}>
          {isRegistering 
            ? (currentLang === 'en' ? 'Registering Account...\nPlease wait.' : 'Регистрация аккаунта...\nПожалуйста, подождите.') 
            : (currentLang === 'en' ? 'Updating Account...\nPlease wait.' : 'Обновление аккаунта...\nПожалуйста, подождите.')}
        </div>
      )}

      {/* Language switcher */}
      <div className="language-switcher">
        <button 
          className={`language-button ${currentLang === 'en' ? 'active' : ''}`}
          onClick={() => switchLanguage('en')}
        >
          EN
        </button>
        <button 
          className={`language-button ${currentLang === 'ru' ? 'active' : ''}`}
          onClick={() => switchLanguage('ru')}
        >
          RU
        </button>
      </div>

      {/* Login Form */}
      {showLoginForm && (
        <div className="form-overlay">
          <div className="form-container">
            <button className="close-button" onClick={handleCloseForm}>&times;</button>
            <h2>{t.login}</h2>
            {loginError && <div className="error-message">{loginError}</div>}
            <form onSubmit={handleLoginSubmit}>
              <div className="form-group">
                <label htmlFor="username">{currentLang === 'en' ? 'Username' : 'Имя пользователя'}</label>
                <input
                  type="text"
                  id="username"
                  name="username"
                  value={loginData.username}
                  onChange={handleLoginChange}
                  required
                />
              </div>
              <div className="form-group">
                <label htmlFor="password">{currentLang === 'en' ? 'Password' : 'Пароль'}</label>
                <input
                  type="password"
                  id="password"
                  name="password"
                  value={loginData.password}
                  onChange={handleLoginChange}
                  required
                />
              </div>
              <button type="submit" className="form-button">
                {currentLang === 'en' ? 'Login' : 'Войти'}
              </button>
            </form>
            <p className="form-switch">
              {currentLang === 'en' ? "Don't have an account?" : 'Нет аккаунта?'} 
              <button onClick={handleShowRegisterForm} className="text-button">
                {currentLang === 'en' ? 'Register' : 'Зарегистрироваться'}
              </button>
            </p>
          </div>
        </div>
      )}

      {/* Registration Form */}
      {showRegisterForm && (
        <div className="form-overlay">
          <div className="form-container">
            <button className="close-button" onClick={handleCloseForm}>&times;</button>
            <h2>{t.createAccount}</h2>
            <p style={{ color: '#666', fontSize: '0.9rem', fontStyle: 'italic', marginBottom: '15px' }}>
              {currentLang === 'en' 
                ? 'Read the help section to understand what this game is all about' 
                : 'Прочитайте справку, чтобы понять, о чём эта игра'}
            </p>
            {registerError && <div className="error-message">{registerError}</div>}
            {registerSuccess && <div className="success-message">{registerSuccess}</div>}
            <form onSubmit={handleRegisterSubmit}>
              <div className="form-group">
                <label htmlFor="name">{currentLang === 'en' ? 'Username' : 'Имя пользователя'}</label>
                <input
                  type="text"
                  id="name"
                  name="name"
                  value={registerData.name}
                  onChange={handleRegisterChange}
                  required
                />
              </div>
              <div className="form-group">
                <label htmlFor="password">{currentLang === 'en' ? 'Password' : 'Пароль'}</label>
                <input
                  type="password"
                  id="password"
                  name="password"
                  value={registerData.password}
                  onChange={handleRegisterChange}
                  required
                />
              </div>
              <div className="form-group">
                <label htmlFor="confirmPassword">
                  {currentLang === 'en' ? 'Confirm Password' : 'Подтвердите пароль'}
                </label>
                <input
                  type="password"
                  id="confirmPassword"
                  name="confirmPassword"
                  value={registerData.confirmPassword}
                  onChange={handleRegisterChange}
                  required
                />
              </div>
              <div className="form-group">
                <label htmlFor="game_name">
                  {currentLang === 'en' ? 'Character Name' : 'Имя персонажа'}
                </label>
                <input
                  type="text"
                  id="game_name"
                  name="game_name"
                  value={registerData.game_name}
                  onChange={handleRegisterChange}
                  required
                />
              </div>
              <div className="form-group">
                <label htmlFor="game_biography">
                  {currentLang === 'en' ? 'Character Biography' : 'Биография персонажа'}
                </label>
                <textarea
                  id="game_biography"
                  name="game_biography"
                  value={registerData.game_biography}
                  onChange={handleRegisterChange}
                  rows="4"
                  required
                ></textarea>
              </div>
              <button type="submit" className="form-button" disabled={isRegistering}>
                {isRegistering 
                  ? (currentLang === 'en' ? 'Registering...' : 'Регистрация...') 
                  : (currentLang === 'en' ? 'Register' : 'Зарегистрироваться')}
              </button>
            </form>
            <p className="form-switch">
              {currentLang === 'en' ? 'Already have an account?' : 'Уже есть аккаунт?'} 
              <button onClick={handleShowLoginForm} className="text-button">
                {currentLang === 'en' ? 'Login' : 'Войти'}
              </button>
            </p>
          </div>
        </div>
      )}

      {/* Contacts Modal */}
      {showContactsModal && (
        <div className="form-overlay">
          <div className="form-container">
            <button className="close-button" onClick={handleCloseContacts}>&times;</button>
            <h2>{t.contacts}</h2>
            <div className="contacts-content">
              <p>Owner: vladlen32230@gmail.com</p>
              <p>Telegram: @vladlen32230</p>
            </div>
          </div>
        </div>
      )}
      
      {/* Account Modal */}
      {showAccountModal && (
        <div className="form-overlay">
          <div className="form-container">
            <div className="modal-header" style={{ position: 'relative', backgroundColor: 'rgba(0, 100, 0, 0.7)', color: 'white', padding: '0', borderTopLeftRadius: '5px', borderTopRightRadius: '5px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', width: '100%' }}>
                <h2 style={{ margin: 0, padding: '10px 15px' }}>{currentLang === 'en' ? 'MY ACCOUNT' : 'МОЙ АККАУНТ'}</h2>
                <button className="close-button" onClick={handleCloseAccount} style={{ fontSize: '60px', background: 'none', border: 'none', color: 'white', cursor: 'pointer', padding: '10px 15px', margin: 0 }}>×</button>
              </div>
            </div>
            
            {userData && (
              <div className="account-details">
                <div className="account-info">
                  <h3>{currentLang === 'en' ? 'Account Information' : 'Информация об аккаунте'}</h3>
                  <p style={{ fontSize: '2rem' }}><strong>{currentLang === 'en' ? 'Username' : 'Имя пользователя'}:</strong> {userData.name}</p>
                  
                  {/* Subscription Information */}
                  <div className="subscription-info" style={{ marginTop: '15px', padding: '10px', backgroundColor: userData.subscription_tier === 'premium' ? 'rgba(255, 215, 0, 0.2)' : 'rgba(128, 128, 128, 0.2)', borderRadius: '5px' }}>
                    <p style={{ fontSize: '1.8rem', margin: '5px 0' }}>
                      <strong>{currentLang === 'en' ? 'Subscription' : 'Подписка'}:</strong> 
                      <span style={{ 
                        color: userData.subscription_tier === 'premium' ? '#FFD700' : '#666',
                        fontWeight: 'bold',
                        marginLeft: '10px',
                        textTransform: 'uppercase'
                      }}>
                        {userData.subscription_tier === 'premium' 
                          ? (currentLang === 'en' ? 'PREMIUM' : 'ПРЕМИУМ')
                          : (currentLang === 'en' ? 'FREE' : 'БЕСПЛАТНАЯ')}
                      </span>
                    </p>
                    
                    {userData.subscription_tier === 'premium' && userData.subscription_ends_at && (
                      <p style={{ fontSize: '1.4rem', margin: '5px 0', color: '#666' }}>
                        {currentLang === 'en' ? 'Expires' : 'Истекает'}: {new Date(userData.subscription_ends_at).toLocaleDateString(currentLang === 'ru' ? 'ru-RU' : 'en-US')}
                      </p>
                    )}
                    
                    {userData.subscription_tier === 'premium' && userData.subscription_started_at && (
                      <p style={{ fontSize: '1.4rem', margin: '5px 0', color: '#666' }}>
                        {currentLang === 'en' ? 'Started' : 'Начата'}: {new Date(userData.subscription_started_at).toLocaleDateString(currentLang === 'ru' ? 'ru-RU' : 'en-US')}
                      </p>
                    )}
                  </div>
                </div>
                
                <div className="character-info">
                  {updateError && <div className="error-message">{updateError}</div>}
                  {updateSuccess && <div className="success-message">{updateSuccess}</div>}
                  
                  <form onSubmit={handleAccountUpdateSubmit}>
                    <div className="form-group">
                      <label htmlFor="game_name">
                        {currentLang === 'en' ? 'Character Name' : 'Имя персонажа'}
                      </label>
                      <input
                        type="text"
                        id="game_name"
                        name="game_name"
                        value={accountFormData.game_name || ''}
                        onChange={handleAccountUpdateChange}
                        required
                      />
                    </div>
                    <div className="form-group">
                      <label htmlFor="game_biography">
                        {currentLang === 'en' ? 'Character Biography' : 'Биография персонажа'}
                      </label>
                      <textarea
                        id="game_biography"
                        name="game_biography"
                        value={accountFormData.game_biography || ''}
                        onChange={handleAccountUpdateChange}
                        rows="4"
                        required
                      ></textarea>
                    </div>
                    <div className="form-group">
                      <label htmlFor="narrative_preference">
                        {currentLang === 'en' ? 'Narrative Preference' : 'Предпочтение сюжета'}
                      </label>
                      <textarea
                        id="narrative_preference"
                        name="narrative_preference"
                        value={accountFormData.narrative_preference || ''}
                        onChange={handleAccountUpdateChange}
                        rows="3"
                        placeholder={currentLang === 'en' ? 'Always respond shortly' : 'Всегда отвечать кратко'}
                      ></textarea>
                    </div>
                    
                    {/* Scroll down indicator */}
                    <div className="scroll-indicator" style={{ 
                      textAlign: 'center', 
                      marginTop: '15px', 
                      color: '#9acd32', 
                      fontSize: '0.9rem',
                      opacity: '0.8'
                    }}>
                      ↓ {currentLang === 'en' ? 'Scroll down for more options' : 'Прокрутите вниз для дополнительных опций'} ↓
                    </div>
                    
                    <div className="form-group">
                      <label htmlFor="language">
                        {currentLang === 'en' ? 'Language Preference' : 'Предпочтение языка'}
                      </label>
                      <select
                        id="language"
                        name="language"
                        value={accountFormData.language || 'auto'}
                        onChange={handleAccountUpdateChange}
                        required
                      >
                        <option value="auto">
                          {currentLang === 'en' ? 'Auto-detect' : 'Автоопределение'}
                        </option>
                        <option value="English">English</option>
                        <option value="Russian">Русский</option>
                        <option value="Chinese (Simplified)">中文 (简体)</option>
                        <option value="Chinese (Traditional)">中文 (繁體)</option>
                        <option value="Spanish">Español</option>
                        <option value="Hindi">हिन्दी</option>
                        <option value="Korean">한국어</option>
                        <option value="French">Français</option>
                        <option value="Italian">Italiano</option>
                        <option value="Dutch">Nederlands</option>
                        <option value="Polish">Polski</option>
                        <option value="Arabic">العربية</option>
                        <option value="Portuguese">Português</option>
                        <option value="Japanese">日本語</option>
                        <option value="German">Deutsch</option>
                        <option value="Indonesian">Bahasa Indonesia</option>
                        <option value="Turkish">Türkçe</option>
                        <option value="Vietnamese">Tiếng Việt</option>
                        <option value="Romanian">Română</option>
                        <option value="Ukrainian">Українська</option>
                      </select>
                    </div>
                    <button type="submit" className="form-button" disabled={isUpdatingAccount}>
                      {isUpdatingAccount 
                        ? (currentLang === 'en' ? 'Updating...' : 'Обновление...') 
                        : (currentLang === 'en' ? 'Update' : 'Обновить')}
                    </button>
                  </form>
                </div>
                
                {/* Account Actions Section */}
                <div className="account-actions" style={{ marginTop: '20px', borderTop: '1px solid #ddd', paddingTop: '20px' }}>
                  {/* Delete Account Section */}
                  {deleteConfirm ? (
                    <div className="delete-confirm">
                      <p className="warning-text" style={{ color: '#d9534f', marginBottom: '10px' }}>
                        {currentLang === 'en' 
                          ? 'Are you sure? This action cannot be undone.'
                          : 'Вы уверены? Это действие нельзя отменить.'}
                      </p>
                      <div className="confirm-buttons" style={{ display: 'flex', gap: '10px' }}>
                        <button 
                          className="form-button" 
                          style={{ backgroundColor: '#d9534f', color: 'white', flex: 1 }}
                          onClick={handleDeleteAccount}
                        >
                          {currentLang === 'en' ? 'Yes, delete my account' : 'Да, удалить мой аккаунт'}
                        </button>
                        <button 
                          className="form-button" 
                          style={{ backgroundColor: '#f0f0f0', color: '#333', flex: 1 }}
                          onClick={() => setDeleteConfirm(false)}
                        >
                          {currentLang === 'en' ? 'Cancel' : 'Отмена'}
                        </button>
                      </div>
                    </div>
                  ) : (
                    <button 
                      className="form-button" 
                      style={{ backgroundColor: '#d9534f', color: 'white', width: '100%' }}
                      onClick={handleDeleteAccount}
                    >
                      {currentLang === 'en' ? 'Delete Account' : 'Удалить аккаунт'}
                    </button>
                  )}
                  
                  {/* Truncate User Data Section */}
                  <div style={{ marginTop: '20px' }}>
                    {truncateConfirm ? (
                      <div className="truncate-confirm">
                        <p className="warning-text" style={{ color: '#ff9800', marginBottom: '10px' }}>
                          {currentLang === 'en' 
                            ? 'This will delete all your game data while keeping your account. Are you sure?'
                            : 'Это удалит все ваши игровые данные, но сохранит ваш аккаунт. Вы уверены?'}
                        </p>
                        <div className="confirm-buttons" style={{ display: 'flex', gap: '10px' }}>
                          <button 
                            className="form-button" 
                            style={{ backgroundColor: '#ff9800', color: 'white', flex: 1 }}
                            onClick={handleTruncateUserData}
                          >
                            {currentLang === 'en' ? 'Yes, delete all my data' : 'Да, удалить все мои данные'}
                          </button>
                          <button 
                            className="form-button" 
                            style={{ backgroundColor: '#f0f0f0', color: '#333', flex: 1 }}
                            onClick={() => setTruncateConfirm(false)}
                          >
                            {currentLang === 'en' ? 'Cancel' : 'Отмена'}
                          </button>
                        </div>
                      </div>
                    ) : (
                      <button 
                        className="form-button" 
                        style={{ backgroundColor: '#ff9800', color: 'white', width: '100%' }}
                        onClick={handleTruncateUserData}
                      >
                        {currentLang === 'en' ? 'Delete All My Data' : 'Удалить все мои данные'}
                      </button>
                    )}
                  </div>
                  
                  {/* Logout Section */}
                  <div style={{ marginTop: '20px' }}>
                    <button 
                      className="form-button" 
                      style={{ backgroundColor: '#4a6da7', color: 'white', width: '100%' }}
                      onClick={handleLogout}
                    >
                      {currentLang === 'en' ? 'Logout' : 'Выйти'}
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Saves Modal */}
      {showSaves && (
        <div className="modal-overlay" onClick={handleCloseSaves}>
          <div className="saves-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header" style={{ position: 'relative' }}>
              <h3>{currentLang === 'ru' ? 'Сохранения' : 'Saves'}</h3>
              <button onClick={handleCloseSaves} className="close-button" aria-label="Close">×</button>
            </div>
            
            <div className="modal-content">
              {savesError && <div className="error-message">{savesError}</div>}
              
              <div className="save-form">
                <input 
                  type="text" 
                  value={saveDescription} 
                  onChange={(e) => setSaveDescription(e.target.value)} 
                  placeholder={currentLang === 'ru' ? 'Описание сохранения' : 'Save description'} 
                  className="save-input"
                />
                {editingSaveId ? (
                  <button 
                    className="save-button" 
                    onClick={handleUpdateSave} 
                    disabled={savingGame}
                  >
                    {savingGame ? (currentLang === 'ru' ? 'Обновление...' : 'Updating...') : 
                                 (currentLang === 'ru' ? 'Обновить' : 'Update')}
                  </button>
                ) : null}
              </div>
              
              <div className="saves-list">
                {savesLoading ? (
                  <div className="loading">{currentLang === 'ru' ? 'Загрузка...' : 'Loading...'}</div>
                ) : saves.length === 0 ? (
                  <div className="no-saves">{currentLang === 'ru' ? 'Нет сохранений' : 'No saves found'}</div>
                ) : (
                  saves.map(save => (
                    <div key={save.id} className="save-item">
                      <div className="save-info">
                        <div className="save-description">{save.description}</div>
                        <div className="save-date">
                          {new Date(save.created_at).toLocaleString(currentLang === 'ru' ? 'ru-RU' : 'en-US')}
                        </div>
                      </div>
                      <div className="save-actions">
                        <button 
                          className="action-button load" 
                          onClick={() => handleLoadSave(save.game_state_id)}
                          disabled={loadingSave}
                        >
                          {currentLang === 'ru' ? 'Загрузить' : 'LOAD'}
                        </button>
                        <button 
                          className="action-button edit" 
                          onClick={() => handleEditSave(save)}
                        >
                          {currentLang === 'ru' ? 'Изменить' : 'EDIT'}
                        </button>
                        <button 
                          className="action-button delete" 
                          onClick={() => handleDeleteSave(save.id)}
                        >
                          {currentLang === 'ru' ? 'Удалить' : 'DELETE'}
                        </button>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Help Modal */}
      {showHelpModal && (
        <div className="form-overlay">
          <div className="form-container">
            <button className="close-button" onClick={handleCloseHelpModal}>&times;</button>
            <h2>{t.help}</h2>
            <div className="help-content" style={{ textAlign: 'left', lineHeight: '1.6' }}>
              <p>{t.helpIntro || "This is a visual novel game powered by AI 🎮"}</p>
              <ul>
                <li>{t.helpItem1 || "🎬 Action takes place in a Soviet pioneer camp."}</li>
                <li>{t.helpItem2 || "🔞 Every character here is 18 years old!"}</li>
                <li>{t.helpItem3 || "✍️ Write your actions and characters will respond accordingly."}</li>
                <li>{t.helpItem4 || "🧠 They have memory."}</li>
                <li>{t.helpItem5 || "🎶 The music and character emotions will change depending on the context."}</li>
                <li>{t.helpItem6 || "🗺️ Use the map to change locations."}</li>
                <li>{t.helpItem7 || "⏳ Click on \"wait\" to advance time."}</li>
                <li>{t.helpItem8 || "🗣️ Persuade characters to follow you to any location."}</li>
                <li>{t.helpItem9 || "🖱️ Click on the background to continue the story, or type a message and click 'Send' to interact with characters."}</li>
              </ul>
              <p style={{ color: '#d9534f', fontWeight: 'bold', marginTop: '20px', padding: '10px', backgroundColor: 'rgba(217, 83, 79, 0.1)', borderRadius: '5px' }}>
                {currentLang === 'en' 
                  ? "🌐 Language Support: You can input text in any language! If you've selected 'auto-detect' in your account settings, the game will automatically detect your language. Alternatively, choose your preferred language from the dropdown menu in your account settings if you experience any issues with auto-detection."
                  : "🌐 Поддержка языков: Вы можете вводить текст на любом языке! Если вы выбрали 'автоопределение' в настройках аккаунта, игра автоматически определит ваш язык. Alternatively, выберите предпочитаемый язык из выпадающего меню в настройках аккаунта, если у вас возникают проблемы с автоопределением."}
              </p>
            </div>
          </div>
        </div>
      )}

      <div className="content">
        <h1 className="title">Red Camp Tale</h1>
        
        {/* Main success message display */}
        {mainSuccessMessage && (
          <div className="success-message" style={{ marginBottom: '20px', padding: '10px', backgroundColor: '#d4edda', color: '#155724', borderRadius: '4px', textAlign: 'center' }}>
            {mainSuccessMessage}
          </div>
        )}
        
        {/* Show different content based on authentication status */}
        {!isAuthenticated ? (
          /* Unauthenticated users - show only login/register options */
          <div className="auth-buttons-container">
            <p className="auth-prompt">
              {currentLang === 'en' 
                ? 'Please log in or create an account to start playing' 
                : 'Пожалуйста, войдите в систему или создайте аккаунт, чтобы начать играть'}
            </p>
            <div className="buttons-container">
              <button className="game-button" onClick={handleShowLoginForm}>
                {currentLang === 'en' ? 'Login' : 'Войти'}
              </button>
              <button className="game-button" onClick={handleShowRegisterForm}>
                {currentLang === 'en' ? 'Register' : 'Зарегистрироваться'}
              </button>
            </div>
          </div>
        ) : loadingUserData ? (
          /* Loading user data */
          <div className="loading-container">
            <p>{currentLang === 'en' ? 'Loading user data...' : 'Загрузка данных пользователя...'}</p>
          </div>
        ) : userData ? (
          /* Authenticated users - show full game interface */
          <div className="authenticated-content">
            <div className="user-welcome" style={{ marginBottom: '20px', padding: '15px', backgroundColor: 'rgba(0, 100, 0, 0.7)', color: 'white', borderRadius: '5px', textAlign: 'center' }}>
              <h2 style={{ margin: '0 0 10px 0' }}>
                {currentLang === 'en' 
                  ? `Welcome back, ${userData.name || 'Player'}!` 
                  : `Добро пожаловать, ${userData.name || 'Игрок'}!`}
              </h2>
              {userData.user_biography_displayed_name && (
                <p style={{ margin: '0', fontSize: '1.2em' }}>
                  {currentLang === 'en' ? 'Playing as: ' : 'Играете за: '}
                  <strong>{userData.user_biography_displayed_name}</strong>
                </p>
              )}
            </div>
            
            <div className="buttons-container">
              <button className="game-button" onClick={() => navigate(`/${currentLang}/game`)}>
                {currentLang === 'en' ? 'Continue' : 'Продолжить'}
              </button>
              <button className="game-button" onClick={handleNewGame} disabled={newGameLoading}>
                {newGameLoading ? (currentLang === 'ru' ? 'Загрузка...' : 'Loading...') : t.newGame}
              </button>
              
              <button className="game-button" onClick={handleMyAccountClick}>{t.myAccount}</button>
              
              <button className="game-button" onClick={handleSavesClick}>{t.saves}</button>
              <button className="game-button" onClick={handleHelpClick}>{t.help}</button>
              <button className="game-button" onClick={handleContactsClick}>{t.contacts}</button>
            </div>
          </div>
        ) : (
          /* Error state */
          <div className="error-container">
            <p style={{ color: '#d9534f' }}>
              {currentLang === 'en' 
                ? 'Failed to load user data. Please try logging in again.' 
                : 'Не удалось загрузить данные пользователя. Пожалуйста, попробуйте войти снова.'}
            </p>
            <div className="buttons-container">
              <button className="game-button" onClick={handleShowLoginForm}>
                {currentLang === 'en' ? 'Login' : 'Войти'}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default HomePage;
