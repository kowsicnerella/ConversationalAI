import { Outlet } from "react-router-dom";
import { Box } from "@mui/material";

const AuthLayout = () => {
  return (
    <Box
      sx={{
        minHeight: "100vh",
        width: "100%",
        display: "flex",
      }}
    >
      <Outlet />
    </Box>
  );
};

export default AuthLayout;
