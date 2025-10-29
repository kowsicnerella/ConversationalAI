import { useState } from 'react';
import {
  Box,
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemText,
  IconButton,
  Typography,
  TextField,
  Button,
  Divider,
  Chip,
  CircularProgress,
  Menu,
  MenuItem,
} from '@mui/material';
import {
  Add,
  Delete,
  Edit,
  Search,
  Download,
  ArrowBack,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { useChat } from '../../context/ChatContext';

// eslint-disable-next-line react/prop-types
const ChatHistorySidebar = ({ open, onClose, onSelectConversation }) => {
  const {
    conversations,
    currentConversation,
    loadConversations,
    createConversation,
    deleteConversation,
    updateConversationTitle,
    exportConversation,
    searchConversations,
  } = useChat();

  const [searchQuery, setSearchQuery] = useState('');
  const [editingId, setEditingId] = useState(null);
  const [editingTitle, setEditingTitle] = useState('');
  const [anchorEl, setAnchorEl] = useState(null);
  const [selectedConvId, setSelectedConvId] = useState(null);
  const [isSearching, setIsSearching] = useState(false);

  const filteredConversations = conversations.filter((conv) =>
    conv.title.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleSearch = async (query) => {
    setSearchQuery(query);
    if (query.trim()) {
      setIsSearching(true);
      await searchConversations(query);
      setIsSearching(false);
    } else {
      await loadConversations();
    }
  };

  const handleNewConversation = async () => {
    const title = `Chat - ${new Date().toLocaleTimeString()}`;
    await createConversation(title, 'General');
    onClose();
  };

  const handleContextMenu = (event, convId) => {
    event.preventDefault();
    event.stopPropagation();
    setAnchorEl(event.currentTarget);
    setSelectedConvId(convId);
  };

  const handleCloseMenu = () => {
    setAnchorEl(null);
    setSelectedConvId(null);
  };

  const handleDelete = async () => {
    if (selectedConvId) {
      await deleteConversation(selectedConvId);
      handleCloseMenu();
    }
  };

  const handleRename = async () => {
    if (selectedConvId && editingTitle) {
      await updateConversationTitle(selectedConvId, editingTitle);
      setEditingId(null);
      setEditingTitle('');
      handleCloseMenu();
    }
  };

  const handleExport = async (format = 'json') => {
    if (selectedConvId) {
      await exportConversation(selectedConvId, format);
      handleCloseMenu();
    }
  };

  const handleSelectConversation = (conversation) => {
    onSelectConversation(conversation);
    onClose();
  };

  const drawerContent = (
    <Box
      sx={{
        width: 320,
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        bgcolor: '#0a0e27',
        color: '#fff',
      }}
    >
      {/* Header */}
      <Box sx={{ p: 2, borderBottom: '1px solid #1e2749' }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
            Chat History
          </Typography>
          <IconButton size="small" onClick={onClose} sx={{ color: '#fff' }}>
            <ArrowBack />
          </IconButton>
        </Box>

        {/* New Conversation Button */}
        <Button
          fullWidth
          startIcon={<Add />}
          onClick={handleNewConversation}
          sx={{
            bgcolor: '#6366f1',
            color: '#fff',
            textTransform: 'none',
            fontWeight: 'bold',
            '&:hover': { bgcolor: '#4f46e5' },
          }}
        >
          New Chat
        </Button>
      </Box>

      {/* Search Box */}
      <Box sx={{ p: 2, borderBottom: '1px solid #1e2749' }}>
        <TextField
          fullWidth
          placeholder="Search conversations..."
          size="small"
          value={searchQuery}
          onChange={(e) => handleSearch(e.target.value)}
          InputProps={{
            startAdornment: <Search sx={{ mr: 1, color: '#888' }} />,
          }}
          sx={{
            '& .MuiOutlinedInput-root': {
              bgcolor: '#1e2749',
              color: '#fff',
              '& fieldset': { borderColor: '#2e3749' },
              '&:hover fieldset': { borderColor: '#3e4759' },
            },
          }}
        />
      </Box>

      {/* Conversations List */}
      <List
        sx={{
          flex: 1,
          overflow: 'auto',
          '&::-webkit-scrollbar': { width: '6px' },
          '&::-webkit-scrollbar-track': { bgcolor: '#1e2749' },
          '&::-webkit-scrollbar-thumb': { bgcolor: '#4f46e5', borderRadius: '3px' },
        }}
      >
        {isSearching ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
            <CircularProgress size={24} />
          </Box>
        ) : filteredConversations.length === 0 ? (
          <Box sx={{ p: 2, textAlign: 'center', color: '#888' }}>
            <Typography variant="body2">No conversations yet</Typography>
          </Box>
        ) : (
          filteredConversations.map((conv) => (
            <motion.div
              key={conv.id}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
            >
              <ListItem
                disablePadding
                onContextMenu={(e) => handleContextMenu(e, conv.id)}
                sx={{
                  borderBottom: '1px solid #1e2749',
                  '&:hover': { bgcolor: '#1e2749' },
                  bgcolor:
                    currentConversation?.id === conv.id ? '#4f46e5' : 'transparent',
                }}
              >
                {editingId === conv.id ? (
                  <Box sx={{ width: '100%', p: 1 }}>
                    <TextField
                      fullWidth
                      size="small"
                      value={editingTitle}
                      onChange={(e) => setEditingTitle(e.target.value)}
                      onBlur={() => {
                        if (editingTitle) handleRename();
                        else setEditingId(null);
                      }}
                      onKeyDown={(e) => {
                        if (e.key === 'Enter') handleRename();
                        if (e.key === 'Escape') setEditingId(null);
                      }}
                      autoFocus
                      sx={{
                        '& .MuiOutlinedInput-root': {
                          bgcolor: '#0a0e27',
                          color: '#fff',
                        },
                      }}
                    />
                  </Box>
                ) : (
                  <ListItemButton
                    onClick={() => handleSelectConversation(conv)}
                    sx={{ width: '100%' }}
                  >
                    <ListItemText
                      primary={conv.title}
                      secondary={conv.topic}
                      sx={{
                        '& .MuiListItemText-primary': {
                          fontSize: '0.95rem',
                          fontWeight: '500',
                        },
                        '& .MuiListItemText-secondary': {
                          fontSize: '0.75rem',
                          color: '#888',
                        },
                      }}
                    />
                    <Chip
                      label={conv.message_count || 0}
                      size="small"
                      sx={{
                        height: '20px',
                        bgcolor: '#1e2749',
                        color: '#888',
                        fontSize: '0.75rem',
                      }}
                    />
                  </ListItemButton>
                )}
              </ListItem>
            </motion.div>
          ))
        )}
      </List>

      {/* Context Menu */}
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleCloseMenu}
        sx={{
          '& .MuiPaper-root': {
            bgcolor: '#1e2749',
            color: '#fff',
          },
        }}
      >
        <MenuItem
          onClick={() => {
            setEditingId(selectedConvId);
            setEditingTitle(
              conversations.find((c) => c.id === selectedConvId)?.title || ''
            );
            handleCloseMenu();
          }}
        >
          <Edit sx={{ mr: 1 }} /> Rename
        </MenuItem>
        <MenuItem onClick={() => handleExport('json')}>
          <Download sx={{ mr: 1 }} /> Export as JSON
        </MenuItem>
        <MenuItem onClick={() => handleExport('pdf')}>
          <Download sx={{ mr: 1 }} /> Export as PDF
        </MenuItem>
        <Divider sx={{ bgcolor: '#2e3749' }} />
        <MenuItem onClick={handleDelete} sx={{ color: '#ff6b6b' }}>
          <Delete sx={{ mr: 1 }} /> Delete
        </MenuItem>
      </Menu>
    </Box>
  );

  return (
    <Drawer
      anchor="left"
      open={open}
      onClose={onClose}
      sx={{
        '& .MuiDrawer-paper': {
          boxShadow: '0 0 20px rgba(99, 102, 241, 0.2)',
        },
      }}
    >
      {drawerContent}
    </Drawer>
  );
};

export default ChatHistorySidebar;
