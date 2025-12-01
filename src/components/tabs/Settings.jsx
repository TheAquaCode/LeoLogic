// src/components/tabs/Settings.jsx
import React, { useState, useEffect } from 'react';
import { Settings, AlertTriangle, Brain, Zap, RotateCcw, Palette, Bell, Sliders } from 'lucide-react';
import apiService from '../../services/api';

// --- Inline Components ---
const SettingsCard = ({ title, children, icon: Icon }) => (
  <div
    className="rounded-lg border p-4"
    style={{
      backgroundColor: 'var(--theme-bg-secondary)',
      borderColor: 'var(--theme-border-primary)',
    }}
  >
    <div className="flex items-center space-x-2 mb-4">
      {Icon && <Icon className="w-4 h-4" style={{ color: 'var(--theme-text-tertiary)' }} />}
      <h3 className="text-base font-semibold" style={{ color: 'var(--theme-text-primary)' }}>
        {title}
      </h3>
    </div>
    <div className="space-y-3">{children}</div>
  </div>
);

const Slider = ({ label, value, onChange, min = 0, max = 100, step = 1 }) => (
  <div className="flex flex-col space-y-2">
    <div className="flex justify-between items-center">
      <label className="text-sm font-medium" style={{ color: 'var(--theme-text-primary)' }}>
        {label}
      </label>
      <span className="text-sm" style={{ color: 'var(--theme-text-tertiary)' }}>
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
        appearance: 'none',
      }}
    />
  </div>
);

const Dropdown = ({ label, value, onChange, options }) => (
  <div className="flex flex-col space-y-2">
    <label className="text-sm font-medium" style={{ color: 'var(--theme-text-primary)' }}>
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
          color: 'var(--theme-text-primary)',
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
        <path strokeLinecap="round" strokeLineJoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
      </svg>
    </div>
  </div>
);

const Switch = ({ label, value, onChange, description }) => (
  <div className="flex items-center justify-between py-1">
    <div className="flex flex-col">
      <span className="text-sm font-medium" style={{ color: 'var(--theme-text-primary)' }}>
        {label}
      </span>
      {description && (
        <span className="text-xs" style={{ color: 'var(--theme-text-tertiary)' }}>
          {description}
        </span>
      )}
    </div>
    <button
      onClick={() => onChange(!value)}
      className="relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2"
      style={{
        backgroundColor: value ? 'var(--theme-toggle-active)' : 'var(--theme-border-primary)',
      }}
    >
      <span
        className="inline-block h-4 w-4 transform rounded-full bg-white transition-transform"
        style={{
          transform: value ? 'translateX(1.5rem)' : 'translateX(0.25rem)',
        }}
      />
    </button>
  </div>
);

