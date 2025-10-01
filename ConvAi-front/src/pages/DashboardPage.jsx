import {
  Box,
  Typography,
  Container,
  Grid,
  Card,
  CardContent,
  LinearProgress,
  Chip,
  useTheme,
} from "@mui/material";
import { TrendingUp, School, Timer, EmojiEvents } from "@mui/icons-material";
import { motion } from "framer-motion";

const DashboardPage = () => {
  const theme = useTheme();

  const quickStats = [
    {
      title: "Current Level",
      value: "Intermediate",
      icon: <School />,
      color: theme.palette.primary.main,
      progress: 65,
    },
    {
      title: "Weekly Goal",
      value: "4/7 days",
      icon: <Timer />,
      color: theme.palette.success.main,
      progress: 57,
    },
    {
      title: "Points Earned",
      value: "1,250",
      icon: <EmojiEvents />,
      color: theme.palette.warning.main,
      progress: 80,
    },
    {
      title: "Improvement",
      value: "+15%",
      icon: <TrendingUp />,
      color: theme.palette.info.main,
      progress: 75,
    },
  ];

  return (
    <Container maxWidth="lg" sx={{ py: { xs: 2, sm: 3 } }}>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        <Typography
          variant="h5"
          sx={{
            mb: { xs: 2, sm: 2.5 },
            fontWeight: 600,
            background: "linear-gradient(45deg, #4f46e5, #06b6d4)",
            backgroundClip: "text",
            WebkitBackgroundClip: "text",
            WebkitTextFillColor: "transparent",
          }}
        >
          Learning Dashboard
        </Typography>

        <Grid
          container
          spacing={{ xs: 2, sm: 3 }}
          className="card-grid-container"
        >
          {quickStats.map((stat, index) => (
            <Grid
              item
              xs={12}
              sm={6}
              md={3}
              key={index}
              className="card-grid-item"
            >
              <motion.div
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
              >
                <Card
                  className="card-flex-layout"
                  sx={{
                    background: `linear-gradient(135deg, ${stat.color}15, ${stat.color}05)`,
                    border: `1px solid ${stat.color}30`,
                    borderRadius: 2,
                  }}
                >
                  <CardContent
                    className="card-content-flex"
                    sx={{
                      p: { xs: 1.5, sm: 2 },
                      "&:last-child": { pb: { xs: 1.5, sm: 2 } },
                    }}
                  >
                    <Box sx={{ display: "flex", alignItems: "center", mb: 1 }}>
                      <Box
                        sx={{
                          p: 0.75,
                          borderRadius: 1,
                          background: `${stat.color}20`,
                          color: stat.color,
                          mr: 1.25,
                          display: "flex",
                          alignItems: "center",
                          justifyContent: "center",
                          "& svg": { fontSize: "1.25rem" },
                        }}
                      >
                        {stat.icon}
                      </Box>
                      <Typography
                        variant="body1"
                        sx={{ fontWeight: 600, fontSize: "1rem" }}
                      >
                        {stat.value}
                      </Typography>
                    </Box>
                    <Typography
                      variant="body2"
                      color="text.secondary"
                      sx={{ mb: 1.5, fontSize: "0.813rem" }}
                    >
                      {stat.title}
                    </Typography>
                    <LinearProgress
                      variant="determinate"
                      value={stat.progress}
                      sx={{
                        height: 6,
                        borderRadius: 3,
                        backgroundColor: `${stat.color}20`,
                        "& .MuiLinearProgress-bar": {
                          backgroundColor: stat.color,
                          borderRadius: 3,
                        },
                      }}
                    />
                    <Box
                      sx={{
                        display: "flex",
                        justifyContent: "space-between",
                        mt: 0.75,
                      }}
                    >
                      <Typography
                        variant="caption"
                        color="text.secondary"
                        sx={{ fontSize: "0.688rem" }}
                      >
                        Progress
                      </Typography>
                      <Typography
                        variant="caption"
                        sx={{ fontWeight: 600, fontSize: "0.688rem" }}
                      >
                        {stat.progress}%
                      </Typography>
                    </Box>
                  </CardContent>
                </Card>
              </motion.div>
            </Grid>
          ))}
        </Grid>

        <Box sx={{ mt: { xs: 2.5, sm: 3 } }}>
          <Typography
            variant="h6"
            sx={{ mb: 1.5, fontWeight: 600, fontSize: "1.125rem" }}
          >
            Recent Activity
          </Typography>
          <Card sx={{ borderRadius: 2 }}>
            <CardContent sx={{ p: { xs: 2, sm: 2.5 } }}>
              <Box sx={{ textAlign: "center", py: 3 }}>
                <Typography variant="body1" color="text.secondary">
                  Activity timeline will appear here
                </Typography>
                <Chip
                  label="Feature in development"
                  color="primary"
                  variant="outlined"
                  sx={{ mt: 2 }}
                />
              </Box>
            </CardContent>
          </Card>
        </Box>
      </motion.div>
    </Container>
  );
};

export default DashboardPage;
