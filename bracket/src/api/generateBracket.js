/**
 * API functions for bracket generation
 */

const API_URL = 'http://localhost:3002/api';

/**
 * Generate a bracket with markers for selected teams
 * @param {Array} selectedTeamIds - Array of team IDs to mark in the bracket
 * @returns {Promise<Object>} - Object containing success status, bracket URL, champion info, and message
 */
export const generateBracket = async (selectedTeamIds) => {
  try {
    // Convert selectedTeamIds to array of team objects
    const selectedTeams = selectedTeamIds.map(id => ({ id }));
    
    // Call the API to generate the bracket
    const response = await fetch(`${API_URL}/generate-bracket`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ selectedTeams }),
    });
    
    const data = await response.json();
    
    if (!response.ok) {
      console.error('API error:', data.error);
      return {
        success: false,
        error: data.error || 'Failed to generate bracket',
      };
    }
    
    if (data.success) {
      // Return the full URL to the bracket HTML with a cache-busting parameter
      return {
        success: true,
        bracketUrl: `http://localhost:3002${data.bracketUrl}?t=${Date.now()}`,
        champion: data.champion,
        message: data.message,
      };
    } else {
      return {
        success: false,
        error: data.error || 'Unknown error generating bracket',
      };
    }
  } catch (error) {
    console.error('Error generating bracket:', error);
    return {
      success: false,
      error: error.message || 'Failed to connect to bracket generation service',
    };
  }
}; 