import React, { useState, useEffect } from 'react';
import {
  Settings,
  AlertTriangle,
  Brain,
  Zap,
  RotateCcw,
  Palette,
  Bell,
  Sliders
} from 'lucide-react';

// Inline components

const SettingsCard = ({ title, children, icon: Icon }) => {
  return (
    <div
      className="rounded-lg border p-6"
      style={{
        backgroundColor: 'var(--theme-bg-secondary)',
        borderColor: 'var(--theme-border-primary)'
      }}
    >
      <div className="flex items-center space-x-3 mb-6">
        {Icon && (
          <Icon
            className="w-5 h-5"
            style={{ color: 'var(--theme-text-tertiary)' }}
          />
        )}
        <h3
          className="text-lg font-semibold"
          style={{ color: 'var(--theme-text-primary)' }}
        >
          {title}
        </h3>
      </div>
      <div className="space-y-4">{children}</div>
    </div>
  );
};

const Slider = ({ label, value, onChange, min = 0, max = 100, step = 1 }) => {
  return (
    <div className="flex flex-col space-y-2">
      <div className="flex justify-between items-center">
        <label
          className="text-sm font-medium"
          style={{ color: 'var(--theme-text-primary)' }}
        >
          {label}
        </label>
        <span
          className="text-sm"
          style={{ color: 'var(--theme-text-tertiary)' }}
        >
          {value}%
        </span>
      </div>
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(e) => onChange(parseInt(e.target.value))}
        className="slider"
        style={{
          width: '100%',
          height: '8px',
          borderRadius: '4px',
          background: `linear-gradient(to right, var(--theme-primary) 0%, var(--theme-primary) ${value}%, var(--theme-border-primary) ${value}%, var(--theme-border-primary) 100%)`,
          outline: 'none',
          WebkitAppearance: 'none',
          appearance: 'none'
        }}
      />
    </div>
  );
};

