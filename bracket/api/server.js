const express = require('express');
const { exec } = require('child_process');
const path = require('path');
const cors = require('cors');
const fs = require('fs');

const app = express();
const PORT = process.env.PORT || 3002;

// Middleware
app.use(cors());
app.use(express.json());

// Serve static files from the parent directory (where tournament_bracket.html is located)
const parentDir = path.join(__dirname, '..', '..');
app.use(express.static(parentDir));

// Also serve static files from the current directory
app.use(express.static(__dirname));

// API endpoint to generate bracket
app.post('/api/generate-bracket', (req, res) => {
  const { selectedTeams } = req.body;
  
  if (!selectedTeams || !Array.isArray(selectedTeams)) {
    return res.status(400).json({ 
      success: false, 
      error: 'Selected teams must be provided as an array' 
    });
  }
  
  // Extract team IDs
  const teamIds = selectedTeams.map(team => team.id);
  
  // Call the Python script with selected team IDs
  const pythonScript = path.join(__dirname, 'generate_bracket.py');
  const command = `python3 ${pythonScript} ${teamIds.join(' ')}`;
  
  exec(command, (error, stdout, stderr) => {
    if (error) {
      console.error(`Error executing Python script: ${error.message}`);
      return res.status(500).json({ 
        success: false, 
        error: `Failed to generate bracket: ${error.message}` 
      });
    }
    
    if (stderr) {
      console.error(`Python script stderr: ${stderr}`);
    }
    
    try {
      // Parse the JSON output from the Python script
      const result = JSON.parse(stdout);
      
      if (result.success) {
        // Check if the tournament_bracket.html file exists in the parent directory
        const bracketFileParent = path.join(parentDir, 'tournament_bracket.html');
        
        // Also check if it exists in the current directory
        const bracketFileLocal = path.join(__dirname, 'tournament_bracket.html');
        
        // If the file exists in the parent directory, copy it to the API directory
        if (fs.existsSync(bracketFileParent)) {
          fs.copyFileSync(bracketFileParent, bracketFileLocal);
          console.log('Copied tournament_bracket.html from parent directory to API directory');
        } else if (!fs.existsSync(bracketFileLocal)) {
          return res.status(500).json({
            success: false,
            error: 'Generated bracket file not found'
          });
        }
        
        // Return the path to the generated HTML file in the API directory
        return res.json({
          success: true,
          bracketUrl: '/tournament_bracket.html',
          champion: result.champion,
          message: result.message
        });
      } else {
        return res.status(500).json({
          success: false,
          error: result.error || 'Failed to generate bracket'
        });
      }
    } catch (parseError) {
      console.error(`Error parsing Python script output: ${parseError.message}`);
      console.error(`Raw output: ${stdout}`);
      return res.status(500).json({ 
        success: false, 
        error: `Failed to parse bracket generation result: ${parseError.message}` 
      });
    }
  });
});

// Start the server
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
  console.log(`API available at http://localhost:${PORT}/api/generate-bracket`);
}); 