// --- Main Settings Page ---
const SettingsPage = ({ isChatMaximized = false }) => {
  const defaultSettings = {
    baseTheme: 'light',
    accentColor: 'blue',
    confidenceThresholds: { text: 85, images: 80, audio: 75, video: 70 },
    fallbackBehavior: 'Skip file',
    preloadModels: true,
    modelToggles: { textClassification: true, imageRecognition: true, audioProcessing: true, videoAnalysis: true },
    scanFrequency: 'Hourly',
    runOnStartup: false,
    desktopNotifications: true,
    minimizeToTray: true,
    maxFileSize: 500,
    skipHiddenFiles: true,
    preserveMetadata: true,
    createBackups: false,
    logLevel: 'Info',
  };

  // Initialize from storage for instant load
  const [settings, setSettings] = useState(() => {
    try {
      const cached = localStorage.getItem('app_settings');
      // Merge cached settings with defaults to ensure all keys exist
      return cached ? { ...defaultSettings, ...JSON.parse(cached) } : defaultSettings;
    } catch {
      return defaultSettings;
    }
  });

  const [activeTab, setActiveTab] = useState('general');
  // No blocking loading state - UI renders instantly
  const [saveStatus, setSaveStatus] = useState(null); // 'saving', 'saved', 'error'

  // Load settings from backend on mount (sync)
  useEffect(() => {
    loadSettings();
  }, []);

  // Apply theme whenever it changes
  useEffect(() => {
    applyTheme(settings.baseTheme, settings.accentColor);
  }, [settings.baseTheme, settings.accentColor]);

  // Auto-save settings with debounce
  useEffect(() => {
    // Only auto-save if we have data and it's different (basic check implies user change)
    // We use a simple timer here. In a real app, might want to track 'isDirty'.
    const timer = setTimeout(() => {
      saveSettings(true); // true = silent save
    }, 1000);

    return () => clearTimeout(timer);
  }, [settings]);

  const loadSettings = async () => {
    try {
      const data = await apiService.getSettings();
      // Update state and cache
      setSettings(prev => ({ ...prev, ...data }));
      localStorage.setItem('app_settings', JSON.stringify({ ...settings, ...data }));
      applyTheme(data.baseTheme, data.accentColor);
    } catch (error) {
      console.error('Error syncing settings:', error);
    }
  };

  const saveSettings = async (silent = false) => {
    if (!silent) setSaveStatus('saving');
    
    // Optimistic update to cache
    localStorage.setItem('app_settings', JSON.stringify(settings));

    try {
      await apiService.updateSettings(settings);
      if (!silent) {
        setSaveStatus('saved');
        setTimeout(() => setSaveStatus(null), 2000);
      }
    } catch (error) {
      console.error('Error saving settings:', error);
      if (!silent) {
        setSaveStatus('error');
        setTimeout(() => setSaveStatus(null), 3000);
      }
    }
  };

  const baseThemes = [
    { value: 'light', label: 'Light' },
    { value: 'dark', label: 'Dark' },
  ];

  const accentColors = [
    { value: 'blue', label: 'Blue' },
    { value: 'green', label: 'Green' },
    { value: 'purple', label: 'Purple' },
    { value: 'rose', label: 'Rose' },
    { value: 'orange', label: 'Orange' },
    { value: 'teal', label: 'Teal' },
  ];

  const updateConfidenceThreshold = (type, value) => {
    setSettings((prev) => ({ 
      ...prev, 
      confidenceThresholds: { ...prev.confidenceThresholds, [type]: value } 
    }));
  };

  const updateModelToggle = (model, value) => {
    setSettings((prev) => ({ 
      ...prev, 
      modelToggles: { ...prev.modelToggles, [model]: value } 
    }));
  };

  const updateSetting = (key, value) => {
    setSettings((prev) => ({ ...prev, [key]: value }));
  };

  const getAccentColors = (accent) => {
    const colors = {
      blue: { primary: '#2563eb', hover: '#1d4ed8' },
      green: { primary: '#16a34a', hover: '#15803d' },
      purple: { primary: '#9333ea', hover: '#7e22ce' },
      rose: { primary: '#e11d48', hover: '#be123c' },
      orange: { primary: '#ea580c', hover: '#c2410c' },
      teal: { primary: '#0891b2', hover: '#0e7490' },
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
    } else {
      root.style.setProperty('--theme-bg-primary', '#f9fafb');
      root.style.setProperty('--theme-bg-secondary', '#ffffff');
      root.style.setProperty('--theme-bg-tertiary', '#f3f4f6');
      root.style.setProperty('--theme-text-primary', '#111827');
      root.style.setProperty('--theme-text-secondary', '#6b7280');
      root.style.setProperty('--theme-text-tertiary', '#6b7280');
      root.style.setProperty('--theme-border-primary', '#e5e7eb');
      root.style.setProperty('--theme-border-secondary', '#f3f4f6');
    }
    root.style.setProperty('--theme-primary', accentColors.primary);
    root.style.setProperty('--theme-primary-hover', accentColors.hover);
    root.style.setProperty('--theme-toggle-active', accentColors.primary);
  };

  const fallbackOptions = [
    { value: 'Skip file', label: 'Skip file' },
    { value: 'Move to review folder', label: 'Move to review folder' },
  ];

  const scanFrequencyOptions = [
    { value: 'Real-time', label: 'Real-time' },
    { value: 'Every 5 minutes', label: 'Every 5 minutes' },
    { value: 'Hourly', label: 'Hourly' },
    { value: 'Daily', label: 'Daily' },
    { value: 'Manual', label: 'Manual only' },
  ];

  const logLevelOptions = [
    { value: 'Error', label: 'Error only' },
    { value: 'Warning', label: 'Warning' },
    { value: 'Info', label: 'Info' },
    { value: 'Debug', label: 'Debug' },
    { value: 'Verbose', label: 'Verbose' },
  ];

  return (
    <div
      className={`flex-1 flex flex-col overflow-hidden transition-all duration-300`}
      style={{
        marginRight: isChatMaximized ? '480px' : '0px',
        transition: 'margin-right 0.3s ease',
      }}
    >
      {/* Save Status Indicator */}
      {saveStatus && (
        <div className="fixed top-4 right-4 z-50">
          <div className={`px-4 py-2 rounded-lg shadow-lg ${
            saveStatus === 'saved' ? 'bg-green-500' :
            saveStatus === 'saving' ? 'bg-blue-500' :
            'bg-red-500'
          } text-white text-sm`}>
            {saveStatus === 'saved' && '✓ Settings saved'}
            {saveStatus === 'saving' && 'Saving...'}
            {saveStatus === 'error' && '✗ Error saving settings'}
          </div>
        </div>
      )}

      {/* Tabs */}
      <div
        className="border-b px-6 flex space-x-8"
        style={{
          backgroundColor: 'var(--theme-bg-secondary)',
          borderColor: 'var(--theme-border-primary)',
        }}
      >
        <button
          onClick={() => setActiveTab('general')}
          className="py-3 text-sm font-medium border-b-2 transition-colors"
          style={{
            borderColor: activeTab === 'general' ? 'var(--theme-primary)' : 'transparent',
            color: activeTab === 'general' ? 'var(--theme-primary)' : 'var(--theme-text-tertiary)',
          }}
        >
          General Settings
        </button>
        <button
          onClick={() => setActiveTab('advanced')}
          className="py-3 text-sm font-medium border-b-2 transition-colors"
          style={{
            borderColor: activeTab === 'advanced' ? 'var(--theme-primary)' : 'transparent',
            color: activeTab === 'advanced' ? 'var(--theme-primary)' : 'var(--theme-text-tertiary)',
          }}
        >
          Advanced Settings
        </button>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-auto p-6">
        <div className="max-w-6xl mx-auto w-full">
          {activeTab === 'general' ? (
            <div className="grid gap-4 grid-cols-1">
              {/* Appearance */}
              <SettingsCard title="Appearance" icon={Palette}>
                <Dropdown
                  label="Theme"
                  value={settings.baseTheme}
                  onChange={(value) => updateSetting('baseTheme', value)}
                  options={baseThemes}
                />
                <Dropdown
                  label="Accent Color"
                  value={settings.accentColor}
                  onChange={(value) => updateSetting('accentColor', value)}
                  options={accentColors}
                />
              </SettingsCard>

              {/* Notifications */}
              <SettingsCard title="Notifications" icon={Bell}>
                <Switch
                  label="Run on Startup"
                  value={settings.runOnStartup}
                  onChange={(value) => updateSetting('runOnStartup', value)}
                />
                <Switch
                  label="Desktop Notifications"
                  value={settings.desktopNotifications}
                  onChange={(value) => updateSetting('desktopNotifications', value)}
                />
                <Switch
                  label="Minimize to Tray"
                  value={settings.minimizeToTray}
                  onChange={(value) => updateSetting('minimizeToTray', value)}
                />
              </SettingsCard>

              {/* Confidence Thresholds */}
              <SettingsCard title="Confidence Thresholds" icon={Settings}>
                <p className="text-xs mb-3" style={{ color: 'var(--theme-text-tertiary)' }}>
                  Files must meet these confidence levels to be automatically organized. Lower thresholds = more files organized, but potentially less accurate.
                </p>
                <div className={`grid gap-4 ${isChatMaximized ? 'grid-cols-2' : 'grid-cols-4'}`}>
                  <Slider
                    label="Text Documents"
                    value={settings.confidenceThresholds.text}
                    onChange={(value) => updateConfidenceThreshold('text', value)}
                  />
                  <Slider
                    label="Images"
                    value={settings.confidenceThresholds.images}
                    onChange={(value) => updateConfidenceThreshold('images', value)}
                  />
                  <Slider
                    label="Audio Files"
                    value={settings.confidenceThresholds.audio}
                    onChange={(value) => updateConfidenceThreshold('audio', value)}
                  />
                  <Slider
                    label="Video Files"
                    value={settings.confidenceThresholds.video}
                    onChange={(value) => updateConfidenceThreshold('video', value)}
                  />
                </div>
              </SettingsCard>

              {/* Fallback & Models */}
              <SettingsCard title="Fallback Behavior" icon={AlertTriangle}>
                <Dropdown
                  label="When confidence is low"
                  value={settings.fallbackBehavior}
                  onChange={(value) => updateSetting('fallbackBehavior', value)}
                  options={fallbackOptions}
                />
              </SettingsCard>

              <SettingsCard title="AI Models" icon={Brain}>
                <p className="text-xs mb-2" style={{ color: 'var(--theme-text-tertiary)' }}>
                  Enable/disable AI processing for different file types
                </p>
                <div className="pt-2 space-y-1">
                  <Switch
                    label="Text Classification"
                    value={settings.modelToggles.textClassification}
                    onChange={(value) => updateModelToggle('textClassification', value)}
                    description="PDFs, Word docs, text files"
                  />
                  <Switch
                    label="Image Recognition"
                    value={settings.modelToggles.imageRecognition}
                    onChange={(value) => updateModelToggle('imageRecognition', value)}
                    description="JPG, PNG, PSD, SVG"
                  />
                  <Switch
                    label="Audio Processing"
                    value={settings.modelToggles.audioProcessing}
                    onChange={(value) => updateModelToggle('audioProcessing', value)}
                    description="MP3, WAV, M4A (via Whisper)"
                  />
                  <Switch
                    label="Video Analysis"
                    value={settings.modelToggles.videoAnalysis}
                    onChange={(value) => updateModelToggle('videoAnalysis', value)}
                    description="MP4, AVI, MOV (audio extraction)"
                  />
                </div>
              </SettingsCard>

              <SettingsCard title="Auto-organization" icon={Zap}>
                <Dropdown
                  label="Scan Frequency"
                  value={settings.scanFrequency}
                  onChange={(value) => updateSetting('scanFrequency', value)}
                  options={scanFrequencyOptions}
                />
              </SettingsCard>
            </div>
          ) : (
            <div className="grid gap-4 grid-cols-1">
              <SettingsCard title="File Processing" icon={Sliders}>
                <div className="space-y-3">
                  <div className="space-y-2">
                    <label className="text-sm font-medium" style={{ color: 'var(--theme-text-primary)' }}>
                      Max File Size (MB)
                    </label>
                    <input
                      type="number"
                      value={settings.maxFileSize}
                      onChange={(e) => updateSetting('maxFileSize', parseInt(e.target.value))}
                      className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-offset-2"
                      style={{
                        backgroundColor: 'var(--theme-bg-secondary)',
                        borderColor: 'var(--theme-border-primary)',
                        color: 'var(--theme-text-primary)',
                      }}
                      min="1"
                      max="10000"
                    />
                  </div>
                  <Dropdown
                    label="Log Level"
                    value={settings.logLevel}
                    onChange={(value) => updateSetting('logLevel', value)}
                    options={logLevelOptions}
                  />
                </div>
              </SettingsCard>

              <SettingsCard title="File Options" icon={Settings}>
                <Switch
                  label="Skip Hidden Files"
                  value={settings.skipHiddenFiles}
                  onChange={(value) => updateSetting('skipHiddenFiles', value)}
                  description="Don't process files starting with '.'"
                />
                <Switch
                  label="Preserve Metadata"
                  value={settings.preserveMetadata}
                  onChange={(value) => updateSetting('preserveMetadata', value)}
                  description="Keep file dates"
                />
                <Switch
                  label="Create Backups"
                  value={settings.createBackups}
                  onChange={(value) => updateSetting('createBackups', value)}
                  description="Backup before moving"
                />
              </SettingsCard>

              <SettingsCard title="Maintenance" icon={RotateCcw}>
                <div className="flex items-start justify-between gap-3">
                  <div className="flex-1 min-w-0">
                    <h4 className="text-sm font-medium" style={{ color: 'var(--theme-text-primary)' }}>
                      Clear Application Cache
                    </h4>
                    <p className="text-xs mt-1" style={{ color: 'var(--theme-text-tertiary)' }}>
                      Remove temporary files and cached data
                    </p>
                  </div>
                  <button 
                    onClick={() => {
                      if (window.confirm('Clear all cached data?')) {
                        sessionStorage.clear();
                        localStorage.removeItem('app_settings');
                        alert('Cache cleared!');
                        window.location.reload();
                      }
                    }}
                    className="px-4 py-2 text-sm text-red-600 bg-red-50 border border-red-200 rounded-lg hover:bg-red-100 transition-colors whitespace-nowrap flex-shrink-0"
                  >
                    Clear Cache
                  </button>
                </div>
              </SettingsCard>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default SettingsPage;