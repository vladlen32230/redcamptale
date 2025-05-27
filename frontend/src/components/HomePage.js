import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import translations from '../translations';
import '../styles/HomePage.css';

// Backend URL configuration
const BACKEND_URL = 'https://redcamptalesbackend-409594015641.europe-north1.run.app';

const HomePage = () => {
  // Authentication state - determined by JWT in localStorage
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  
  // Check for JWT token on component mount
  useEffect(() => {
    const token = localStorage.getItem('token');
    setIsAuthenticated(!!token);
  }, []);
  
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
      // Close the form
      handleCloseForm();
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
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [savesLoading, setSavesLoading] = useState(false);
  const [savesError, setSavesError] = useState('');
  const [savingGame, setSavingGame] = useState(false);
  const [loadingSave, setLoadingSave] = useState(false);
  
  // Account state
  const [userData, setUserData] = useState(null);
  const [accountFormData, setAccountFormData] = useState({});
  const [updateSuccess, setUpdateSuccess] = useState('');
  const [updateError, setUpdateError] = useState('');
  const [isUpdatingAccount, setIsUpdatingAccount] = useState(false); // For account update loading state
  const [deleteConfirm, setDeleteConfirm] = useState(false);
  const [truncateConfirm, setTruncateConfirm] = useState(false);
  const [saves, setSaves] = useState([]);
  const [saveDescription, setSaveDescription] = useState('');
  const [editingSaveId, setEditingSaveId] = useState(null);

  // Add some custom styles for the account modal
  const modalStyles = {
    authSection: {
      marginBottom: '20px',
      padding: '15px',
      backgroundColor: 'rgba(0, 0, 0, 0.05)',
      borderRadius: '5px',
      border: '1px solid #ddd'
    },
    authButtons: {
      display: 'flex',
      gap: '10px',
      marginTop: '15px'
    },
    formButton: {
      minWidth: '120px'
    }
  };

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
    // Always fetch user data and show account modal
    setLoading(true);
    setError('');
    setUpdateError('');
    setUpdateSuccess('');
    try {
      // Get token if available
      const token = localStorage.getItem('token');
      const headers = token ? { 'Authorization': `Bearer ${token}` } : {};
      
      // Map currentLang for the query parameter
      const apiQueryLanguage = currentLang === 'en' ? 'english' : 'russian';

      // Fetch user data - the backend will return IP-based user if not authenticated
      // Append language query parameter
      const response = await fetch(`${BACKEND_URL}/api/v1/user/me?lang=${apiQueryLanguage}`, {
        method: 'GET',
        headers: headers
      });
      
      if (!response.ok) {
        // If unauthorized but we had a token, it's likely expired
        if (response.status === 401 && token) {
          localStorage.removeItem('token');
          setIsAuthenticated(false);
          // Try again without the token
          return handleMyAccountClick();
        }
        throw new Error(currentLang === 'en' ? 'Failed to load account data' : 'Не удалось загрузить данные аккаунта');
      }
      
      const data = await response.json();
      setUserData(data);

      // Determine which biography to display based on currentLang
      let biographyNameToDisplay = data.user_biography_name;
      let biographyDescriptionToDisplay = data.user_biography_description;

      if (currentLang === 'ru' && data.user_biography_russian_name && data.user_biography_russian_description) {
        biographyNameToDisplay = data.user_biography_russian_name;
        biographyDescriptionToDisplay = data.user_biography_russian_description;
      }

      setAccountFormData({
        game_name: biographyNameToDisplay,
        game_biography: biographyDescriptionToDisplay
      });
      setShowAccountModal(true);
    } catch (error) {
      setError(error.message);
      // Still show account modal even if there's an error
      setShowAccountModal(true);
      
      // Clear error message after 1 second
      setTimeout(() => {
        setError('');
      }, 3000);
    } finally {
      setLoading(false);
    }
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
      // Only include Authorization header if token exists
      const headers = token 
        ? { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' } 
        : { 'Content-Type': 'application/json' };
      
      // Map currentLang to backend expected values for the payload
      const apiPayloadLanguage = currentLang === 'en' ? 'english' : 'russian';

      // Send current language with the payload
      const payload = {
        ...accountFormData, // This will send game_name and game_biography as currently in the form
        language: apiPayloadLanguage // Use mapped language
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

      // Determine which biography to display from the updated user data
      let updatedBiographyNameToDisplay = updatedUserData.user_biography_name;
      let updatedBiographyDescriptionToDisplay = updatedUserData.user_biography_description;

      if (currentLang === 'ru' && updatedUserData.user_biography_russian_name && updatedUserData.user_biography_russian_description) {
        updatedBiographyNameToDisplay = updatedUserData.user_biography_russian_name;
        updatedBiographyDescriptionToDisplay = updatedUserData.user_biography_russian_description;
      }
      
      setAccountFormData({
        game_name: updatedBiographyNameToDisplay,
        game_biography: updatedBiographyDescriptionToDisplay
      });
      setUpdateSuccess(currentLang === 'en' ? 'Account updated successfully!' : 'Аккаунт успешно обновлен!');
      
      // Clear success message after 1 second
      setTimeout(() => {
        setUpdateSuccess('');
      }, 3000);
    } catch (error) {
      setUpdateError(error.message);
      
      // Clear error message after 1 second
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
            
            {error && <div className="error-message">{error}</div>}
            {loading ? (
              <p>{currentLang === 'en' ? 'Loading...' : 'Загрузка...'}</p>
            ) : userData && (
              <div className="account-details">
                {!isAuthenticated && (
                  <div className="auth-section" style={modalStyles.authSection}>
                    <h3>{currentLang === 'en' ? 'Authentication' : 'Авторизация'}</h3>
                    <p>{currentLang === 'en' ? 'You are not logged in.' : 'Вы не вошли в систему.'}</p>
                    <div className="auth-buttons" style={modalStyles.authButtons}>
                      <button 
                        className="form-button" 
                        style={modalStyles.formButton} 
                        onClick={() => {
                          setShowAccountModal(false);
                          handleShowLoginForm();
                        }}
                      >
                        {currentLang === 'en' ? 'Login' : 'Войти'}
                      </button>
                      <button 
                        className="form-button" 
                        style={modalStyles.formButton} 
                        onClick={() => {
                          setShowAccountModal(false);
                          handleShowRegisterForm();
                        }}
                      >
                        {currentLang === 'en' ? 'Register' : 'Зарегистрироваться'}
                      </button>
                    </div>
                  </div>
                )}
                
                <div className="account-info">
                  <h3>{currentLang === 'en' ? 'Account Information' : 'Информация об аккаунте'}</h3>
                  {userData.name && <p style={{ fontSize: '2rem' }}><strong>{currentLang === 'en' ? 'Username' : 'Имя пользователя'}:</strong> {userData.name}</p>}
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
                        value={accountFormData.game_name}
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
                        value={accountFormData.game_biography}
                        onChange={handleAccountUpdateChange}
                        rows="4"
                        required
                      ></textarea>
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
                  {/* Authenticated-only actions */}
                  {isAuthenticated && (
                    <>
                      <div style={{ marginBottom: '15px' }}>
                        <button 
                          className="form-button" 
                          style={{ backgroundColor: '#4a6da7', color: 'white', width: '100%' }}
                          onClick={() => {
                            handleLogout();
                            setShowAccountModal(false);
                          }}
                        >
                          {currentLang === 'en' ? 'Logout' : 'Выйти'}
                        </button>
                      </div>
                      
                      {/* Delete Account Section - only for authenticated users */}
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
                    </>
                  )}
                  
                  {/* Truncate User Data Section - always visible for all users */}
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
        
        <div className="buttons-container">
          <button className="game-button" onClick={() => navigate(`/${currentLang}/game`)}>{currentLang === 'en' ? 'Continue' : 'Продолжить'}</button>
          <button className="game-button" onClick={handleNewGame} disabled={newGameLoading}>
            {newGameLoading ? (currentLang === 'ru' ? 'Загрузка...' : 'Loading...') : t.newGame}
          </button>
          
          <button className="game-button" onClick={handleMyAccountClick}>{t.myAccount}</button>
          
          <button className="game-button" onClick={handleSavesClick}>{t.saves}</button>
          <button className="game-button" onClick={handleHelpClick}>{t.help}</button>
          <button className="game-button" onClick={handleContactsClick}>{t.contacts}</button>
        </div>
        

      </div>
    </div>
  );
};

export default HomePage;
