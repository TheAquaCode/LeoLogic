import React, { useState } from 'react';
import { Settings as SettingsIcon, AlertTriangle, Brain, Zap, RotateCcw } from 'lucide-react';
import SettingsCard from '../ui/SettingsCard';
import Slider from '../ui/slider';
import Dropdown from '../ui/Dropdown';
import Switch from '../ui/Switch';
import { defaultSettings } from '../../data/mockdata';

const Settings = () => {
  const [settings, setSettings] = useState(defaultSettings);

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

  const resetSettings = () => {
    setSettings(defaultSettings);
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

  return (
    <div className="flex-1 p-6 overflow-hidden">
      {/* Header Actions */}
      <div className="flex justify-end mb-6">
        <button
          onClick={resetSettings}
          className="flex items-center space-x-2 px-4 py-2 text-sm text-gray-600 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
        >
          <RotateCcw className="w-4 h-4" />
          <span>Reset</span>
        </button>
      </div>

      <div className="overflow-y-auto">
        {/* Global Confidence Thresholds - Full Width */}
        <div className="bg-white rounded-lg border border-gray-200 p-6 mb-6">
          <div className="flex items-center space-x-3 mb-6">
            <SettingsIcon className="w-5 h-5 text-gray-500" />
            <h3 className="text-lg font-semibold text-gray-900">Global Confidence Thresholds</h3>
          </div>
          
          <div className="grid grid-cols-4 gap-8">
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

        {/* Three Column Layout */}
        <div className="grid grid-cols-3 gap-6">
          {/* Fallback Behavior */}
          <SettingsCard title="Fallback Behavior" icon={AlertTriangle}>
            <Dropdown
              label="When confidence is low"
              value={settings.fallbackBehavior}
              onChange={(value) => updateSetting('fallbackBehavior', value)}
              options={fallbackOptions}
            />
          </SettingsCard>

          {/* AI Model Management */}
          <SettingsCard title="AI Model Management" icon={Brain}>
            <Switch
              label="Pre-load models"
              value={settings.preloadModels}
              onChange={(value) => updateSetting('preloadModels', value)}
            />
            
            <div className="border-t border-gray-100 pt-4 mt-4">
              <p className="text-sm font-medium text-gray-700 mb-3">Select Models</p>
              <div className="space-y-2">
                <Switch
                  label="Text Classification"
                  value={settings.modelToggles.textClassification}
                  onChange={(value) => updateModelToggle('textClassification', value)}
                />
                <Switch
                  label="Image Recognition"
                  value={settings.modelToggles.imageRecognition}
                  onChange={(value) => updateModelToggle('imageRecognition', value)}
                />
                <Switch
                  label="Audio Processing"
                  value={settings.modelToggles.audioProcessing}
                  onChange={(value) => updateModelToggle('audioProcessing', value)}
                />
                <Switch
                  label="Video Analysis"
                  value={settings.modelToggles.videoAnalysis}
                  onChange={(value) => updateModelToggle('videoAnalysis', value)}
                />
              </div>
            </div>
          </SettingsCard>

          {/* Auto-organization */}
          <SettingsCard title="Auto-organization" icon={Zap}>
            <Dropdown
              label="Scan Frequency"
              value={settings.scanFrequency}
              onChange={(value) => updateSetting('scanFrequency', value)}
              options={scanFrequencyOptions}
            />
          </SettingsCard>
        </div>
      </div>
    </div>
  );
};

export default Settings;