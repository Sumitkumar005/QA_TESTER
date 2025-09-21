import React from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  Box,
} from '@mui/material';
import { Link, useLocation } from 'react-router-dom';
import CodeIcon from '@mui/icons-material/Code';

const Navbar = () => {
  const location = useLocation();

  const isActive = (path) => location.pathname === path;

  return (
    <AppBar position="static" sx={{ mb: 4 }}>
      <Toolbar>
        <CodeIcon sx={{ mr: 2 }} />
        <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
          Code Quality Intelligence Agent
        </Typography>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button
            color="inherit"
            component={Link}
            to="/"
            sx={{
              backgroundColor: isActive('/') ? 'rgba(255, 255, 255, 0.1)' : 'transparent',
            }}
          >
            Home
          </Button>
          <Button
            color="inherit"
            component={Link}
            to="/analyze"
            sx={{
              backgroundColor: isActive('/analyze') ? 'rgba(255, 255, 255, 0.1)' : 'transparent',
            }}
          >
            Analyze
          </Button>
          <Button
            color="inherit"
            component={Link}
            to="/qa"
            sx={{
              backgroundColor: isActive('/qa') ? 'rgba(255, 255, 255, 0.1)' : 'transparent',
            }}
          >
            Q&A
          </Button>
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default Navbar;