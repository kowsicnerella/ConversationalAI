import { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  CardHeader,
  Typography,
  Link,
  Divider,
  Avatar,
  Accordion,
  AccordionSummary,
  AccordionDetails,
} from '@mui/material';
import { ExpandMore, OpenInNew, Language } from '@mui/icons-material';
import { motion } from 'framer-motion';

// eslint-disable-next-line react/prop-types
const WebSearchResults = ({ results, query }) => {
  const [expanded, setExpanded] = useState(0);

  if (!results || results.length === 0) {
    return null;
  }

  return (
    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
      <Card
        sx={{
          bgcolor: 'rgba(59, 130, 246, 0.1)',
          border: '1px solid rgba(59, 130, 246, 0.3)',
          borderRadius: 2,
          mb: 2,
        }}
      >
        <CardHeader
          avatar={
            <Avatar sx={{ bgcolor: '#3b82f6' }}>
              <Language />
            </Avatar>
          }
          title="Web Search Results"
          subtitle={query ? `for: "${query}"` : 'Recent searches'}
          titleTypographyProps={{ variant: 'subtitle1', fontWeight: 'bold' }}
        />
        <Divider />
        <CardContent>
          {results.map((result, idx) => (
            <Accordion
              key={idx}
              expanded={expanded === idx}
              onChange={() => setExpanded(expanded === idx ? -1 : idx)}
              sx={{
                bgcolor: 'rgba(59, 130, 246, 0.05)',
                mb: 1,
                '&:last-child': { mb: 0 },
              }}
            >
              <AccordionSummary expandIcon={<ExpandMore />}>
                <Box sx={{ flex: 1 }}>
                  <Typography
                    variant="subtitle2"
                    sx={{
                      color: '#3b82f6',
                      fontWeight: 'bold',
                      textDecoration: 'none',
                      '&:hover': { textDecoration: 'underline' },
                    }}
                  >
                    {result.title}
                  </Typography>
                  <Typography variant="caption" sx={{ color: '#888' }}>
                    {result.source}
                  </Typography>
                </Box>
              </AccordionSummary>
              <AccordionDetails sx={{ bgcolor: 'rgba(59, 130, 246, 0.02)' }}>
                <Typography variant="body2" sx={{ color: '#ccc', mb: 1.5 }}>
                  {result.body}
                </Typography>
                <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
                  {result.link && (
                    <Link
                      href={result.link}
                      target="_blank"
                      rel="noopener noreferrer"
                      sx={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: 0.5,
                        color: '#3b82f6',
                        fontSize: '0.85rem',
                        textDecoration: 'none',
                        '&:hover': { textDecoration: 'underline' },
                      }}
                    >
                      Read more
                      <OpenInNew sx={{ fontSize: '0.85rem' }} />
                    </Link>
                  )}
                </Box>
              </AccordionDetails>
            </Accordion>
          ))}
        </CardContent>
      </Card>
    </motion.div>
  );
};

export default WebSearchResults;
