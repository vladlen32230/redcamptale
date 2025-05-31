import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import translations from '../translations';
import '../styles/GamePage.css';

// Backend URL configuration
const BACKEND_URL = 'https://redcamptalesbackend-409594015641.europe-north1.run.app';

// Define character colors
const characterColors = {
  'ulyana': 'red',
  'miku': 'turquoise',
  'slavya': 'yellow',
  'alice': 'orange',
  'lena': 'violet',
  'main_character': 'green' 
};

// Message history component to display all messages
const MessageHistory = ({ messages, currentLang, onMessageClick }) => {
  if (!messages || messages.length === 0) return null;
  
  const getCharacterDisplayName = (characterName) => {
    if (characterName === 'main_character') {
      return currentLang === 'ru' ? 'Вы' : 'You';
    }
    return characterName;
  };

  return (
    <div className="message-history" style={{ minHeight: '100%', display: 'flex', flexDirection: 'column' }}>
      {messages.map((msg, index) => (
        <div 
          key={index} 
          className="message-item clickable" 
          onClick={() => onMessageClick && onMessageClick(msg.game_state_id)}
        >
          <div 
            className="character-name" 
            style={{ color: characterColors[msg.character.toLowerCase()] || 'inherit' }}
          >
            {getCharacterDisplayName(msg.character)}
          </div>
          <div className="message-text">
            {currentLang === 'ru' && msg.russian_translation
              ? msg.russian_translation
              : msg.english_text}
          </div>
        </div>
      ))}
    </div>
  );
};

