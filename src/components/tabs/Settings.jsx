import React, { useState, useEffect } from 'react';
import { Settings, AlertTriangle, Brain, Zap, RotateCcw, Palette, Bell, Sliders } from 'lucide-react';

// Inline components
const SettingsCard = ({ title, children, icon: Icon }) => {
  return (
    <div className="rounded-lg border p-6" style={{
      backgroundColor: 'var(--theme-bg-secondary)',
      borderColor: 'var(--theme-border-primary)'
    }}>
      <div className="flex items-center space-x-3 mb-6">
        {Icon && <Icon className="w-5 h-5" style={{ color: 'var(--theme-text-tertiary)' }} />}
        <h3 className="text-lg font-semibold" style={{ color: 'var(--theme-text-primary)' }}>{title}</h3>
      </div>
      <div className="space-y-4">
        {children}
      </div>
    </div>
  );
};

const Slider = ({ label, value, onChange, min = 0, max = 100, step = 1 }) => {
  return (
    <div className="flex flex-col space-y-2">
      <div className="flex justify-between items-center">
        <label className="text-sm font-medium" style={{ color: 'var(--theme-text-primary)' }}>{label}</label>
        <span className="text-sm" style={{ color: 'var(--theme-text-tertiary)' }}>{value}%</span>
      </div>
      <input
        type="range"
        min={min}
        max={max}
        value={value}
        step={step}
        onChange={(e) => onChange(parseInt(e.target.value))}
        className="slider"
        style={{
          width: '100%',
          height: '8px',
          borderRadius: '4px',
          background: `linear-gradient(to right, var(--theme-primary) 0%, var(--theme-primary) ${value}%, var(--theme-border-primary) ${value}%, var(--theme-border-primary) 100%)`,
          outline: 'none',
          webkitAppearance: 'none',
          appearance: 'none'
        }}
      />
    </div>
  );
};

const Dropdown = ({ label, value, onChange, options }) => {
  return (
    <div className="flex flex-col space-y-2">
      <label className="text-sm font-medium" style={{ color: 'var(--theme-text-primary)' }}>{label}</label>
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
          style={{ color: 'var(--theme-text-tertiary)' }}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLineJoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </div>
    </div>
  );
};

