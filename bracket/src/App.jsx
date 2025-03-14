import { useState, useEffect } from 'react'
import { generateBracket } from './api/generateBracket'
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./components/ui/tabs"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "./components/ui/card"
import { Button } from "./components/ui/button"
import { Checkbox } from "./components/ui/checkbox"
import './App.css'

function App() {
  const [selectedTeams, setSelectedTeams] = useState([]);
  const [allTeams, setAllTeams] = useState([]);
  const [bracketGenerated, setBracketGenerated] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [bracketUrl, setBracketUrl] = useState('about:blank');
  const [champion, setChampion] = useState(null);

  // Generate list of teams when component mounts
  useEffect(() => {
    // Create a list of 64 teams (16 teams per region, 4 regions)
    const regions = ['East', 'West', 'South', 'Midwest'];
    const teams = [];
    let teamId = 1;

    regions.forEach(region => {
      for (let seed = 1; seed <= 16; seed++) {
        teams.push({
          id: teamId,
          name: `Team ${teamId}`,
          region,
          seed
        });
        teamId++;
      }
    });

    setAllTeams(teams);
  }, []);

  // Handle team selection (max 5 teams)
  const handleTeamSelect = (team) => {
    setError(null);
    
    // Check if team is already selected
    if (selectedTeams.some(t => t.id === team.id)) {
      // Remove team if already selected
      setSelectedTeams(selectedTeams.filter(t => t.id !== team.id));
    } else {
      // Add team if not already selected and less than 5 teams are selected
      if (selectedTeams.length < 5) {
        setSelectedTeams([...selectedTeams, team]);
      } else {
        setError('You can only select up to 5 teams');
      }
    }
  };

  // Handle bracket generation
  const handleGenerateBracket = async () => {
    if (selectedTeams.length === 0) {
      setError('Please select at least one team');
      return;
    }

    setLoading(true);
    setError(null);
    setBracketGenerated(false);
    
    try {
      // Get selected team IDs
      const selectedTeamIds = selectedTeams.map(team => team.id);
      
      // Call API to generate bracket
      const result = await generateBracket(selectedTeamIds);
      
      if (result.success) {
        setBracketUrl(result.bracketUrl);
        setChampion(result.champion);
        setBracketGenerated(true);
      } else {
        setError(result.error || 'Failed to generate bracket');
      }
    } catch (err) {
      console.error('Error generating bracket:', err);
      setError('An error occurred while generating the bracket');
    } finally {
      setLoading(false);
    }
  };

  // Get seed color class based on seed number
  const getSeedColorClass = (seed) => {
    const seedColors = {
      1: "bg-blue-600 text-white",
      2: "bg-green-600 text-white",
      3: "bg-red-600 text-white",
      4: "bg-purple-600 text-white",
      5: "bg-orange-500 text-white",
      6: "bg-teal-600 text-white",
      7: "bg-amber-600 text-white",
      8: "bg-sky-600 text-white",
      9: "bg-orange-600 text-white",
      10: "bg-amber-700 text-white",
      11: "bg-yellow-600 text-white",
      12: "bg-teal-500 text-white",
      13: "bg-pink-700 text-white",
      14: "bg-indigo-600 text-white",
      15: "bg-lime-700 text-white",
      16: "bg-gray-600 text-white"
    };
    
    return seedColors[seed] || "bg-gray-500 text-white";
  };

  return (
    <div className="min-h-screen bg-slate-50 py-8 px-4">
      <div className="container mx-auto">
        <h1 className="text-3xl font-bold text-center text-primary mb-8">NCAA Tournament Bracket Generator</h1>
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Select Your Teams (Max 5)</CardTitle>
                <CardDescription>Choose up to five teams to highlight in your bracket</CardDescription>
              </CardHeader>
              <CardContent>
                {error && (
                  <div className="bg-destructive/10 text-destructive text-sm p-3 rounded-md mb-4">
                    {error}
                  </div>
                )}
                
                <Tabs defaultValue="East">
                  <TabsList className="grid grid-cols-4 mb-4">
                    {['East', 'West', 'South', 'Midwest'].map(region => (
                      <TabsTrigger key={region} value={region}>{region}</TabsTrigger>
                    ))}
                  </TabsList>
                  
                  {['East', 'West', 'South', 'Midwest'].map(region => (
                    <TabsContent key={region} value={region} className="space-y-2">
                      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                        {allTeams
                          .filter(team => team.region === region)
                          .sort((a, b) => a.seed - b.seed)
                          .map(team => (
                            <div
                              key={team.id}
                              className={`flex items-center p-2 rounded-md border cursor-pointer transition-colors
                                ${selectedTeams.some(t => t.id === team.id) 
                                  ? 'border-primary bg-primary/5' 
                                  : 'border-border hover:bg-muted/50'}`}
                              onClick={() => handleTeamSelect(team)}
                            >
                              <div className={`w-6 h-6 flex items-center justify-center rounded-full mr-2 text-xs font-bold ${getSeedColorClass(team.seed)}`}>
                                {team.seed}
                              </div>
                              <span className="text-sm font-medium truncate">{team.name}</span>
                              {selectedTeams.some(t => t.id === team.id) && (
                                <Checkbox className="ml-auto" checked />
                              )}
                            </div>
                          ))}
                      </div>
                    </TabsContent>
                  ))}
                </Tabs>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader>
                <CardTitle>Your Selected Teams ({selectedTeams.length}/5)</CardTitle>
              </CardHeader>
              <CardContent>
                {selectedTeams.length > 0 ? (
                  <div className="space-y-2">
                    {selectedTeams.map(team => (
                      <div key={team.id} className="flex items-center justify-between p-3 bg-muted/50 rounded-md">
                        <div className="flex items-center">
                          <div className={`w-6 h-6 flex items-center justify-center rounded-full mr-2 text-xs font-bold ${getSeedColorClass(team.seed)}`}>
                            {team.seed}
                          </div>
                          <div>
                            <div className="font-medium">{team.name}</div>
                            <div className="text-xs text-muted-foreground">{team.region} Region</div>
                          </div>
                        </div>
                        <Button 
                          variant="ghost" 
                          size="sm" 
                          className="h-8 w-8 p-0 text-muted-foreground"
                          onClick={() => handleTeamSelect(team)}
                        >
                          ✕
                        </Button>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-6 text-muted-foreground">
                    No teams selected yet
                  </div>
                )}
              </CardContent>
              <CardFooter>
                <Button 
                  className="w-full"
                  onClick={handleGenerateBracket}
                  disabled={loading}
                >
                  {loading ? 'Generating...' : 'Generate Bracket'}
                </Button>
              </CardFooter>
            </Card>
          </div>
          
          <div>
            {bracketGenerated ? (
              <Card className="h-full">
                <CardHeader>
                  <CardTitle>Tournament Bracket</CardTitle>
                  {champion && (
                    <CardDescription>
                      Champion: <span className="font-semibold">{champion}</span>
                    </CardDescription>
                  )}
                </CardHeader>
                <CardContent className="p-0">
                  <div className="w-full h-[700px] overflow-hidden">
                    <iframe 
                      src={bracketUrl} 
                      title="Tournament Bracket"
                      className="w-full h-full border-0"
                      sandbox="allow-same-origin allow-scripts"
                      key={bracketUrl + Date.now()}
                    />
                  </div>
                </CardContent>
              </Card>
            ) : (
              <Card className="h-full flex items-center justify-center">
                <CardContent className="text-center py-12">
                  <div className="text-6xl mb-4">🏀</div>
                  <h3 className="text-xl font-semibold mb-2">Ready to Generate Your Bracket</h3>
                  <p className="text-muted-foreground max-w-md">
                    Select your teams from the left panel and click "Generate Bracket" to create your tournament visualization.
                  </p>
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default App