const GamePage = () => {
  const { lang } = useParams();
  const navigate = useNavigate();
  const currentLang = lang && (lang === 'en' || lang === 'ru') ? lang : 'en';
  const t = translations[currentLang] || translations.en;
  
  const [gameState, setGameState] = useState(null);
  const [previousCharacters, setPreviousCharacters] = useState([]);
  const [characterTransitioning, setCharacterTransitioning] = useState(false);

  const [error, setError] = useState(null);
  const [userInput, setUserInput] = useState('');
  const [showMap, setShowMap] = useState(false);
  const [mapCharacters, setMapCharacters] = useState([]);
  const [mapLoading, setMapLoading] = useState(false);
  const [locationChanging, setLocationChanging] = useState(false);

  const [sendingMessage, setSendingMessage] = useState(false);
  const [waiting, setWaiting] = useState(false);
  const [showHistory, setShowHistory] = useState(false);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [historyError, setHistoryError] = useState(null);
  const [historyMessages, setHistoryMessages] = useState([]);
  
  // Saves modal state
  const [showSaves, setShowSaves] = useState(false);
  const [saves, setSaves] = useState([]);
  const [savesLoading, setSavesLoading] = useState(false);
  const [savesError, setSavesError] = useState(null);
  const [saveDescription, setSaveDescription] = useState('');
  const [editingSaveId, setEditingSaveId] = useState(null);
  const [savingGame, setSavingGame] = useState(false);
  const [loadingSave, setLoadingSave] = useState(false);
  
  // Music state
  const [currentMusicType, setCurrentMusicType] = useState(null);
  const [currentMusicUrl, setCurrentMusicUrl] = useState(null);
  const [musicFading, setMusicFading] = useState(false);
  const [isMuted, setIsMuted] = useState(false); // Mute state
  
  // Initialize audio refs - using a ref to hold the audio instance
  const audioRef = useRef(null);
  const newAudioRef = useRef(null);
  
  // Message typing effect states and refs
  const [displayedMessageText, setDisplayedMessageText] = useState('');
  const isNewInteractionMessageRef = useRef(false);
  const typingIntervalRef = useRef(null);
  
  // Initialize audio on component mount
  useEffect(() => {
    // Create initial audio object
    audioRef.current = new Audio();
    newAudioRef.current = new Audio();
    
    return () => {
      // Clean up audio on unmount
      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current = null;
      }
      if (newAudioRef.current) {
        newAudioRef.current.pause();
        newAudioRef.current = null;
      }
    };
  }, []);
  
  // Helper function for character display name and style
  const getCharacterDisplayNameAndStyle = (characterName) => {
    const displayName = characterName === 'main_character' 
      ? (currentLang === 'ru' ? 'Вы' : 'You') 
      : characterName;
    const style = { color: characterColors[characterName?.toLowerCase()] || 'inherit' };
    return { displayName, style };
  };
  
  // Effect to handle page visibility changes for music playback
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (document.hidden) {
        // Page is hidden, pause music
        if (audioRef.current && !audioRef.current.paused) {
          audioRef.current.pause();
        }
        if (newAudioRef.current && !newAudioRef.current.paused) {
          // Pause the incoming track during a crossfade
          newAudioRef.current.pause();
        }
      } else {
        // Page is visible, resume music if it was playing and is now paused
        if (audioRef.current && audioRef.current.paused && currentMusicUrl && !isMuted) {
          audioRef.current.play().catch(e => {
            console.warn('Audio resume on visibility change failed:', e);
            // Autoplay might be prevented by the browser
          });
        }
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);

    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
  }, [currentMusicUrl, isMuted]);
  
  // Apply game state update with transitions for characters
  const updateGameStateWithTransitions = (newState) => {
    if (gameState && gameState.characters && newState.characters) {
      // Only apply transition if characters are actually changing
      const currentCharacterIds = gameState.characters.map(c => c.pose_url).sort().join('|');
      const newCharacterIds = newState.characters.map(c => c.pose_url).sort().join('|');
      
      if (currentCharacterIds !== newCharacterIds) {
        // Save current characters for transition
        setPreviousCharacters(gameState.characters);
        setCharacterTransitioning(true);
        
        // Apply new game state after a short delay to allow transition effect
        setTimeout(() => {
          setGameState(newState);
          
          // Reset transition after a delay to complete the fade-in
          setTimeout(() => {
            setCharacterTransitioning(false);
          }, 800); // Match the CSS animation duration
        }, 400); // Slightly shorter delay before showing new state
      } else {
        // Characters haven't changed, just update the state
        setGameState(newState);
      }
    } else {
      // If no previous characters, just update normally
      setGameState(newState);
    }
  };
  
  // Fetch game state from API
  useEffect(() => {
    const fetchGameState = async () => {
      try {
        // Get token from localStorage if available
        const token = localStorage.getItem('token');
        const headers = { 'Authorization': token ? `Bearer ${token}` : '' };
        
        const response = await fetch(`${BACKEND_URL}/api/v1/game_state/continue`, {
          method: 'GET',
          headers: headers
        });
        
        if (!response.ok) {
          throw new Error(`Error: ${response.status}`);
        }
        
        const data = await response.json();
        setGameState(data);
        setError(null);
      } catch (err) {
        setError(err.message || 'Failed to fetch game state');
        console.error('Error fetching game state:', err);
      }
    };
    
    fetchGameState();
  }, []);
  
  // Function to select a random music URL from the list
  const getRandomMusicUrl = (musicUrls) => {
    if (!musicUrls || musicUrls.length === 0) return null;
    const randomIndex = Math.floor(Math.random() * musicUrls.length);
    return musicUrls[randomIndex];
  };
  
  // Handle music playback when gameState changes or when current song ends
  useEffect(() => {
    if (!gameState || !audioRef.current) return;

    if (isMuted) {
      if (audioRef.current && !audioRef.current.paused) {
        audioRef.current.pause();
      }
      if (newAudioRef.current && !newAudioRef.current.paused) {
        newAudioRef.current.pause();
      }
      if(audioRef.current) audioRef.current.volume = 0;
      if(newAudioRef.current) newAudioRef.current.volume = 0;
      return; 
    }
    
    // When NOT muted (isMuted is false):
    // If the current track URL is set, not fading, and its volume somehow became 0 while not muted,
    // restore it. This is a safeguard. handleMuteToggle should primarily handle unmute volume restoration.
    if (audioRef.current && audioRef.current.src === currentMusicUrl && !musicFading && audioRef.current.volume === 0 && currentMusicUrl) {
      audioRef.current.volume = 1.0;
    }

    const handleMusicLogic = () => {
      // If music type is "none", fade out current music if playing
      if (gameState.music_type === "none") {
        if (audioRef.current && !audioRef.current.paused) {
          setMusicFading(true);
          const fadeOutInterval = setInterval(() => {
            if (audioRef.current && audioRef.current.volume > 0.1) {
              audioRef.current.volume -= 0.1;
            } else {
              clearInterval(fadeOutInterval);
              if (audioRef.current) {
                audioRef.current.pause();
              }
              setCurrentMusicUrl(null);
              setMusicFading(false);
            }
          }, 100);
        }
        return;
      }
      
      // If music type is different from current, change the music with cross-fade
      if (gameState.music_type !== currentMusicType) {
        setCurrentMusicType(gameState.music_type);
        
        // Select a random music URL from the array
        const newMusicUrl = getRandomMusicUrl(gameState.music_urls);
        if (!newMusicUrl) return; // No valid URL, exit early
        
        // If we already have music playing, crossfade
        if (audioRef.current && !audioRef.current.paused) {
          setCurrentMusicUrl(newMusicUrl);
          setMusicFading(true);
          
          // Set up the new audio
          if (newAudioRef.current) {
            newAudioRef.current.src = newMusicUrl;
            newAudioRef.current.volume = 0; // Start at 0 for fade-in
            
            const playNewAudio = () => {
              if (isMuted) { // Check mute status before playing
                newAudioRef.current.pause();
                newAudioRef.current.volume = 0;
                if(audioRef.current) audioRef.current.volume = 0; 
                setMusicFading(false);
                return;
              }
              newAudioRef.current.play().catch(e => {
                console.warn('Audio playback was prevented by browser:', e);
              });
              
              // Crossfade
              let volume = 0;
              const fadeInterval = setInterval(() => {
                volume += 0.1;
                if (newAudioRef.current) newAudioRef.current.volume = isMuted ? 0 : Math.min(volume, 1);
                if (audioRef.current) audioRef.current.volume = isMuted ? 0 : Math.max(1 - volume, 0);
                
                if (volume >= 1) {
                  clearInterval(fadeInterval);
                  if (audioRef.current) {
                    audioRef.current.pause();
                  }
                  
                  // Swap refs to maintain the primary audio ref
                  const temp = audioRef.current;
                  audioRef.current = newAudioRef.current;
                  newAudioRef.current = temp;
                  setMusicFading(false);
                }
              }, 100);
            };
            
            // Use event listener or direct play based on browser state
            if (newAudioRef.current.readyState >= 3) {
              // Audio is ready to play
              playNewAudio();
            } else {
              // Wait for audio to be ready
              const canPlayHandler = () => {
                playNewAudio();
                newAudioRef.current.removeEventListener('canplaythrough', canPlayHandler);
              };
              newAudioRef.current.addEventListener('canplaythrough', canPlayHandler);
              
              // Set a timeout in case canplaythrough doesn't fire
              setTimeout(() => {
                if (musicFading) {
                  newAudioRef.current.removeEventListener('canplaythrough', canPlayHandler);
                  playNewAudio();
                }
              }, 2000);
            }
          }
        } 
        // No music playing, just start new music
        else if (audioRef.current) {
          setCurrentMusicUrl(newMusicUrl);
          audioRef.current.src = newMusicUrl;
          audioRef.current.volume = 0; // Start at 0 for fade-in
          
          const playAudio = () => {
            if (isMuted) { // Check mute status before playing
              audioRef.current.pause();
              audioRef.current.volume = 0;
              setMusicFading(false);
              return;
            }
            audioRef.current.play().catch(e => {
              console.warn('Audio playback was prevented by browser:', e);
            });
            
            // Fade in
            let volume = 0;
            const fadeInInterval = setInterval(() => {
              volume += 0.1;
              if (audioRef.current) audioRef.current.volume = isMuted ? 0 : Math.min(volume, 1);
              
              if (volume >= 1) {
                clearInterval(fadeInInterval);
                setMusicFading(false);
              }
            }, 100);
          };
          
          // Use event listener or direct play based on browser state
          if (audioRef.current.readyState >= 3) {
            // Audio is ready to play
            playAudio();
          } else {
            // Wait for audio to be ready
            const canPlayHandler = () => {
              playAudio();
              audioRef.current.removeEventListener('canplaythrough', canPlayHandler);
            };
            audioRef.current.addEventListener('canplaythrough', canPlayHandler);
            
            // Set a timeout in case canplaythrough doesn't fire
            setTimeout(() => {
              if (musicFading) {
                audioRef.current.removeEventListener('canplaythrough', canPlayHandler);
                playAudio();
              }
            }, 2000);
          }
        }
      }
    };
    
    handleMusicLogic();
    
    // Add an event listener for when the audio ends
    const handleAudioEnded = () => {
      // When the current track ends, pick a new random track from the list
      if (gameState.music_urls && gameState.music_urls.length > 0) {
        const newMusicUrl = getRandomMusicUrl(gameState.music_urls);
        if (!newMusicUrl) return; // No valid URL, exit early
        
        setCurrentMusicUrl(newMusicUrl);
        
        if (audioRef.current) {
          audioRef.current.src = newMusicUrl;
          if (!isMuted) { // Check mute status before playing
            audioRef.current.play().catch(e => {
              console.warn('Audio playback was prevented by browser:', e);
            });
          } else {
            audioRef.current.volume = 0;
          }
        }
      }
    };
    
    if (audioRef.current) {
      audioRef.current.addEventListener('ended', handleAudioEnded);
    }
    
    return () => {
      if (audioRef.current) {
        audioRef.current.removeEventListener('ended', handleAudioEnded);
      }
    };
  }, [gameState, currentMusicType, isMuted, currentMusicUrl, musicFading]);
  
  const handleUserInputChange = (e) => {
    setUserInput(e.target.value);
  };
  
  const handleMenuClick = () => {
    navigate(`/${currentLang}`);
  };
  
  const handleMuteToggle = () => {
    const newMutedState = !isMuted;
    setIsMuted(newMutedState);

    if (!newMutedState) { // Just unmuted
      if (audioRef.current) {
        audioRef.current.volume = 1.0; // Restore volume first
        // If music was playing (currentMusicUrl exists) and is paused, try to resume
        if (audioRef.current.paused && currentMusicUrl) {
          audioRef.current.play().catch(e => console.warn("Failed to play on unmute in toggle:", e));
        }
      }
      if (newAudioRef.current) {
        // Also restore volume for the secondary audio element, if it exists and was muted.
        // Playback for newAudioRef is typically handled by crossfade logic.
        newAudioRef.current.volume = 1.0; 
      }
    } 
    // When muting (newMutedState is true), the useEffect hook for isMuted will handle pausing and setting volume to 0.
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
  
  const handleCreateSave = async () => {
    // Get the current game state ID - safely access nested properties
    let gameStateId;
    if (gameState && gameState.id) {
      gameStateId = gameState.id;
    } else if (gameState && gameState.message && gameState.message.game_state_id) {
      gameStateId = gameState.message.game_state_id;
    } else if (gameState && gameState.message && gameState.message.message && gameState.message.message.game_state_id) {
      gameStateId = gameState.message.message.game_state_id;
    } else {
      console.error('Game state structure:', gameState);
      setSavesError('No active game state to save');
      return;
    }
    
    setSavingGame(true);
    setSavesError(null);
    
    try {
      const token = localStorage.getItem('token');
      const headers = {
        'Authorization': token ? `Bearer ${token}` : '',
        'Content-Type': 'application/json'
      };
      
      const response = await fetch(`${BACKEND_URL}/api/v1/save`, {
        method: 'POST',
        headers: headers,
        body: JSON.stringify({
          description: saveDescription || 'Quicksave',
          game_state_id: gameStateId
        })
      });
      
      if (!response.ok) {
        throw new Error(`Error: ${response.status}`);
      }
      
      // Refresh saves list
      await fetchSaves();
      setSaveDescription('');
    } catch (err) {
      setSavesError(err.message || 'Failed to create save');
      console.error('Error creating save:', err);
    } finally {
      setSavingGame(false);
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
      
      const response = await fetch(`${BACKEND_URL}/api/v1/game_state/${gameStateId}`, {
        method: 'GET',
        headers: headers
      });
      
      if (!response.ok) {
        throw new Error(`Error: ${response.status}`);
      }
      
      const data = await response.json();
      updateGameStateWithTransitions(data);
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

  
  const handleMapClick = async () => {
    if (!gameState) return;
    
    setShowMap(true);
    setMapLoading(true);
    
    try {
      // Get token from localStorage if available
      const token = localStorage.getItem('token');
      const headers = token ? { 'Authorization': `Bearer ${token}` } : {};
      
      // Get the current game state ID - safely access nested properties
      let gameStateId;
      if (gameState && gameState.message && gameState.message.game_state_id) {
        gameStateId = gameState.message.game_state_id;
      } else if (gameState && gameState.id) {
        // Fallback to gameState.id if available
        gameStateId = gameState.id;
      } else if (gameState && gameState.message && gameState.message.message && gameState.message.message.game_state_id) {
        // Try another possible path
        gameStateId = gameState.message.message.game_state_id;
      } else {
        console.error('No game state ID available');
        setError('No game state ID available');
        setMapLoading(false);
        return;
      }
      
      const response = await fetch(`${BACKEND_URL}/api/v1/game_state/${gameStateId}/map`, {
        method: 'GET',
        headers: headers
      });
      
      if (!response.ok) {
        throw new Error(`Error: ${response.status}`);
      }
      
      const data = await response.json();
      setMapCharacters(data);
    } catch (err) {
      setError(err.message || 'Failed to fetch map data');
    } finally {
      setMapLoading(false);
    }
  };
  
  const handleCloseMap = () => {
    setShowMap(false);
  };
  

  
  const handleLocationClick = async (locationName) => {
    if (!gameState || locationChanging) return;
    
    setLocationChanging(true);
    
    try {
      // Get token from localStorage if available
      const token = localStorage.getItem('token');
      const headers = {
        'Authorization': token ? `Bearer ${token}` : '',
        'Content-Type': 'application/json'
      };
      
      // Get the current game state ID
      let gameStateId;
      if (gameState && gameState.message && gameState.message.game_state_id) {
        gameStateId = gameState.message.game_state_id;
      } else if (gameState && gameState.id) {
        gameStateId = gameState.id;
      } else if (gameState && gameState.message && gameState.message.message && gameState.message.message.game_state_id) {
        gameStateId = gameState.message.message.game_state_id;
      } else {
        console.error('No game state ID available');
        setError('No game state ID available');
        setLocationChanging(false);
        return;
      }
      
      // Call the change_location endpoint
      const response = await fetch(`${BACKEND_URL}/api/v1/game_state/${gameStateId}/location`, {
        method: 'POST',
        headers: headers,
        body: JSON.stringify({
          new_location: locationName
        })
      });
      
      if (!response.ok) {
        throw new Error(`Error: ${response.status}`);
      }
      
      const data = await response.json();
      setGameState(data);
    } catch (err) {
      setError(err.message || 'Failed to change location');
      console.error('Error changing location:', err);
    } finally {
      setLocationChanging(false);
      setTimeout(() => setShowMap(false), 400); // 400ms delay for spinner visibility
    }
  };
  
  // Handle background image click to request character message
  const handleBackgroundClick = async () => {
    if (!gameState || waiting || sendingMessage) return;
    
    try {
      setSendingMessage(true);
      isNewInteractionMessageRef.current = true; // Signal for typing effect
      
      // Get token from localStorage if available
      const token = localStorage.getItem('token');
      const headers = { 
        'Authorization': token ? `Bearer ${token}` : '',
        'Content-Type': 'application/json'
      };
      
      const response = await fetch(`${BACKEND_URL}/api/v1/game_state/${gameState.id}/interaction`, {
        method: 'POST',
        headers: headers,
        body: JSON.stringify({
          user_interaction: false,
          user_text: null,
          language: currentLang === 'ru' ? 'russian' : 'english'
        })
      });
      
      if (!response.ok) {
        throw new Error(`Error: ${response.status}`);
      }
      
      const data = await response.json();
      updateGameStateWithTransitions(data);
      setError(null);
    } catch (err) {
      setError(err.message || 'Failed to fetch game state');
      console.error('Error fetching game state:', err);
    } finally {
      setSendingMessage(false);
    }
  };

  const handleHistoryClick = async () => {
    if (!gameState) return;
    setShowHistory(true);
    setHistoryLoading(true);
    setHistoryError(null);
    try {
      // Get token from localStorage if available
      const token = localStorage.getItem('token');
      const headers = { 'Authorization': token ? `Bearer ${token}` : '' };
      // Get the current game state ID - safely access nested properties
      let gameStateId;
      if (gameState && gameState.message && gameState.message.game_state_id) {
        gameStateId = gameState.message.game_state_id;
      } else if (gameState && gameState.id) {
        gameStateId = gameState.id;
      } else if (gameState && gameState.message && gameState.message.message && gameState.message.message.game_state_id) {
        gameStateId = gameState.message.message.game_state_id;
      } else {
        throw new Error('No game state ID available');
      }
      const response = await fetch(`${BACKEND_URL}/api/v1/game_state/${gameStateId}/messages?limit=50&offset=0`, {
        method: 'GET',
        headers: headers
      });
      if (!response.ok) {
        throw new Error(`Error: ${response.status}`);
      }
      const data = await response.json();
      // Keep the full MessageGameState objects to have access to game_state_id
      setHistoryMessages(data);
    } catch (err) {
      setHistoryError(err.message || 'Failed to fetch message history');
    } finally {
      setHistoryLoading(false);
    }
  };

  
  const handleHistoryMessageClick = async (gameStateId) => {
    if (!gameStateId) return;
    setWaiting(true);
    setShowHistory(false); // Close the history panel
    
    try {
      // Get token from localStorage if available
      const token = localStorage.getItem('token');
      const headers = { 'Authorization': token ? `Bearer ${token}` : '' };
      
      const response = await fetch(`${BACKEND_URL}/api/v1/game_state/${gameStateId}`, {
        method: 'GET',
        headers: headers
      });
      
      if (!response.ok) {
        throw new Error(`Error: ${response.status}`);
      }
      
      const data = await response.json();
      updateGameStateWithTransitions(data);
      setError(null);
    } catch (err) {
      setError(err.message || 'Failed to fetch game state');
      console.error('Error fetching game state:', err);
    } finally {
      setWaiting(false);
    }
  };

  const handleSendMessage = async () => {
    if (!userInput.trim()) return;
    setSendingMessage(true);
    try {
      isNewInteractionMessageRef.current = true; // Signal that the next message update is from user interaction
      // Get token from localStorage if available
      const token = localStorage.getItem('token');
      const headers = {
        'Content-Type': 'application/json',
        'Authorization': token ? `Bearer ${token}` : ''
      };
      
      // Get the current game state ID - safely access nested properties
      let gameStateId;
      if (gameState && gameState.id) {
        gameStateId = gameState.id;
      } else if (gameState && gameState.message && gameState.message.game_state_id) {
        gameStateId = gameState.message.game_state_id;
      } else if (gameState && gameState.message && gameState.message.message && gameState.message.message.game_state_id) {
        gameStateId = gameState.message.message.game_state_id;
      } else {
        console.error('Game state structure:', gameState);
        throw new Error('No game state ID available');
      }
      
      // Send POST request to the backend endpoint at line 109 in game_state.py
      const response = await fetch(`${BACKEND_URL}/api/v1/game_state/${gameStateId}/interaction`, {
        method: 'POST',
        headers: headers,
        body: JSON.stringify({
          user_interaction: true,
          user_text: userInput,
          language: currentLang === 'ru' ? 'russian' : 'english'
        })
      });
      
      if (!response.ok) {
        throw new Error(`Error: ${response.status}`);
      }
      
      const data = await response.json();
      updateGameStateWithTransitions(data);
      
      setUserInput('');
    } catch (err) {
      setError(err.message || 'Failed to send message');
      console.error('Error sending message:', err);
    } finally {
      setSendingMessage(false);
    }
  };
  
  // useEffect for message display and animation:
  useEffect(() => {
    // Always clear previous interval if active
    if (typingIntervalRef.current) {
      clearInterval(typingIntervalRef.current);
      typingIntervalRef.current = null;
    }

    const messageContainer = gameState?.message?.message;

    if (messageContainer && (messageContainer.english_text || messageContainer.russian_translation)) {
      const targetText = currentLang === 'ru' && messageContainer.russian_translation
        ? messageContainer.russian_translation
        : messageContainer.english_text;

      if (isNewInteractionMessageRef.current && targetText) {
        isNewInteractionMessageRef.current = false; // Consume the flag for this message instance

        setDisplayedMessageText(''); // Initialize for typing
        let charIndex = 0;
        typingIntervalRef.current = setInterval(() => {
          if (charIndex < targetText.length) {
            setDisplayedMessageText(targetText.substring(0, charIndex + 1));
            charIndex++;
          } else {
            clearInterval(typingIntervalRef.current);
            typingIntervalRef.current = null;
          }
        }, 25); // Adjust typing speed (e.g., 50ms per character)
      } else if (targetText) {
        // Not a new interaction message, or flag already consumed, or no targetText for animation: display full text immediately
        setDisplayedMessageText(targetText);
      } else {
        setDisplayedMessageText(''); // No text in message
      }
    } else {
      setDisplayedMessageText(''); // No message or empty message
    }

    // Cleanup function for when the component unmounts or dependencies change before interval finishes
    return () => {
      if (typingIntervalRef.current) {
        clearInterval(typingIntervalRef.current);
        typingIntervalRef.current = null;
      }
    };
  }, [gameState?.message, currentLang]);
  
  // Render error state
  if (error) {
    return (
      <div className="game-page">
        <div className="error-container">
          <h2>{t.error || 'Error'}</h2>
          <p>{error}</p>
          <button onClick={() => window.location.reload()}>{t.tryAgain || 'Try Again'}</button>
        </div>
      </div>
    );
  }
  
  // Render game interface
  return (
    <div className="game-page">
      {/* Fullscreen loading overlay when changing location */}
      {locationChanging && (
        <div className="fullscreen-loading-overlay">
          <div className="fullscreen-loading-spinner">
            <div className="loading-spinner"></div>
            <p>{t.loading || 'Loading...'}</p>
          </div>
        </div>
      )}
      
      {/* History Modal Overlay */}
      {showHistory && (
        <div className="map-modal">
          {historyError ? (
            <div className="error-container">
              <h2>{t.error || 'Error'}</h2>
              <p>{historyError}</p>
              <button onClick={() => setShowHistory(false)}>{t.tryAgain || 'Try Again'}</button>
            </div>
          ) : (
            <div className="map-container" style={{ width: '95%', height: '95vh', maxWidth: '95vw', background: 'transparent', borderRadius: 10, padding: 10, display: 'flex', flexDirection: 'column' }}>
              <div className="map-header" style={{ position: 'relative' }}>
                <h2>{currentLang === 'ru' ? 'История сообщений' : 'Message History'}</h2>
                <button onClick={() => setShowHistory(false)} className="close-button" aria-label="Close">×</button>
              </div>
              <div className="map-content" style={{ flex: 1, overflowY: 'auto', marginTop: 10, display: 'flex', flexDirection: 'column' }}>
                {historyLoading ? (
                  <div className="loading-container">
                    <div className="loading-spinner"></div>
                    <p>{t.loading || 'Loading...'}</p>
                  </div>
                ) : (
                  <div className="message-history-container" style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
                    <MessageHistory 
                      messages={historyMessages.map(item => ({
                        ...item.message,
                        game_state_id: item.game_state_id
                      }))} 
                      currentLang={currentLang} 
                      onMessageClick={handleHistoryMessageClick} 
                    />
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      )}
      {/* Background Image - clickable */}
      {gameState && gameState.background_url && (
        <div 
          className="game-background" 
          style={{ 
            backgroundImage: `url(${gameState.background_url})`,
            filter: sendingMessage ? 'brightness(0.5)' : 'none' // Darken background when sendingMessage is true
          }}
          onClick={handleBackgroundClick}
        ></div>
      )}
      
      {/* Character Sprites Container - clickable */}
      <div className="characters-container" onClick={handleBackgroundClick}>
        {/* Render previous characters with fade-out effect during transition */}
        {characterTransitioning && previousCharacters && previousCharacters.length > 0 && (
          <div className="characters-transition-container">
            {previousCharacters
              .sort((a, b) => a.pose_url.localeCompare(b.pose_url))
              .map((character, index) => (
              <div key={`prev-${index}`} className="character-sprite fading-out" style={{
                /* Calculate the position similar to current layout */
                position: 'relative',
                order: index
              }}>
                {/* Layered character images */}
                <div className="character-layer pose" style={{ 
                  backgroundImage: `url(${character.pose_url})`,
                  filter: sendingMessage ? 'brightness(0.5)' : 'none'
                }}></div>
                <div className="character-layer clothes" style={{ 
                  backgroundImage: `url(${character.clothes_url})`,
                  filter: sendingMessage ? 'brightness(0.5)' : 'none'
                }}></div>
                <div className="character-layer face" style={{ 
                  backgroundImage: `url(${character.facial_expression_url})`,
                  filter: sendingMessage ? 'brightness(0.5)' : 'none'
                }}></div>
              </div>
            ))}
          </div>
        )}
        
        {/* Render current characters with fade-in effect if transitioning */}
        {gameState && gameState.characters && [...gameState.characters]
          .sort((a, b) => a.pose_url.localeCompare(b.pose_url))
          .map((character, index) => (
          <div key={index} className={`character-sprite ${characterTransitioning ? 'fading-in' : ''}`}>
            {/* Layered character images */}
            <div className="character-layer pose" style={{ 
              backgroundImage: `url(${character.pose_url})`,
              filter: sendingMessage ? 'brightness(0.5)' : 'none' // Darken character when loading
            }}></div>
            <div className="character-layer clothes" style={{ 
              backgroundImage: `url(${character.clothes_url})`,
              filter: sendingMessage ? 'brightness(0.5)' : 'none' // Darken character when loading
            }}></div>
            <div className="character-layer face" style={{ 
              backgroundImage: `url(${character.facial_expression_url})`,
              filter: sendingMessage ? 'brightness(0.5)' : 'none' // Darken character when loading
            }}></div>
          </div>
        ))}
      </div>
      
      {/* Message Box */}
      <div className="message-box">
        {/* Game Control Buttons - NOW FIRST */}
        <div className="game-controls">
          <div className="left-controls">
            {/* Menu button removed from here */}
          </div>
          <div className="right-controls">
            <button className="control-button" onClick={handleMapClick}>
              {currentLang === 'ru' ? 'Карта' : 'Map'}
            </button>
            <button className="control-button" onClick={handleHistoryClick}>
              {currentLang === 'ru' ? 'История' : 'History'}
            </button>
            <button className="control-button" onClick={handleSavesClick}>
              {currentLang === 'ru' ? 'Сохранения' : 'Saves'}
            </button>
            <button className="control-button" onClick={handleMuteToggle}>
              {isMuted 
                ? (currentLang === 'ru' ? 'Вкл. звук' : 'Unmute') 
                : (currentLang === 'ru' ? 'Выкл. звук' : 'Mute')}
            </button>
            <button className="control-button" onClick={handleMenuClick}>
              {currentLang === 'ru' ? 'Меню' : 'Menu'}
            </button>
          </div>
        </div>

        {/* Display received messages - NOW SECOND */}
        <div className="messages-container" style={{marginTop: '10px'}}> {/* Adjusted margin */}
          {gameState && gameState.message && (
            <div className="message-content">
              <div 
                className="character-name"
                style={getCharacterDisplayNameAndStyle(gameState.message.message.character).style}
              >
                {getCharacterDisplayNameAndStyle(gameState.message.message.character).displayName}
              </div>
              <div className="message-text">
                {/* This will now use displayedMessageText which is animated or set directly */}
                {displayedMessageText}
              </div>
            </div>
          )}
        </div>

        {/* User Input Area - NOW LAST */}
        <div className="user-input-container">
          <input
            type="text"
            value={userInput}
            onChange={handleUserInputChange}
            placeholder={currentLang === 'ru' ? 'Введите сообщение...' : 'Type your message...'}
            className="user-input"
            onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
            disabled={sendingMessage}
          />
          <button onClick={handleSendMessage} className="send-button" disabled={sendingMessage}>
            {sendingMessage ? (
              <span className="input-loading-spinner"></span>
            ) : (
              currentLang === 'ru' ? 'Отправить' : 'Send'
            )}
          </button>
        </div>
      </div>
      
      {/* Map Modal */}
      {showMap && (
        <div className="map-modal">
          {waiting && (
            <div className="fullscreen-loading-overlay">
              <div className="fullscreen-loading-spinner">
                <div className="loading-spinner"></div>
                <p>{t.waiting || 'Waiting...'}</p>
              </div>
            </div>
          )}
          <div className="map-container">
            <div className="map-header" style={{ position: 'relative' }}>
              <h2>{currentLang === 'ru' ? 'Карта' : 'Map'}</h2>
              <button onClick={handleCloseMap} className="close-button" aria-label="Close">×</button>
            </div>
            <div className="map-content" style={{ position: 'relative' }}>
              <button
                className="control-button map-wait-button"
                onClick={async () => {
                  if (waiting) return;
                  setWaiting(true);
                  try {
                    // Get token from localStorage if available
                    const token = localStorage.getItem('token');
                    const headers = {};
                    if (token) headers['Authorization'] = `Bearer ${token}`;
                    // Get the current game state ID
                    let gameStateId;
                    if (gameState && gameState.message && gameState.message.game_state_id) {
                      gameStateId = gameState.message.game_state_id;
                    } else if (gameState && gameState.id) {
                      gameStateId = gameState.id;
                    } else if (gameState && gameState.message && gameState.message.message && gameState.message.message.game_state_id) {
                      gameStateId = gameState.message.message.game_state_id;
                    } else {
                      setWaiting(false);
                      setError('No game state ID available');
                      return;
                    }
                    const response = await fetch(`${BACKEND_URL}/api/v1/game_state/${gameStateId}/map`, {
                      method: 'POST',
                      headers: headers
                    });
                    if (!response.ok) {
                      throw new Error(`Error: ${response.status}`);
                    }
                    const data = await response.json();
                    setGameState(data);
                    setShowMap(false);
                  } catch (err) {
                    setError(err.message || 'Failed to wait');
                  } finally {
                    setWaiting(false);
                  }
                }}
                disabled={waiting}
              >
                {t.wait || 'Wait'}
              </button>
              <div className="map-image-wrapper">
                {mapLoading ? (
                  <div className="map-loading">
                    <div className="loading-spinner"></div>
                    <p>{t.loading || 'Loading...'}</p>
                  </div>
                ) : (
                  <>
                    {/* Map image with fixed size */}
                    <div className="map-image-container">
                      <img 
                        src="https://storage.googleapis.com/redcamptalesstatic/static/map.jpg" 
                        alt="Map" 
                        className="map-image" 
                        style={{maxHeight: '85vh', objectFit: 'contain'}}
                      />
                      
                      {/* Clickable location areas */}
                      {(() => {
                        // Define positions for each location as percentages of the map image
                        const mapPositions = {
                          'forest': { left: '32.5%', top: '12%' },
                          'main_character_home': { left: '51%', top: '18%' },
                          'ulyana_alice_home': { left: '38.5%', top: '59.5%' },
                          'beach': { left: '70.8%', top: '68.5%' },
                          'field': { left: '75%', top: '53%' },
                          'boathouse': { left: '46.5%', top: '76%' },
                          'island': { left: '42.5%', top: '91%' },
                          'square': { left: '49%', top: '43%' },
                          'stage': { left: '58%', top: '9%' },
                          'aidpost': { left: '57%', top: '37.5%' },
                          'underground_bunker': { left: '15%', top: '96%' },
                          'dining_hall': { left: '56%', top: '47%' },
                          'lena_miku_home': { left: '43.3%', top: '16%' },
                          'library': { left: '63.5%', top: '29%' },
                          'warehouse': { left: '26.5%', top: '51%' },
                          'outside': { left: '18%', top: '46%' },
                        };
                        
                        return Object.entries(mapPositions).map(([location, position]) => (
                          <div 
                            key={`location-${location}`}
                            className="location-marker"
                            onClick={() => handleLocationClick(location)}
                            style={{
                              position: 'absolute',
                              left: position.left,
                              top: position.top,
                              width: '5vw',
                              height: '5vw',
                              borderRadius: '50%',
                              backgroundColor: 'rgba(255, 255, 255, 0.3)',
                              border: '2px solid rgba(255, 255, 255, 0.7)',
                              transform: 'translate(-50%, -50%)',
                              cursor: 'pointer',
                              zIndex: 5,
                              display: 'block'
                            }}
                          >
                          </div>
                        ));
                      })()}
                    </div>
                    
                    {/* Character markers */}
                    {(() => {
                      // Group characters by location
                      const locationGroups = {};
                      mapCharacters.forEach(character => {
                        if (!locationGroups[character.location]) {
                          locationGroups[character.location] = [];
                        }
                        locationGroups[character.location].push(character);
                      });
                      
                      // Sort characters in each location group by character_head_url
                      Object.keys(locationGroups).forEach(location => {
                        locationGroups[location].sort((a, b) => 
                          a.character_head_url.localeCompare(b.character_head_url)
                        );
                      });

                      // Define positions for each location as percentages of the map image
                      const mapPositions = {
                        'forest': { left: '35%', top: '20%' },
                        'main_character_home': { left: '50%', top: '25%' },
                        'ulyana_alice_home': { left: '37%', top: '65%' },
                        'beach': { left: '72.5%', top: '75%' },
                        'field': { left: '76.5%', top: '60%' },
                        'boathouse': { left: '47%', top: '68%' },
                        'island': { left: '42.5%', top: '85%' },
                        'square': { left: '47%', top: '51%' },
                        'stage': { left: '58%', top: '18%' },
                        'aidpost': { left: '61%', top: '42.5%' },
                        'underground_bunker': { left: '15%', top: '87%' },
                        'dining_hall': { left: '58%', top: '56%' },
                        'lena_miku_home': { left: '43.3%', top: '25%' },
                        'library': { left: '67.5%', top: '20%' },
                        'warehouse': { left: '26.5%', top: '60%' },
                        'outside': { left: '18%', top: '55%' },
                      };
                      
                      // Render all characters
                      return Object.entries(locationGroups).flatMap(([location, characters]) => {
                        const basePosition = mapPositions[location] || { left: 400, top: 300 };
                        
                        return characters.map((character, charIndex) => {
                          // Simple array-like positioning
                          // Start from the middle position and arrange characters side by side
                          // For even number of characters: center around the middle
                          // For odd number of characters: center character at the middle
                          const totalChars = characters.length;
                          const spacing = 4;
                          
                          // Calculate horizontal position
                          const startOffset = ((totalChars - 1) * spacing) / 2;
                          const charOffset = charIndex * spacing;
                          const finalOffset = charOffset - startOffset;
                          
                          const baseLeft = parseFloat(basePosition.left);
                          const finalLeft = `${baseLeft + finalOffset}%`;
                          
                          const baseTop = parseFloat(basePosition.top);
                          const finalTop = `${baseTop}%`;
                          
                          return (
                            <div 
                              key={`${location}-${charIndex}`} 
                              className="character-head-only" 
                              style={{
                                position: 'absolute',
                                left: finalLeft,
                                top: finalTop,
                                transform: 'translate(-50%, -50%)',
                                width: '4vw', /* Viewport-based width */
                                height: '4vw', /* Viewport-based height */
                                minWidth: '10px', /* Minimum size */
                                minHeight: '10px', /* Minimum size */
                                maxWidth: '60px', /* Maximum size */
                                maxHeight: '60px', /* Maximum size */
                                backgroundImage: `url(${character.character_head_url})`,
                                backgroundSize: 'contain',
                                backgroundPosition: 'center',
                                backgroundRepeat: 'no-repeat',
                                zIndex: 10,
                                pointerEvents: 'none' // Make character markers non-clickable
                              }}
                            />
                          );
                        });
                      });
                    })()}
                  </>
                )}
              </div>
              {/* Followers in left bottom corner - moved here to be above the map */}
              {gameState && Array.isArray(gameState.followers_head_urls) && gameState.followers_head_urls.length > 0 && (
                <div className="followers-corner">
                  <span className="followers-label">{currentLang === 'ru' ? 'Последователи:' : 'Followers:'}</span>
                  <div className="followers-heads">
                    {[...gameState.followers_head_urls].sort().map((url, idx) => (
                      <img key={idx} src={url} alt={`Follower ${idx + 1}`} className="follower-head" />
                    ))}
                  </div>
                </div>
              )}
            </div>
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
                ) : (
                  <button 
                    className="save-button" 
                    onClick={handleCreateSave} 
                    disabled={savingGame}
                  >
                    {savingGame ? (currentLang === 'ru' ? 'Сохранение...' : 'Saving...') : 
                                 (currentLang === 'ru' ? 'Сохранить' : 'Save')}
                  </button>
                )}
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
    </div>
  );
};

export default GamePage;
