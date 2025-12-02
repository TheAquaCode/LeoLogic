import {
  FolderOpen,
  Upload,
  MessageSquare,
  Clock,
  Settings,
  Folder,
  Monitor,
  Image,
  Video,
  LayoutDashboard
} from 'lucide-react';

export const sidebarItems = [
  { name: 'Dashboard', icon: LayoutDashboard },
  { name: 'File Explorer', icon: FolderOpen },
  { name: 'Upload & Scan', icon: Upload },
  { name: 'History', icon: Clock },
  { name: 'Settings', icon: Settings }
];

export const watchedFolders = [
  {
    name: 'Downloads',
    path: '/Users/username/Downloads',
    files: 247,
    lastActivity: '2 minutes ago',
    status: 'Active',
    icon: Folder
  },
  {
    name: 'Desktop',
    path: '/Users/username/Desktop',
    files: 89,
    lastActivity: '5 minutes ago',
    status: 'Active',
    icon: Monitor
  },
  {
    name: 'Documents',
    path: '/Users/username/Documents',
    files: 1543,
    lastActivity: '1 hour ago',
    status: 'Paused',
    icon: Folder
  },
  {
    name: 'Pictures',
    path: '/Users/username/Pictures',
    files: 892,
    lastActivity: '10 minutes ago',
    status: 'Active',
    icon: Image
  },
  {
    name: 'Videos',
    path: '/Users/username/Videos',
    files: 156,
    lastActivity: '12 minutes ago',
    status: 'Active',
    icon: Video
  }
];

export const categories = [
  {
    name: 'Work Documents',
    path: '/Users/username/Organized/Work',
    fileTypes: ['pdf', 'docx', 'xlsx', '+1'],
    rules: 8,
    color: 'bg-blue-500'
  },
  {
    name: 'Personal Photos',
    path: '/Users/username/Organized/Photos/Personal',
    fileTypes: ['jpg', 'png', 'heic', '+1'],
    rules: 12,
    color: 'bg-pink-500'
  },
  {
    name: 'Video Content',
    path: '/Users/username/Organized/Video',
    fileTypes: [],
    rules: 0,
    ruleStatus: 'No rules defined',
    color: 'bg-purple-500'
  }
];

export const fileMovements = [
  {
    id: 1,
    filename: 'beach-sunset.jpg',
    confidence: '98%',
    timeAgo: '15 minutes ago',
    detection: 'Vacation photo detected',
    fromPath: '/Downloads',
    toPath: '/Photos/Summer_2024',
    status: 'Done',
    fileType: 'image'
  },
  {
    id: 2,
    filename: 'family-dinner.jpg',
    confidence: '96%',
    timeAgo: '16 minutes ago',
    detection: 'Family photo detected',
    fromPath: '/Downloads',
    toPath: '/Photos/Summer_2024',
    status: 'Done',
    fileType: 'image'
  },
  {
    id: 3,
    filename: 'IMG_001.jpg',
    confidence: '85%',
    timeAgo: '20 minutes ago',
    detection: 'Personal photo detected',
    fromPath: '/Downloads',
    toPath: '/Photos/Personal',
    status: 'Done',
    fileType: 'image'
  }
];

export const initialMessages = [
  {
    id: 1,
    type: 'ai',
    content: "Hi! I'm your AI file organizer. I can help you sort, categorize, and manage your files. What would you like to do today?",
    timestamp: '4:52:33 PM'
  }
];

export const aiResponses = [
  "I can help you organize those files! Let me analyze your folder structure and suggest the best categorization approach.",
  "Great question! I'll scan your files and create appropriate categories based on their content and metadata.",
  "I've identified several duplicate files in your system. Would you like me to help you clean them up?",
  "Based on your file patterns, I recommend creating categories for Work Documents, Personal Photos, and Media Files.",
  "I can set up automated rules to organize future files as they arrive. What types of files do you work with most often?"
];

// CHANGED: All defaults now 50 instead of 85/80/75/70
export const defaultSettings = {
  confidenceThresholds: {
    text: 50,
    images: 50,
    audio: 50,
    video: 50
  },
  fallbackBehavior: "Skip file",
  preloadModels: true,
  modelToggles: {
    textClassification: true,
    imageRecognition: true,
    audioProcessing: false,
    videoAnalysis: false
  },
  scanFrequency: 'Hourly'
};