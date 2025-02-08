import React, { useState } from 'react';
import LiveDataGraph from './LiveDataGraph';
import Grid from '@mui/material/Grid';
import AddIcon from '@mui/icons-material/Add';
import TextField from '@mui/material/TextField';
import { IconButton, Paper, Button, Box, Dialog, DialogTitle, DialogContent, DialogActions } from '@mui/material';
import FullscreenIcon from '@mui/icons-material/Fullscreen';
import FullscreenExitIcon from '@mui/icons-material/FullscreenExit';

interface CellState {
  text: string;
  showGraph: boolean;
}

const ArbitrageDashboard: React.FC = () => {
  const [cells, setCells] = useState<CellState[]>(
    Array.from({ length: 4 }, () => ({  text: '', showGraph: false }))
  );
  const [dialogOpen, setDialogOpen] = useState<boolean>(false);
  const [selectedIndex, setSelectedIndex] = useState<number | null>(null);
  const [inputValue, setInputValue] = useState<string>('');
  const [error, setError] = useState<string>('');
  const [fullScreenOpen, setFullScreenOpen] = useState<boolean>(false);
  const [fullScreenCurrency, setFullScreenCurrency] = useState<string>('');

  const handleOpenDialog = (index: number) => {
    setSelectedIndex(index);
    setInputValue(''); // Clear any previous input
    setDialogOpen(true);
  };

  const handleCloseDialog = () => {
    setDialogOpen(false);
    setSelectedIndex(null);
  };

  const handleSubmitDialog = () => {
    if (!/^[A-Za-z]{3,5}$/.test(inputValue)) {
      setError('Text must be 3 to 5 alphabetic characters.');
      return;
    }
    if (selectedIndex === null) return;
    setCells((prev) =>
      prev.map((cell, i) =>
        i === selectedIndex ? { text: inputValue, showGraph: true, } : cell
      )
    );
    setDialogOpen(false);
    setSelectedIndex(null);
  };

  const handleRunFullScript = () => {
    // Placeholder for full script execution logic
    runQAOA();
    alert("Run full script functionality coming soon!");
  };

  // Run QAOA on live data (stubbed API call)
  const runQAOA = async () => {
    try {
      
    } catch (error) {
      console.error("Error running QAOA:", error);
    }
  };

  const handleOpenFullScreen = (currency: string) => {
    setFullScreenCurrency(currency);
    setFullScreenOpen(true);
  };

  const handleCloseFullScreen = () => {
    setFullScreenOpen(false);
    setFullScreenCurrency('');
  };

  return (
    <div className="dashboard-container">
      <h2>Arbitrage Opportunities Dashboard</h2>
      <Grid container spacing={2}>
        {cells.map((cell, index) => (
          <Grid item xs={6} key={index}>
            <Paper
              style={{
                padding: 16,
                position: 'relative',
                minHeight: 200,
                textAlign: 'center',
              }}
            >
              {/* "+" icon to trigger the popup dialog */}
              <IconButton
                onClick={() => handleOpenDialog(index)}
                style={{ position: 'absolute', top: 8, left: 8 }}
              >
                <AddIcon />
              </IconButton>
              {cell.showGraph ? (
                <div>
                  <p>{cell.text}</p>
                  {/* Pass an indicator if needed */}
                  <LiveDataGraph currency = {cell.text}/>

                  <IconButton
                    onClick={() => handleOpenFullScreen(cell.text)}
                    style={{ position: 'absolute', top: 8, right: 8 }}
                  >
                    <FullscreenIcon />
                  </IconButton>
                </div>
              ) : (
                <p>Click + to add graph</p>
              )}
            </Paper>
          </Grid>
        ))}
      </Grid>

      {/* Popup Dialog for text entry */}
      <Dialog open={dialogOpen} onClose={handleCloseDialog}>
        <DialogTitle>Please Enter Currency</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Currency"
            type="text"
            fullWidth
            variant="standard"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            error={Boolean(error)}
            helperText={error}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button onClick={handleSubmitDialog}>Submit</Button>
        </DialogActions>
      </Dialog>

      <Dialog open={fullScreenOpen} onClose={handleCloseFullScreen} fullScreen>
        <DialogTitle>
          Full Screen Graph - {fullScreenCurrency}
          <IconButton
            onClick={handleCloseFullScreen}
            style={{ position: 'absolute', right: 16, top: 16 }}
          >
            <FullscreenExitIcon />
          </IconButton>
        </DialogTitle>
        <DialogContent>
        <LiveDataGraph currency={fullScreenCurrency} />
        </DialogContent>
      </Dialog>

      <Box mt={2}>
        <Button 
          variant="contained" 
          color="primary" 
          onClick={handleRunFullScript}
        >
          Run full script
        </Button>
      </Box>
    </div>
  );
};

export default ArbitrageDashboard;
