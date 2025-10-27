import React from 'react';
import { Palette, Bell, Settings as SettingsIcon, AlertTriangle, Zap, Activity } from 'lucide-react';

const Settings = ({ isChatMaximized }) => {
  const [activeTab, setActiveTab] = React.useState('general');

  return (
    <div 
      className={`flex-1 overflow-auto transition-all duration-300 ${
        isChatMaximized ? 'pr-[500px]' : ''
      }`}
      style={{ backgroundColor: 'var(--theme-bg-primary)' }}
    >
      <div className="p-6">
        {/* Tabs */}
        <div className="flex space-x-1 mb-8 border-b" style={{ borderColor: 'var(--theme-border-primary)' }}>
          <button
            onClick={() => setActiveTab('general')}
            className={`px-6 py-3 font-medium transition-colors ${
              activeTab === 'general' ? 'border-b-2' : ''
            }`}
            style={{
              color: activeTab === 'general' ? 'var(--theme-primary)' : 'var(--theme-text-secondary)',
              borderColor: activeTab === 'general' ? 'var(--theme-primary)' : 'transparent'
            }}
          >
            General Settings
          </button>
          <button
            onClick={() => setActiveTab('advanced')}
            className={`px-6 py-3 font-medium transition-colors ${
              activeTab === 'advanced' ? 'border-b-2' : ''
            }`}
            style={{
              color: activeTab === 'advanced' ? 'var(--theme-primary)' : 'var(--theme-text-secondary)',
              borderColor: activeTab === 'advanced' ? 'var(--theme-primary)' : 'transparent'
            }}
          >
            Advanced Settings
          </button>
        </div>

        {/* General Settings Tab */}
        {activeTab === 'general' && (
          <div className={`grid gap-6 ${isChatMaximized ? 'grid-cols-1' : 'grid-cols-1 lg:grid-cols-2'}`}>
            {/* Appearance */}
            <div className="border rounded-lg p-6" style={{
              backgroundColor: 'var(--theme-bg-secondary)',
              borderColor: 'var(--theme-border-primary)'
            }}>
              <div className="flex items-center gap-2 mb-4">
                <Palette className="w-5 h-5" style={{ color: 'var(--theme-text-secondary)' }} />
                <h3 className="font-semibold" style={{ color: 'var(--theme-text-primary)' }}>Appearance</h3>
              </div>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-2" style={{ color: 'var(--theme-text-primary)' }}>
                    Theme
                  </label>
                  <select className="w-full px-3 py-2 rounded-lg border" style={{
                    backgroundColor: 'var(--theme-bg-tertiary)',
                    borderColor: 'var(--theme-border-primary)',
                    color: 'var(--theme-text-primary)'
                  }}>
                    <option>Light</option>
                    <option>Dark</option>
                    <option>System</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2" style={{ color: 'var(--theme-text-primary)' }}>
                    Accent Color
                  </label>
                  <select className="w-full px-3 py-2 rounded-lg border" style={{
                    backgroundColor: 'var(--theme-bg-tertiary)',
                    borderColor: 'var(--theme-border-primary)',
                    color: 'var(--theme-text-primary)'
                  }}>
                    <option>Blue</option>
                    <option>Purple</option>
                    <option>Green</option>
                    <option>Red</option>
                  </select>
                </div>
              </div>
            </div>

            {/* Application */}
            <div className="border rounded-lg p-6" style={{
              backgroundColor: 'var(--theme-bg-secondary)',
              borderColor: 'var(--theme-border-primary)'
            }}>
              <div className="flex items-center gap-2 mb-4">
                <Bell className="w-5 h-5" style={{ color: 'var(--theme-text-secondary)' }} />
                <h3 className="font-semibold" style={{ color: 'var(--theme-text-primary)' }}>Application</h3>
              </div>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm" style={{ color: 'var(--theme-text-primary)' }}>Run on Startup</span>
                  <button className="w-11 h-6 rounded-full relative transition-colors" style={{ backgroundColor: 'var(--theme-primary)' }}>
                    <div className="absolute right-1 top-1 w-4 h-4 bg-white rounded-full transition-transform"></div>
                  </button>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm" style={{ color: 'var(--theme-text-primary)' }}>Desktop Notifications</span>
                  <button className="w-11 h-6 rounded-full relative transition-colors" style={{ backgroundColor: 'var(--theme-primary)' }}>
                    <div className="absolute right-1 top-1 w-4 h-4 bg-white rounded-full transition-transform"></div>
                  </button>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm" style={{ color: 'var(--theme-text-primary)' }}>Minimize to Tray</span>
                  <button className="w-11 h-6 rounded-full relative transition-colors" style={{ backgroundColor: 'var(--theme-border-primary)' }}>
                    <div className="absolute left-1 top-1 w-4 h-4 bg-white rounded-full transition-transform"></div>
                  </button>
                </div>
              </div>
            </div>

            {/* Confidence Thresholds - Full Width */}
            <div className={`border rounded-lg p-6 ${isChatMaximized ? 'col-span-1' : 'lg:col-span-2'}`} style={{
              backgroundColor: 'var(--theme-bg-secondary)',
              borderColor: 'var(--theme-border-primary)'
            }}>
              <div className="flex items-center gap-2 mb-4">
                <Activity className="w-5 h-5" style={{ color: 'var(--theme-text-secondary)' }} />
                <h3 className="font-semibold" style={{ color: 'var(--theme-text-primary)' }}>Confidence Thresholds</h3>
              </div>
              <div className={`grid gap-6 ${isChatMaximized ? 'grid-cols-1' : 'grid-cols-1 md:grid-cols-3'}`}>
                {['Text', 'Images', 'Audio'].map((type, index) => (
                  <div key={type}>
                    <div className="flex justify-between items-center mb-2">
                      <label className="text-sm font-medium" style={{ color: 'var(--theme-text-primary)' }}>
                        {type}
                      </label>
                      <span className="text-sm" style={{ color: 'var(--theme-text-secondary)' }}>
                        {index === 0 ? '85%' : index === 1 ? '80%' : '75%'}
                      </span>
                    </div>
                    <input
                      type="range"
                      min="0"
                      max="100"
                      defaultValue={index === 0 ? '85' : index === 1 ? '80' : '75'}
                      className="w-full h-2 rounded-lg appearance-none cursor-pointer"
                      style={{
                        background: `linear-gradient(to right, var(--theme-primary) 0%, var(--theme-primary) ${index === 0 ? '85' : index === 1 ? '80' : '75'}%, var(--theme-border-primary) ${index === 0 ? '85' : index === 1 ? '80' : '75'}%, var(--theme-border-primary) 100%)`
                      }}
                    />
                  </div>
                ))}
              </div>
            </div>

            {/* Fallback Behavior */}
            <div className="border rounded-lg p-6" style={{
              backgroundColor: 'var(--theme-bg-secondary)',
              borderColor: 'var(--theme-border-primary)'
            }}>
              <div className="flex items-center gap-2 mb-4">
                <AlertTriangle className="w-5 h-5" style={{ color: 'var(--theme-text-secondary)' }} />
                <h3 className="font-semibold" style={{ color: 'var(--theme-text-primary)' }}>Fallback Behavior</h3>
              </div>
              <div>
                <label className="block text-sm font-medium mb-2" style={{ color: 'var(--theme-text-primary)' }}>
                  When confidence is low
                </label>
                <select className="w-full px-3 py-2 rounded-lg border" style={{
                  backgroundColor: 'var(--theme-bg-tertiary)',
                  borderColor: 'var(--theme-border-primary)',
                  color: 'var(--theme-text-primary)'
                }}>
                  <option>Move to review folder</option>
                  <option>Ask for confirmation</option>
                  <option>Skip file</option>
                  <option>Use best guess</option>
                </select>
              </div>
            </div>

            {/* AI Models */}
            <div className="border rounded-lg p-6" style={{
              backgroundColor: 'var(--theme-bg-secondary)',
              borderColor: 'var(--theme-border-primary)'
            }}>
              <div className="flex items-center gap-2 mb-4">
                <Zap className="w-5 h-5" style={{ color: 'var(--theme-text-secondary)' }} />
                <h3 className="font-semibold" style={{ color: 'var(--theme-text-primary)' }}>AI Models</h3>
              </div>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm" style={{ color: 'var(--theme-text-primary)' }}>Pre-load models</span>
                  <button className="w-11 h-6 rounded-full relative transition-colors" style={{ backgroundColor: 'var(--theme-primary)' }}>
                    <div className="absolute right-1 top-1 w-4 h-4 bg-white rounded-full transition-transform"></div>
                  </button>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm" style={{ color: 'var(--theme-text-primary)' }}>Text</span>
                  <button className="w-11 h-6 rounded-full relative transition-colors" style={{ backgroundColor: 'var(--theme-primary)' }}>
                    <div className="absolute right-1 top-1 w-4 h-4 bg-white rounded-full transition-transform"></div>
                  </button>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm" style={{ color: 'var(--theme-text-primary)' }}>Images</span>
                  <button className="w-11 h-6 rounded-full relative transition-colors" style={{ backgroundColor: 'var(--theme-primary)' }}>
                    <div className="absolute right-1 top-1 w-4 h-4 bg-white rounded-full transition-transform"></div>
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Advanced Settings Tab */}
        {activeTab === 'advanced' && (
          <div className="border rounded-lg p-6" style={{
            backgroundColor: 'var(--theme-bg-secondary)',
            borderColor: 'var(--theme-border-primary)'
          }}>
            <h3 className="font-semibold mb-4" style={{ color: 'var(--theme-text-primary)' }}>
              Advanced Settings
            </h3>
            <p style={{ color: 'var(--theme-text-secondary)' }}>
              Advanced configuration options coming soon...
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default Settings;