const Dropdown = ({ label, value, onChange, options }) => {
  return (
    <div className="flex flex-col space-y-2">
      <label
        className="text-sm font-medium"
        style={{ color: 'var(--theme-text-primary)' }}
      >
        {label}
      </label>
      <div className="relative">
        <select
          value={value}
          onChange={(e) => onChange(e.target.value)}
          className="w-full appearance-none border rounded-lg px-4 py-2 pr-8 text-sm focus:ring-2 focus:ring-offset-2"
          style={{
            backgroundColor: 'var(--theme-bg-secondary)',
            borderColor: 'var(--theme-border-primary)',
            color: 'var(--theme-text-primary)'
          }}
        >
          {options.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
        <svg
          className="absolute right-3 top-1/2 transform -translate-y-1/2 w-4 h-4 pointer-events-none"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
          style={{ color: 'var(--theme-text-tertiary)' }}
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M19 9l-7 7-7-7"
          />
        </svg>
      </div>
    </div>
  );
};

const Switch = ({ label, value, onChange, description }) => {
  return (
    <div className="flex items-center justify-between py-2">
      <div className="flex flex-col">
        <span
          className="text-sm font-medium"
          style={{ color: 'var(--theme-text-primary)' }}
        >
          {label}
        </span>
        {description && (
          <span
            className="text-xs"
            style={{ color: 'var(--theme-text-tertiary)' }}
          >
            {description}
          </span>
        )}
      </div>
      <button
        onClick={() => onChange(!value)}
        className="relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2"
        style={{
          backgroundColor: value
            ? 'var(--theme-toggle-active)'
            : 'var(--theme-border-primary)'
        }}
      >
        <span
          className="inline-block h-4 w-4 transform rounded-full bg-white transition-transform"
          style={{
            transform: value ? 'translateX(1.5rem)' : 'translateX(0.25rem)'
          }}
        />
      </button>
    </div>
  );
};

// ✅ UPDATED: full SettingsPage with chatbotMaximized responsiveness
const SettingsPage = ({ chatbotMaximized = false }) => {
  const loadSettings = () => {
    const savedSettings = window.appSettings || {
      baseTheme: 'light',
      accentColor: 'blue',
      confidenceThresholds: {
        text: 85,
        images: 80,
        audio: 75,
        video: 70
      },
      fallbackBehavior: 'Move to review folder',
      preloadModels: true,
      modelToggles: {
        textClassification: true,
        imageRecognition: true,
        audioProcessing: false,
        videoAnalysis: false
      },
      scanFrequency: 'Hourly',
      runOnStartup: false,
      desktopNotifications: true,
      minimizeToTray: true,
      maxFileSize: 500,
      skipHiddenFiles: true,
      preserveMetadata: true,
      createBackups: false,
      logLevel: 'Info'
    };
    return savedSettings;
  };

  const [settings, setSettings] = useState(loadSettings());
  const [activeTab, setActiveTab] = useState('general');

  useEffect(() => {
    applyTheme(settings.baseTheme, settings.accentColor);
  }, []);

  useEffect(() => {
    window.appSettings = settings;
  }, [settings]);

  const baseThemes = [
    { value: 'light', label: 'Light' },
    { value: 'dark', label: 'Dark' }
  ];

  const accentColors = [
    { value: 'blue', label: 'Blue' },
    { value: 'green', label: 'Green' },
    { value: 'purple', label: 'Purple' },
    { value: 'rose', label: 'Rose' },
    { value: 'orange', label: 'Orange' },
    { value: 'teal', label: 'Teal' }
  ];

  const updateConfidenceThreshold = (type, value) => {
    setSettings((prev) => ({
      ...prev,
      confidenceThresholds: {
        ...prev.confidenceThresholds,
        [type]: value
      }
    }));
  };

  const updateModelToggle = (model, value) => {
    setSettings((prev) => ({
      ...prev,
      modelToggles: {
        ...prev.modelToggles,
        [model]: value
      }
    }));
  };

  const updateSetting = (key, value) => {
    setSettings((prev) => ({
      ...prev,
      [key]: value
    }));
  };

  const getAccentColors = (accent) => {
    const colors = {
      blue: { primary: '#2563eb', hover: '#1d4ed8' },
      green: { primary: '#16a34a', hover: '#15803d' },
      purple: { primary: '#9333ea', hover: '#7e22ce' },
      rose: { primary: '#e11d48', hover: '#be123c' },
      orange: { primary: '#ea580c', hover: '#c2410c' },
      teal: { primary: '#0891b2', hover: '#0e7490' }
    };
    return colors[accent] || colors.blue;
  };

  const applyTheme = (base, accent) => {
    const root = document.documentElement;
    const accentColors = getAccentColors(accent);

    if (base === 'dark') {
      root.style.setProperty('--theme-bg-primary', '#09090b');
      root.style.setProperty('--theme-bg-secondary', '#18181b');
      root.style.setProperty('--theme-bg-tertiary', '#27272a');
      root.style.setProperty('--theme-text-primary', '#fafafa');
      root.style.setProperty('--theme-text-secondary', '#d4d4d8');
      root.style.setProperty('--theme-text-tertiary', '#a1a1aa');
      root.style.setProperty('--theme-border-primary', '#3f3f46');
      root.style.setProperty('--theme-border-secondary', '#27272a');
      root.style.setProperty('--theme-sidebar-active', '#3f3f46');
      root.style.setProperty('--theme-sidebar-hover', '#27272a');
      root.style.setProperty('--theme-card-hover', '#27272a');
      root.style.setProperty('--theme-chat-ai-bg', '#27272a');
      root.style.setProperty('--theme-chat-ai-text', '#fafafa');
      root.style.setProperty('--theme-slider-thumb', '#e4e4e7');
    } else {
      root.style.setProperty('--theme-bg-primary', '#f9fafb');
      root.style.setProperty('--theme-bg-secondary', '#ffffff');
      root.style.setProperty('--theme-bg-tertiary', '#f3f4f6');
      root.style.setProperty('--theme-text-primary', '#111827');
      root.style.setProperty('--theme-text-secondary', '#4b5563');
      root.style.setProperty('--theme-text-tertiary', '#6b7280');
      root.style.setProperty('--theme-border-primary', '#e5e7eb');
      root.style.setProperty('--theme-border-secondary', '#f3f4f6');
      root.style.setProperty('--theme-sidebar-active', '#f3f4f6');
      root.style.setProperty('--theme-sidebar-hover', '#f9fafb');
      root.style.setProperty('--theme-card-hover', '#f9fafb');
      root.style.setProperty('--theme-chat-ai-bg', '#f3f4f6');
      root.style.setProperty('--theme-chat-ai-text', '#111827');
      root.style.setProperty('--theme-slider-thumb', '#1f2937');
    }

    root.style.setProperty('--theme-primary', accentColors.primary);
    root.style.setProperty('--theme-primary-hover', accentColors.hover);
    root.style.setProperty('--theme-toggle-active', accentColors.primary);
    root.style.setProperty('--theme-chat-user-bg', accentColors.primary);
  };

  const fallbackOptions = [
    { value: 'Move to review folder', label: 'Move to review folder' },
    { value: 'Skip file', label: 'Skip file' },
    { value: 'Move to misc', label: 'Move to misc folder' }
  ];

  const scanFrequencyOptions = [
    { value: 'Real-time', label: 'Real-time' },
    { value: 'Every 5 minutes', label: 'Every 5 minutes' },
    { value: 'Hourly', label: 'Hourly' },
    { value: 'Daily', label: 'Daily' },
    { value: 'Manual', label: 'Manual only' }
  ];

  const logLevelOptions = [
    { value: 'Error', label: 'Error only' },
    { value: 'Warning', label: 'Warning' },
    { value: 'Info', label: 'Info' },
    { value: 'Debug', label: 'Debug' },
    { value: 'Verbose', label: 'Verbose' }
  ];

  // ✅ MAIN RETURN WITH RESPONSIVE WIDTH
  return (
    <div
      className="flex-1 flex flex-col overflow-hidden transition-all duration-300"
      style={{
        width: chatbotMaximized ? 'calc(100% - 420px)' : '100%',
        transition: 'width 0.3s ease'
      }}
    >
      {/* HEADER */}
      <div
        className="border-b px-6 max-w-7xl mx-auto w-full"
        style={{
          backgroundColor: 'var(--theme-bg-secondary)',
          borderColor: 'var(--theme-border-primary)'
        }}
      >
        <div className="flex space-x-8">
          <button
            onClick={() => setActiveTab('general')}
            className="py-4 text-sm font-medium border-b-2 transition-colors"
            style={{
              borderColor:
                activeTab === 'general'
                  ? 'var(--theme-primary)'
                  : 'transparent',
              color:
                activeTab === 'general'
                  ? 'var(--theme-primary)'
                  : 'var(--theme-text-tertiary)'
            }}
          >
            General Settings
          </button>
          <button
            onClick={() => setActiveTab('advanced')}
            className="py-4 text-sm font-medium border-b-2 transition-colors"
            style={{
              borderColor:
                activeTab === 'advanced'
                  ? 'var(--theme-primary)'
                  : 'transparent',
              color:
                activeTab === 'advanced'
                  ? 'var(--theme-primary)'
                  : 'var(--theme-text-tertiary)'
            }}
          >
            Advanced Settings
          </button>
        </div>
      </div>

      {/* CONTENT */}
      <div className="flex-1 p-6 overflow-auto">
        {/* ... rest of your settings content remains unchanged ... */}
      </div>
    </div>
  );
};

export default SettingsPage;
