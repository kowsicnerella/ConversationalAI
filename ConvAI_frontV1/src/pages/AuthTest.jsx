import { useState } from "react";
import { Box, Button, Typography, Alert, Paper, Divider } from "@mui/material";
import axiosInstance from "../config/api";

/**
 * JWT Authentication Test Component
 * Use this to debug authentication issues
 */
const AuthTest = () => {
  const [results, setResults] = useState({});
  const [loading, setLoading] = useState(false);

  const checkToken = () => {
    const token = localStorage.getItem("access_token");
    const user = localStorage.getItem("user");

    setResults({
      tokenExists: !!token,
      tokenLength: token?.length,
      tokenPreview: token?.substring(0, 50) + "...",
      userExists: !!user,
      userData: user ? JSON.parse(user) : null,
    });
  };

  const testNoAuth = async () => {
    setLoading(true);
    try {
      const response = await fetch("http://localhost:5000/api/test-no-auth");
      const data = await response.json();
      setResults({ ...results, noAuthTest: { success: true, data } });
    } catch (error) {
      setResults({
        ...results,
        noAuthTest: { success: false, error: error.message },
      });
    } finally {
      setLoading(false);
    }
  };

  const testWithAuth = async () => {
    setLoading(true);
    try {
      const response = await axiosInstance.get("/test-auth");
      setResults({
        ...results,
        authTest: { success: true, data: response.data },
      });
    } catch (error) {
      setResults({
        ...results,
        authTest: {
          success: false,
          error: error.message,
          status: error.response?.status,
          data: error.response?.data,
        },
      });
    } finally {
      setLoading(false);
    }
  };

  const testLearningPaths = async () => {
    setLoading(true);
    try {
      const response = await axiosInstance.get("/courses/learning-paths");
      setResults({
        ...results,
        learningPathsTest: { success: true, data: response.data },
      });
    } catch (error) {
      setResults({
        ...results,
        learningPathsTest: {
          success: false,
          error: error.message,
          status: error.response?.status,
          data: error.response?.data,
        },
      });
    } finally {
      setLoading(false);
    }
  };

  const decodeToken = () => {
    const token = localStorage.getItem("access_token");
    if (!token) {
      setResults({ ...results, decoded: { error: "No token found" } });
      return;
    }

    try {
      const parts = token.split(".");
      if (parts.length !== 3) {
        setResults({
          ...results,
          decoded: { error: "Invalid JWT format - should have 3 parts" },
        });
        return;
      }

      const header = JSON.parse(atob(parts[0]));
      const payload = JSON.parse(atob(parts[1]));

      setResults({
        ...results,
        decoded: {
          header,
          payload,
          expiresAt: new Date(payload.exp * 1000).toLocaleString(),
          isExpired: payload.exp * 1000 < Date.now(),
        },
      });
    } catch (error) {
      setResults({ ...results, decoded: { error: error.message } });
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        🔐 JWT Authentication Tester
      </Typography>
      <Typography variant="body2" color="text.secondary" gutterBottom>
        Use this tool to debug authentication issues
      </Typography>

      <Divider sx={{ my: 3 }} />

      <Box sx={{ display: "flex", gap: 2, flexWrap: "wrap", mb: 3 }}>
        <Button variant="contained" onClick={checkToken}>
          1. Check Token
        </Button>
        <Button variant="contained" onClick={decodeToken}>
          2. Decode Token
        </Button>
        <Button variant="contained" onClick={testNoAuth} disabled={loading}>
          3. Test No Auth Endpoint
        </Button>
        <Button variant="contained" onClick={testWithAuth} disabled={loading}>
          4. Test With Auth Endpoint
        </Button>
        <Button
          variant="contained"
          onClick={testLearningPaths}
          disabled={loading}
        >
          5. Test Learning Paths
        </Button>
      </Box>

      {Object.keys(results).length > 0 && (
        <Paper
          sx={{
            p: 2,
            bgcolor: "#1e1e1e",
            color: "#fff",
            fontFamily: "monospace",
          }}
        >
          <Typography variant="h6" gutterBottom>
            Results:
          </Typography>
          <pre style={{ overflow: "auto", whiteSpace: "pre-wrap" }}>
            {JSON.stringify(results, null, 2)}
          </pre>
        </Paper>
      )}

      <Alert severity="info" sx={{ mt: 3 }}>
        <strong>How to use:</strong>
        <ol>
          <li>Click "Check Token" to see if you have a token</li>
          <li>Click "Decode Token" to inspect the token contents</li>
          <li>Click "Test No Auth Endpoint" - should always work</li>
          <li>
            Click "Test With Auth Endpoint" - should work if token is valid
          </li>
          <li>
            Click "Test Learning Paths" - should work if authentication is
            working
          </li>
        </ol>
        <strong>Also check the browser console for detailed logs!</strong>
      </Alert>
    </Box>
  );
};

export default AuthTest;
