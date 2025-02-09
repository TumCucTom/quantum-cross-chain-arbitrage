import React, { useState } from 'react';
import LiveDataGraph from './LiveDataGraph';
import Grid from '@mui/material/Grid';
import Drawer from '@mui/material/Drawer';
import { IconButton, Paper, Button, Box, Dialog, DialogTitle, DialogContent, AppBar, Toolbar } from '@mui/material';
import FullscreenIcon from '@mui/icons-material/Fullscreen';
import FullscreenExitIcon from '@mui/icons-material/FullscreenExit';
import { Link } from "react-router-dom";


const buttonNames = [
    "AAVE", "ADA", "ALGO", "APT", "ARB", "ATOM", "AVAX", "BCH",
    "BNB", "BTC", "DOGE", "DOT", "ETC", "ETH", "FIL", "FLR",
    "FTM", "HBAR", "ICP", "LINK", "LTC", "NEAR", "QNT", "SHIB",
    "SOL", "UNI", "USDC", "USDT", "XLM", "XRP"
  ];

const drawerWidth = 300;

const HomeDashboard: React.FC = () => {
  // State to store the selected currencies (max 6)
  const [selectedCurrencies, setSelectedCurrencies] = useState<string[]>([]);
  const [fullScreenOpen, setFullScreenOpen] = useState<boolean>(false);
  const [fullScreenCurrency, setFullScreenCurrency] = useState<string>('');

  const handleOpenFullScreen = (currency: string) => {
    setFullScreenCurrency(currency);
    setFullScreenOpen(true);
  };

  const handleCloseFullScreen = () => {
    setFullScreenOpen(false);
    setFullScreenCurrency('');
  };

  const toggleCurrency = (currency: string) => {
    setSelectedCurrencies((prev) => {
      if (prev.includes(currency)) {
        return prev.filter((c) => c !== currency); // Remove if already selected
      } else if (prev.length < 6) {
        return [...prev, currency]; // Add if not already selected (max 6)
      }
      return prev; // Do nothing if max reached
    });
  };

  return (
    <div style={{ display: 'flex' }}>
      {/* Sidebar Drawer */}
      <Drawer
        variant="permanent"
        anchor="left"
        sx={{
          width: drawerWidth,
          flexShrink: 0,
          [`& .MuiDrawer-paper`]: { 
            width: drawerWidth, 
            boxSizing: 'border-box',
            padding: 0.6
          },
        }}
      >
        <Grid container spacing={1}>
          {buttonNames.map((name, index) => (
            <Grid item xs={6} key={index}>
              <Button
                variant={selectedCurrencies.includes(name) ? "contained" : "outlined"}
                color={selectedCurrencies.includes(name) ? "primary" : "secondary"}
                size="small"
                onClick={() => toggleCurrency(name)}
                fullWidth
              >
                {name}
              </Button>
            </Grid>
          ))}
        </Grid>
      </Drawer>

        {/* Main Content Area */}
        <Box 
        component="main"
        sx={{ 
          flexGrow: 1, 
          padding: '20px',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center'
        }}
        >
        <h1>Quantum-Enhanced Cross-Chain Arbitrage Bot</h1>
        <h2>Arbitrage Opportunities Dashboard</h2>
        <Link to="/custom-historic">Go to Home Page</Link>

        {/* Graphs - Only Display 6 Selected Graphs */}
        <Grid container spacing={2} sx={{ width: '100%', justifyContent: 'center' }}>
          {selectedCurrencies.map((currency, index) => (
            <Grid item xs={12} key={index}>
              <Paper sx={{ p: 2, textAlign: 'center', minHeight: 250, position: 'relative', minWidth: '300px' }}>
                {/* Fullscreen Button (Top Right) */}
                <IconButton
                  onClick={() => handleOpenFullScreen(currency)} 
                  sx={{ position: 'absolute', top: 8, right: 8 }}
                >
                  <FullscreenIcon />
                </IconButton>

                <p>{currency+"USDT"}</p>
                <LiveDataGraph currency={currency+"USDT"} isHistorical={false}/>
              </Paper>
            </Grid>
          ))}
        </Grid>
      </Box>

        {/* Full Screen Dialog */}
        <Dialog open={fullScreenOpen} onClose={handleCloseFullScreen} fullScreen>
        <DialogTitle>
          Full Screen Graph - {fullScreenCurrency+"USDT"}
          <IconButton 
            onClick={handleCloseFullScreen} 
            sx={{ position: 'absolute', right: 16, top: 16 }}
          >
            <FullscreenExitIcon />
          </IconButton>
        </DialogTitle>
        <DialogContent>
          <LiveDataGraph currency={fullScreenCurrency+"USDT"} isHistorical={false} />
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default HomeDashboard;