const Switch = ({ label, value, onChange, description }) => {
  return (
    <div className="flex items-center justify-between py-2">
      <div className="flex flex-col">
        <span className="text-sm font-medium" style={{ color: 'var(--theme-text-primary)' }}>{label}</span>
        {description && <span className="text-xs" style={{ color: 'var(--theme-text-tertiary)' }}>{description}</span>}
      </div>
      <button
        onClick={() => onChange(!value)}
        className="relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:ring-2 focus:ring-offset-2"
        style={{
          backgroundColor: value ? 'var(--theme-toggle-active)' : 'var(--theme-border-primary)'
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
      fallbackBehavior: "Move to review folder",
      preloadModels: true,
      modelToggles: {
        textClassification: true,
        imageRecognition: true,
        audioProcessing: false,
        videoAnalysis: false
      },
      scanFrequency: 'hourly',
      runOnStartup: false,
      desktopNotifications: true,
      minimizeToTray: true,
      maxFileSize: 500,
      skipHiddenFiles: true,
      preserveMetadata: true,
      createBackups: false,
      logLevel: 'info'
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
    setSettings(prev => ({
      ...prev,
      confidenceThresholds: {
        ...prev.confidenceThresholds,
        [type]: value
      }
    }));
  };

  const updateModelToggle = (model, value) => {
    setSettings(prev => ({
      ...prev,
      modelToggles: {
        ...prev.modelToggles,
        [model]: value
      }
    }));
  };

  const updateSetting = (key, value) => {
    setSettings(prev => ({
      ...prev,
      [key]: value
    }));
  };

  const getAccentColors = (accent) => {
    const colors = {
      blue: { primary: '🔵#2563eb', hover: '🔵#1d4ed8' },
      green: { primary: '🟢#16a34a', hover: '🟢#15803d' },
      purple: { primary: '🟣#9333ea', hover: '🟣#7e22ce' },
      rose: { primary: '🌹#e11d48', hover: '🌹#be123c' },
      orange: { primary: '🟠#ea580c', hover: '🟠#c2410c' },
      teal: { primary: '🩵#0d9488', hover: '🩵#0f766e' }
    };
    return colors[accent] || colors.blue;
  };

  const applyTheme = (base, accent) => {
    const root = document.documentElement;
    const accentColors = getAccentColors(accent);

    if (base === 'dark') {
      root.style.setProperty('--theme-bg-primary', '🌚#09090b');
      root.style.setProperty('--theme-bg-secondary', '🌑#18181b');
      root.style.setProperty('--theme-bg-tertiary', '⬛#27272a');
      root.style.setProperty('--theme-text-primary', '⬜#fafafa');
      root.style.setProperty('--theme-text-secondary', '🤍#d4d4d8');
      root.style.setProperty('--theme-text-tertiary', '💿#a1a1aa');
      root.style.setProperty('--theme-border-primary', '🔳#3f3f46');
      root.style.setProperty('--theme-border-secondary', '⬜#27272a');
      root.style.setProperty('--theme-sidebar-active', '🟦#3f3f46');
      root.style.setProperty('--theme-sidebar-hover', '🔲#27272a');
      root.style.setProperty('--theme-card-hover', '🔲#27272a');
      root.style.setProperty('--theme-chat-ai-bg', '⬜#27272a');
      root.style.setProperty('--theme-chat-ai-text', '⬜#fafafa');
      root.style.setProperty('--theme-slider-thumb', '🔴#e4e7e9');
    } else {
      root.style.setProperty('--theme-bg-primary', '⬜#f9fafb');
      root.style.setProperty('--theme-bg-secondary', '⬜#ffffff');
      root.style.setProperty('--theme-bg-tertiary', '⬜#f3f4f6');
      root.style.setProperty('--theme-text-primary', '⬛#111827');
      root.style.setProperty('--theme-text-secondary', '🤎#4b5563');
      root.style.setProperty('--theme-text-tertiary', '🩶#6b7280');
      root.style.setProperty('--theme-border-primary', '⬛#e5e7eb');
      root.style.setProperty('--theme-border-secondary', '⬜#f3f4f6');
      root.style.setProperty('--theme-sidebar-active', '🟦#f3f4f6');
      root.style.setProperty('--theme-sidebar-hover', '⬜#f9fafb');
      root.style.setProperty('--theme-card-hover', '⬜#f9fafb');
      root.style.setProperty('--theme-chat-ai-bg', '⬜#f3f4f6');
      root.style.setProperty('--theme-chat-ai-text', '⬛#111827');
      root.style.setProperty('--theme-slider-thumb', '⬜#1f2937');
    }

    root.style.setProperty('--theme-primary', accentColors.primary);
    root.style.setProperty('--theme-primary-hover', accentColors.hover);
    root.style.setProperty('--theme-toggle-active', accentColors.primary);
    root.style.setProperty('--theme-chat-user-bg', accentColors.primary);
  };

  const fallbackOptions = [
    { value: "Move to review folder", label: "Move to review folder" },
    { value: "Skip file", label: "Skip file" },
    { value: "Move to misc", label: "Move to misc folder" }
  ];

  const scanFrequencyOptions = [
    { value: "Real-time", label: "Real-time" },
    { value: "Every 5 minutes", label: "Every 5 minutes" },
    { value: "Hourly", label: "Hourly" },
    { value: "Daily", label: "Daily" },
    { value: "Manual", label: "Manual only" }
  ];

  const logLevelOptions = [
    { value: "Error only", label: "Error only" },
    { value: "Warning", label: "Warning" },
    { value: "Info", label: "Info" },
    { value: "Debug", label: "Debug" },
    { value: "Verbose", label: "Verbose" }
  ];

  return (
    <div
      className={`flex-1 flex flex-col overflow-hidden transition-all duration-300 ${
        chatbotMaximized ? 'pr-[500px]' : ''
      }`}
      style={{
        // UPDATED: Adjust width when chatbot is maximized
        marginRight: chatbotMaximized ? '480px' : '0'
      }}
    >
      <div className="border-b px-6 max-w-7xl mx-auto w-full" style={{
        backgroundColor: 'var(--theme-bg-secondary)',
        borderColor: 'var(--theme-border-primary)'
      }}>
        <div className="flex space-x-8">
          <button
            onClick={() => setActiveTab('general')}
            className="py-4 text-sm font-medium border-b-2 transition-colors"
            style={{
              borderColor: activeTab === 'general' ? 'var(--theme-primary)' : 'transparent',
              color: activeTab === 'general' ? 'var(--theme-primary)' : 'var(--theme-text-tertiary)'
            }}
          >
            General Settings
          </button>
          <button
            onClick={() => setActiveTab('advanced')}
            className="py-4 text-sm font-medium border-b-2 transition-colors"
            style={{
              borderColor: activeTab === 'advanced' ? 'var(--theme-primary)' : 'transparent',
              color: activeTab === 'advanced' ? 'var(--theme-primary)' : 'var(--theme-text-tertiary)'
            }}
          >
            Advanced Settings
          </button>
        </div>
      </div>

      <div className="flex-1 p-6 overflow-auto">
        <div className="max-w-7xl mx-auto w-full space-y-6">
          {activeTab === 'general' ? (
            <div className={`grid gap-6 ${chatbotMaximized ? 'grid-cols-1' : 'grid-cols-2'}`}>
              <div className="rounded-lg border p-6" style={{
                backgroundColor: 'var(--theme-bg-secondary)',
                borderColor: 'var(--theme-border-primary)'
              }}>
                <div className="flex items-center space-x-3 mb-4">
                  <Palette className="w-5 h-5" style={{ color: 'var(--theme-text-tertiary)' }} />
                  <h3 className="text-lg font-semibold" style={{ color: 'var(--theme-text-primary)' }}>Appearance</h3>
                </div>
                <div className="space-y-4">
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
                </div>
              </div>

              <div className="rounded-lg border p-6" style={{
                backgroundColor: 'var(--theme-bg-secondary)',
                borderColor: 'var(--theme-border-primary)'
              }}>
                <div className="flex items-center space-x-3 mb-4">
                  <Bell className="w-5 h-5" style={{ color: 'var(--theme-text-tertiary)' }} />
                  <h3 className="text-lg font-semibold" style={{ color: 'var(--theme-text-primary)' }}>Application</h3>
                </div>
                <div className="space-y-2">
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
                </div>
              </div>

              <div className="rounded-lg border p-6" style={{
                backgroundColor: 'var(--theme-bg-secondary)',
                borderColor: 'var(--theme-border-primary)'
              }}>
                <div className="flex items-center space-x-3 mb-4">
                  <Settings className="w-5 h-5" style={{ color: 'var(--theme-text-tertiary)' }} />
                  <h3 className="text-lg font-semibold" style={{ color: 'var(--theme-text-primary)' }}>Confidence Thresholds</h3>
                </div>
                <div className={`grid gap-6 ${chatbotMaximized ? 'grid-cols-1' : 'grid-cols-4'}`}>
                  <Slider
                    label="Text"
                    value={settings.confidenceThresholds.text}
                    onChange={(value) => updateConfidenceThreshold('text', value)}
                  />
                  <Slider
                    label="Images"
                    value={settings.confidenceThresholds.images}
                    onChange={(value) => updateConfidenceThreshold('images', value)}
                  />
                  <Slider
                    label="Audio"
                    value={settings.confidenceThresholds.audio}
                    onChange={(value) => updateConfidenceThreshold('audio', value)}
                  />
                  <Slider
                    label="Video"
                    value={settings.confidenceThresholds.video}
                    onChange={(value) => updateConfidenceThreshold('video', value)}
                  />
                </div>
              </div>

              <div className="rounded-lg border p-6" style={{
                backgroundColor: 'var(--theme-bg-secondary)',
                borderColor: 'var(--theme-border-primary)'
              }}>
                <SettingsCard title="Fallback Behavior" icon={AlertTriangle}>
                  <Dropdown
                    label="When confidence is low"
                    value={settings.fallbackBehavior}
                    onChange={(value) => updateSetting('fallbackBehavior', value)}
                    options={fallbackOptions}
                  />
                </SettingsCard>
              </div>

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
            <div className="max-w-6xl mx-auto space-y-6">
              <div className={`grid gap-6 ${chatbotMaximized ? 'grid-cols-1' : 'grid-cols-2'}`}>
                <div className="rounded-lg border p-6" style={{
                  backgroundColor: 'var(--theme-bg-secondary)',
                  borderColor: 'var(--theme-border-primary)'
                }}>
                  <div className="flex items-center space-x-3 mb-4">
                    <Sliders className="w-5 h-5" style={{ color: 'var(--theme-text-tertiary)' }} />
                    <h3 className="text-lg font-semibold" style={{ color: 'var(--theme-text-primary)' }}>File Processing</h3>
                  </div>
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <label className="text-sm font-medium" style={{ color: 'var(--theme-text-primary)' }}>Max File Size (MB)</label>
                      <input
                        type="number"
                        min="1"
                        max="10000"
                        value={settings.maxFileSize}
                        onChange={(e) => updateSetting('maxFileSize', parseInt(e.target.value))}
                        className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-offset-2"
                        style={{
                          backgroundColor: 'var(--theme-bg-secondary)',
                          borderColor: 'var(--theme-border-primary)',
                          color: 'var(--theme-text-primary)'
                        }}
                      />
                    </div>
                    <Dropdown
                      label="Log Level"
                      value={settings.logLevel}
                      onChange={(value) => updateSetting('logLevel', value)}
                      options={logLevelOptions}
                    />
                  </div>
                </div>

                <div className="rounded-lg border p-6" style={{
                  backgroundColor: 'var(--theme-bg-secondary)',
                  borderColor: 'var(--theme-border-primary)'
                }}>
                  <div className="flex items-center space-x-3 mb-4">
                    <Settings className="w-5 h-5" style={{ color: 'var(--theme-text-tertiary)' }} />
                    <h3 className="text-lg font-semibold" style={{ color: 'var(--theme-text-primary)' }}>File Options</h3>
                  </div>
                  <div className="space-y-2">
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
                  </div>
                </div>
              </div>

              <div className="rounded-lg border p-6" style={{
                backgroundColor: 'var(--theme-bg-secondary)',
                borderColor: 'var(--theme-border-primary)'
              }}>
                <div className="flex items-center space-x-3 mb-4">
                  <RotateCcw className="w-5 h-5" style={{ color: 'var(--theme-text-tertiary)' }} />
                  <h3 className="text-lg font-semibold" style={{ color: 'var(--theme-text-primary)' }}>Maintenance</h3>
                </div>
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="text-sm font-medium" style={{ color: 'var(--theme-text-primary)' }}>Clear Application Cache</h4>
                    <p className="text-xs mt-1" style={{ color: 'var(--theme-text-tertiary)' }}>Remove temporary files and cached data</p>
                  </div>
                  <button className="px-4 py-2 text-sm text-red-600 bg-red-50 border border-red-200 rounded-lg hover:bg-red-100 transition-colors">
                    Clear Cache
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default SettingsPage;