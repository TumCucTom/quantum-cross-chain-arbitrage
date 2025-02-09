import React from "react";
import { AppBar, Toolbar, Typography, Button } from "@mui/material";
import { Link } from "react-router-dom";

const NavBar: React.FC = () => {
  return (
    <AppBar position="fixed"  // Keeps the navbar at the top even when scrolling
    sx={{ backgroundColor: "#9E9E9E", width: "100%", top: 0 }}>
      <Toolbar>
        <Typography variant="h6" sx={{ flexGrow: 1 }}>
          Quantum Enhanced Cross-Chain Arbitrage
        </Typography>

        {/* Navigation Links */}
        <Button color="inherit" component={Link} to="/">Home</Button>
        <Button color="inherit" component={Link} to="/custom-historic">Custom Historic</Button>
        <Button color="inherit" component={Link} to="/arbitrage">Arbitrage</Button>
      </Toolbar>
    </AppBar>
  );
};

export default NavBar;
