import React, { useState, useEffect } from 'react';
import { Settings, AlertTriangle, Brain, Zap, RotateCcw, Palette, Bell, Sliders } from 'lucide-react';
import apiService from '../../services/api';

// --- Inline Components ---
const SettingsCard = ({ title, children, icon: Icon }) => (
  <div
    className="rounded-lg border p-6"
    style={{
      backgroundColor: 'var(--theme-bg-secondary)',
      borderColor: 'var(--theme-border-primary)',
    }}
  >
    <div className="flex items-center space-x-3 mb-6">
      {Icon && <Icon className="w-5 h-5" style={{ color: 'var(--theme-text-tertiary)' }} />}
      <h3 className="text-lg font-semibold" style={{ color: 'var(--theme-text-primary)' }}>
        {title}
      </h3>
    </div>
    <div className="space-y-4">{children}</div>
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
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
      </svg>
    </div>
  </div>
);

const Switch = ({ label, value, onChange, description }) => (
  <div className="flex items-center justify-between py-2">
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
const SettingsPage = ({ chatbotMaximized = false }) => {
  const loadSettings = () => {
    return window.appSettings || {
      baseTheme: 'light',
      accentColor: 'blue',
      confidenceThreshold: 30,
      confidenceThresholds: { text: 85, images: 80, audio: 75, video: 70 },
      fallbackBehavior: 'Move to review folder',
      preloadModels: true,
      modelToggles: { textClassification: true, imageRecognition: true, audioProcessing: false, videoAnalysis: false },
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
  };

  const [settings, setSettings] = useState(loadSettings());
  const [activeTab, setActiveTab] = useState('general');
  const [saving, setSaving] = useState(false);
  const [saveMessage, setSaveMessage] = useState('');

  useEffect(() => {
    applyTheme(settings.baseTheme, settings.accentColor);
  }, []);

  useEffect(() => {
    window.appSettings = settings;
  }, [settings]);

  // Load current threshold from backend on mount
  useEffect(() => {
    loadBackendThreshold();
  }, []);

  const loadBackendThreshold = async () => {
    try {
      const response = await apiService.getConfidenceThreshold();
      if (response && response.threshold !== undefined) {
        setSettings(prev => ({ ...prev, confidenceThreshold: Math.round(response.threshold * 100) }));
      }
    } catch (error) {
      console.error('Error loading threshold:', error);
    }
  };

  const saveThresholdToBackend = async (threshold) => {
    setSaving(true);
    setSaveMessage('');
    try {
      // Convert percentage to decimal (e.g., 30% -> 0.3)
      const decimalThreshold = threshold / 100;
      await apiService.updateConfidenceThreshold(decimalThreshold);
      setSaveMessage('✓ Threshold saved successfully');
      setTimeout(() => setSaveMessage(''), 3000);
    } catch (error) {
      console.error('Error saving threshold:', error);
      setSaveMessage('✗ Failed to save threshold');
      setTimeout(() => setSaveMessage(''), 3000);
    } finally {
      setSaving(false);
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

  const updateConfidenceThreshold = (value) => {
    setSettings((prev) => ({ ...prev, confidenceThreshold: value }));
    // Debounce the save to avoid too many API calls
    clearTimeout(window.thresholdSaveTimeout);
    window.thresholdSaveTimeout = setTimeout(() => {
      saveThresholdToBackend(value);
    }, 500);
  };

  const updateModelToggle = (model, value) => {
    setSettings((prev) => ({ ...prev, modelToggles: { ...prev.modelToggles, [model]: value } }));
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
      root.style.setProperty('--theme-text-primary', '#fafafa');
      root.style.setProperty('--theme-text-tertiary', '#a1a1aa');
      root.style.setProperty('--theme-border-primary', '#3f3f46');
    } else {
      root.style.setProperty('--theme-bg-primary', '#f9fafb');
      root.style.setProperty('--theme-bg-secondary', '#ffffff');
      root.style.setProperty('--theme-text-primary', '#111827');
      root.style.setProperty('--theme-text-tertiary', '#6b7280');
      root.style.setProperty('--theme-border-primary', '#e5e7eb');
    }
    root.style.setProperty('--theme-primary', accentColors.primary);
    root.style.setProperty('--theme-primary-hover', accentColors.hover);
    root.style.setProperty('--theme-toggle-active', accentColors.primary);
  };

  const fallbackOptions = [
    { value: 'Move to review folder', label: 'Move to review folder' },
    { value: 'Skip file', label: 'Skip file' },
    { value: 'Move to misc', label: 'Move to misc folder' },
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
      className="flex-1 flex flex-col overflow-hidden transition-all duration-300"
      style={{
        width: chatbotMaximized ? 'calc(100% - 420px)' : '100%',
        transition: 'width 0.3s ease',
      }}
    >
      {/* Tabs */}
      <div
        className="border-b px-6 w-full sticky top-0 z-10 flex space-x-8"
        style={{
          backgroundColor: 'var(--theme-bg-secondary)',
          borderColor: 'var(--theme-border-primary)',
        }}
      >
        <button
          onClick={() => setActiveTab('general')}
          className="py-4 text-sm font-medium border-b-2 transition-colors"
          style={{
            borderColor: activeTab === 'general' ? 'var(--theme-primary)' : 'transparent',
            color: activeTab === 'general' ? 'var(--theme-primary)' : 'var(--theme-text-tertiary)',
          }}
        >
          General Settings
        </button>
        <button
          onClick={() => setActiveTab('advanced')}
          className="py-4 text-sm font-medium border-b-2 transition-colors"
          style={{
            borderColor: activeTab === 'advanced' ? 'var(--theme-primary)' : 'transparent',
            color: activeTab === 'advanced' ? 'var(--theme-primary)' : 'var(--theme-text-tertiary)',
          }}
        >
          Advanced Settings
        </button>
      </div>

      {/* Content */}
      <div
        className="flex-1 overflow-auto p-6"
        style={{ paddingRight: chatbotMaximized ? '2rem' : '4rem' }}
      >
        {/* General Tab */}
        {activeTab === 'general' ? (
          <div className={`grid gap-6 ${chatbotMaximized ? 'grid-cols-1' : 'grid-cols-2'}`}>
            {/* Appearance */}
            <SettingsCard title="Appearance" icon={Palette}>
              <Dropdown
                label="Theme"
                value={settings.baseTheme}
                onChange={(value) => {
                  updateSetting('baseTheme', value);
                  applyTheme(value, settings.accentColor);
                }}
                options={baseThemes}
              />
              <Dropdown
                label="Accent Color"
                value={settings.accentColor}
                onChange={(value) => {
                  updateSetting('accentColor', value);
                  applyTheme(settings.baseTheme, value);
                }}
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
              <div className={`grid gap-6 ${chatbotMaximized ? 'grid-cols-2' : 'grid-cols-4'}`}>
                <Slider
                  label="Text"
                  value={settings.confidenceThresholds?.text || settings.confidenceThreshold}
                  onChange={(value) => {
                    setSettings(prev => ({
                      ...prev,
                      confidenceThreshold: value,
                      confidenceThresholds: { ...prev.confidenceThresholds, text: value }
                    }));
                    saveThresholdToBackend(value);
                  }}
                />
                <Slider
                  label="Images"
                  value={settings.confidenceThresholds?.images || 80}
                  onChange={(value) => {
                    setSettings(prev => ({
                      ...prev,
                      confidenceThresholds: { ...prev.confidenceThresholds, images: value }
                    }));
                  }}
                />
                <Slider
                  label="Audio"
                  value={settings.confidenceThresholds?.audio || 75}
                  onChange={(value) => {
                    setSettings(prev => ({
                      ...prev,
                      confidenceThresholds: { ...prev.confidenceThresholds, audio: value }
                    }));
                  }}
                />
                <Slider
                  label="Video"
                  value={settings.confidenceThresholds?.video || 70}
                  onChange={(value) => {
                    setSettings(prev => ({
                      ...prev,
                      confidenceThresholds: { ...prev.confidenceThresholds, video: value }
                    }));
                  }}
                />
              </div>
              {saveMessage && (
                <p className={`text-xs ${saveMessage.startsWith('✓') ? 'text-green-600' : 'text-red-600'}`}>
                  {saveMessage}
                </p>
              )}
              <p className="text-xs" style={{ color: 'var(--theme-text-tertiary)' }}>
                Files with confidence below the threshold will not be automatically sorted
              </p>
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
              <Switch
                label="Pre-load models"
                value={settings.preloadModels}
                onChange={(value) => updateSetting('preloadModels', value)}
              />
              <div className="pt-3 mt-3 space-y-1" style={{ borderTop: '1px solid var(--theme-border-secondary)' }}>
                <Switch
                  label="Text"
                  value={settings.modelToggles.textClassification}
                  onChange={(value) => updateModelToggle('textClassification', value)}
                />
                <Switch
                  label="Images"
                  value={settings.modelToggles.imageRecognition}
                  onChange={(value) => updateModelToggle('imageRecognition', value)}
                />
                <Switch
                  label="Audio"
                  value={settings.modelToggles.audioProcessing}
                  onChange={(value) => updateModelToggle('audioProcessing', value)}
                />
                <Switch
                  label="Video"
                  value={settings.modelToggles.videoAnalysis}
                  onChange={(value) => updateModelToggle('videoAnalysis', value)}
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
          // --- Advanced Tab ---
          <div className={`grid gap-6 ${chatbotMaximized ? 'grid-cols-1' : 'grid-cols-3'}`}>
            <SettingsCard title="File Processing" icon={Sliders}>
              <div className="space-y-4">
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
              <div className="flex items-center justify-between">
                <div>
                  <h4 className="text-sm font-medium" style={{ color: 'var(--theme-text-primary)' }}>
                    Clear Application Cache
                  </h4>
                  <p className="text-xs mt-1" style={{ color: 'var(--theme-text-tertiary)' }}>
                    Remove temporary files and cached data
                  </p>
                </div>
                <button className="px-4 py-2 text-sm text-red-600 bg-red-50 border border-red-200 rounded-lg hover:bg-red-100 transition-colors">
                  Clear Cache
                </button>
              </div>
            </SettingsCard>
          </div>
        )}
      </div>
    </div>
  );
};

export default SettingsPage;