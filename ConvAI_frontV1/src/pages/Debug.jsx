import { Box, Typography, Paper, Button } from "@mui/material";
import { useAuth } from "../context/AuthContext";
import { useNavigate, useLocation } from "react-router-dom";
import { useState, useEffect } from "react";

const Debug = () => {
  const { isAuthenticated, user, loading, userStatus } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [renderCount, setRenderCount] = useState(0);

  useEffect(() => {
    setRenderCount((prev) => prev + 1);
  });

  const clearAuth = () => {
    localStorage.clear();
    sessionStorage.clear();
    window.location.href = "/";
  };

  return (
    <Box
      sx={{
        minHeight: "100vh",
        background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
        p: 4,
      }}
    >
      <Paper sx={{ p: 3, maxWidth: 800, mx: "auto" }}>
        <Typography variant="h4" gutterBottom>
          🔍 Debug Page
        </Typography>

        <Typography variant="h6" sx={{ mt: 3 }}>
          Render Info:
        </Typography>
        <Typography>Render Count: {renderCount}</Typography>

        <Typography variant="h6" sx={{ mt: 3 }}>
          Auth State:
        </Typography>
        <Typography>Loading: {loading ? "true" : "false"}</Typography>
        <Typography>
          Is Authenticated: {isAuthenticated ? "true" : "false"}
        </Typography>
        <Typography>User: {JSON.stringify(user, null, 2)}</Typography>
        <Typography>
          User Status: {JSON.stringify(userStatus, null, 2)}
        </Typography>

        <Typography variant="h6" sx={{ mt: 3 }}>
          Location:
        </Typography>
        <Typography>Pathname: {location.pathname}</Typography>
        <Typography>Search: {location.search}</Typography>
        <Typography>Hash: {location.hash}</Typography>

        <Typography variant="h6" sx={{ mt: 3 }}>
          LocalStorage:
        </Typography>
        <Typography>
          access_token:{" "}
          {localStorage.getItem("access_token")
            ? "exists"
            : "null"}
        </Typography>
        <Typography>
          user: {localStorage.getItem("user") ? "exists" : "null"}
        </Typography>

        <Box sx={{ mt: 3, display: "flex", gap: 2 }}>
          <Button variant="contained" onClick={() => navigate("/")}>
            Go to Home
          </Button>
          <Button variant="contained" onClick={() => navigate("/login")}>
            Go to Login
          </Button>
          <Button
            variant="contained"
            onClick={() => navigate("/dashboard")}
          >
            Go to Dashboard
          </Button>
          <Button variant="outlined" color="error" onClick={clearAuth}>
            Clear Auth & Reload
          </Button>
        </Box>
      </Paper>
    </Box>
  );
};

export default Debug;
