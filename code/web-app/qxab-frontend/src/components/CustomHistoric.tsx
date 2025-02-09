import React, { useState } from 'react';
import CombinedDataGraph from './CombinedDataGraph';
import Grid from '@mui/material/Grid';
import TextField from '@mui/material/TextField';
import { IconButton, Paper, Box, Dialog, DialogTitle, DialogContent, Button } from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import FullscreenIcon from '@mui/icons-material/Fullscreen';
import FullscreenExitIcon from '@mui/icons-material/FullscreenExit';
import { Link } from "react-router-dom";

interface CellState {
  text1: string;
  text2: string;
  showGraph: boolean;
}

const CustomHistoric: React.FC = () => {
  const [cells, setCells] = useState<CellState[]>(
    Array.from({ length: 4 }, () => ({ text1: '', text2: '', showGraph: false }))
  );
  const [fullScreenOpen, setFullScreenOpen] = useState<boolean>(false);
  const [fullScreenCurrencies, setFullScreenCurrencies] = useState<{ text1: string; text2: string } | null>(null);

  const handleInputChange = (index: number, field: 'text1' | 'text2', value: string) => {
    setCells((prev) =>
      prev.map((cell, i) => (i === index ? { ...cell, [field]: value } : cell))
    );
  };

  const handleSubmit = (index: number) => {
    if (!/^[A-Za-z]{3,5}$/.test(cells[index].text1) || !/^[A-Za-z]{3,5}$/.test(cells[index].text2)) {
      alert('Text must be 3 to 5 alphabetic characters.');
      return;
    }
    setCells((prev) =>
      prev.map((cell, i) => (i === index ? { ...cell, showGraph: true } : cell))
    );
  };

  const handleOpenFullScreen = (text1: string, text2: string) => {
    setFullScreenCurrencies({ text1, text2 });
    setFullScreenOpen(true);
  };

  const handleCloseFullScreen = () => {
    setFullScreenOpen(false);
    setFullScreenCurrencies(null);
  };

  return (
    <div className="dashboard-container">
      <h2>Arbitrage Opportunities Dashboard</h2>
      <Link to="/arbitrage">Go to Home Page</Link>
      <Grid container spacing={2}>
        {cells.map((cell, index) => (
          <Grid item xs={6} key={index}>
            <Paper style={{ padding: 16, position: 'relative', minHeight: 250, textAlign: 'center' }}>
              <Box display="flex" justifyContent="center" gap={1} mb={2}>
                <TextField
                  label="Currency 1"
                  variant="outlined"
                  size="small"
                  value={cell.text1}
                  onChange={(e) => handleInputChange(index, 'text1', e.target.value)}
                />
                <TextField
                  label="Currency 2"
                  variant="outlined"
                  size="small"
                  value={cell.text2}
                  onChange={(e) => handleInputChange(index, 'text2', e.target.value)}
                />
                <IconButton onClick={() => handleSubmit(index)}>
                  <AddIcon />
                </IconButton>
              </Box>
              {cell.showGraph ? (
                <div>
                  <p>{cell.text1} / {cell.text2}</p>
                  <CombinedDataGraph currency1={cell.text1} currency2={cell.text2} isHistorical={true} />
                  <IconButton
                    onClick={() => handleOpenFullScreen(cell.text1, cell.text2)}
                    style={{ position: 'absolute', top: 8, right: 8 }}
                  >
                    <FullscreenIcon />
                  </IconButton>
                </div>
              ) : (
                <p>Enter two currencies and click + to add graphs</p>
              )}
            </Paper>
          </Grid>
        ))}
      </Grid>

      {fullScreenOpen && fullScreenCurrencies && (
        <div className="fullscreen-modal">
          <h2>Full Screen Graph - {fullScreenCurrencies.text1} / {fullScreenCurrencies.text2}</h2>
          <CombinedDataGraph currency1={fullScreenCurrencies.text1} currency2={fullScreenCurrencies.text2} isHistorical={true} />
          <Button onClick={handleCloseFullScreen}>
            <FullscreenExitIcon /> Close Full Screen
          </Button>
        </div>
      )}
    </div>
  );
};

export default CustomHistoric;