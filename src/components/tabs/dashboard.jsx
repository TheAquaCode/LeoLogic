import React from "react";
import { Activity } from "lucide-react";

const Dashboard = ({ isChatMaximized }) => {
  return (
    <div 
      className={`flex-1 overflow-auto p-8 transition-all duration-300 ${
        isChatMaximized ? 'pr-[500px]' : ''
      }`} 
      style={{ backgroundColor: 'var(--theme-bg-primary)' }}
    >
      <div className="max-w-7xl mx-auto w-full space-y-10">
        {/* Dashboard Section */}
        <div>
          <h1 className="text-2xl font-semibold mb-2" style={{ color: 'var(--theme-text-primary)' }}>Dashboard</h1>
          <p className="mb-6" style={{ color: 'var(--theme-text-secondary)' }}>
            AI-powered file organization overview
          </p>

          {/* Organization Progress */}
          <div className="rounded-lg shadow-sm p-6 border" style={{
            backgroundColor: 'var(--theme-bg-secondary)',
            borderColor: 'var(--theme-border-primary)'
          }}>
            <h2 className="text-lg font-medium mb-2" style={{ color: 'var(--theme-text-primary)' }}>
              Organization Progress
            </h2>
            <p className="text-sm mb-4" style={{ color: 'var(--theme-text-secondary)' }}>Overall Organization</p>

            {/* Progress Bar */}
            <div className="relative w-full h-3 rounded-full overflow-hidden mb-3" style={{
              backgroundColor: 'var(--theme-border-primary)'
            }}>
              <div className="absolute top-0 left-0 h-full rounded-full transition-all" style={{
                backgroundColor: 'var(--theme-primary)',
                width: '73%'
              }}></div>
            </div>
            <div className="flex justify-between text-sm mb-6" style={{ color: 'var(--theme-text-secondary)' }}>
              <span>2,081 files organized</span>
              <span>73%</span>
            </div>

            {/* Stats - Responsive grid */}
            <div className={`grid gap-4 ${
              isChatMaximized 
                ? 'grid-cols-2' 
                : 'grid-cols-2 md:grid-cols-4'
            }`}>
              {[
                {
                  title: "Total Files",
                  value: "2,847",
                  change: "+12% from last week",
                },
                {
                  title: "Organized",
                  value: "2,081",
                  change: "+23% from last week",
                },
                {
                  title: "Pending Review",
                  value: "156",
                  change: "-8% from last week",
                },
                {
                  title: "Duplicates Found",
                  value: "47",
                  change: "+5% from last week",
                },
              ].map((stat, i) => (
                <div
                  key={i}
                  className="border rounded-lg p-4 text-center"
                  style={{
                    backgroundColor: 'var(--theme-bg-tertiary)',
                    borderColor: 'var(--theme-border-primary)'
                  }}
                >
                  <p className="text-sm" style={{ color: 'var(--theme-text-secondary)' }}>{stat.title}</p>
                  <p className={`font-bold mt-1 ${
                    isChatMaximized ? 'text-xl' : 'text-2xl'
                  }`} style={{ color: 'var(--theme-text-primary)' }}>
                    {stat.value}
                  </p>
                  <p
                    className={`text-xs mt-1 ${
                      stat.change.startsWith("+")
                        ? "text-green-500"
                        : "text-red-500"
                    }`}
                  >
                    {stat.change}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Active Activity Section */}
        <div>
          <h1 className="text-2xl font-semibold mb-2" style={{ color: 'var(--theme-text-primary)' }}>
            Active Activity
          </h1>
          <p className="mb-6" style={{ color: 'var(--theme-text-secondary)' }}>
            System metrics and task monitoring
          </p>

          {/* Metrics */}
          <div className="rounded-lg shadow-sm p-6 border mb-6" style={{
            backgroundColor: 'var(--theme-bg-secondary)',
            borderColor: 'var(--theme-border-primary)'
          }}>
            <div className="flex flex-wrap justify-between items-center mb-4">
              <div className="flex items-center gap-2">
                <Activity className="w-5 h-5" style={{ color: 'var(--theme-text-secondary)' }} />
                <span className="text-sm font-medium" style={{ color: 'var(--theme-text-primary)' }}>
                  CPU Usage
                </span>
              </div>
              <span className={`font-semibold ${
                isChatMaximized ? 'text-xl' : 'text-2xl'
              }`} style={{ color: 'var(--theme-text-primary)' }}>45%</span>
            </div>
            <div className="w-full h-2 rounded-full mb-6 overflow-hidden" style={{
              backgroundColor: 'var(--theme-border-primary)'
            }}>
              <div className="h-full rounded-full" style={{
                backgroundColor: 'var(--theme-primary)',
                width: '45%'
              }}></div>
            </div>

            <div className={`grid gap-6 text-sm ${
              isChatMaximized 
                ? 'grid-cols-1' 
                : 'grid-cols-2 md:grid-cols-3'
            }`} style={{ color: 'var(--theme-text-secondary)' }}>
              <div>
                <p className="font-medium" style={{ color: 'var(--theme-text-primary)' }}>Processing Speed</p>
                <p>127 files/min</p>
              </div>
              <div>
                <p className="font-medium" style={{ color: 'var(--theme-text-primary)' }}>Queue Status</p>
                <p>23 files pending</p>
              </div>
            </div>
          </div>

          {/* Active Tasks */}
          <div className="rounded-lg shadow-sm p-6 border" style={{
            backgroundColor: 'var(--theme-bg-secondary)',
            borderColor: 'var(--theme-border-primary)'
          }}>
            <h2 className="text-lg font-medium mb-4" style={{ color: 'var(--theme-text-primary)' }}>
              Active Tasks
            </h2>

            {[
              {
                name: "Organize Downloads",
                status: "Running",
                progress: 67,
                details: "157/234 files",
                color: "bg-blue-500",
              },
              {
                name: "Remove Duplicates",
                status: "Complete",
                progress: 100,
                details: "1203/1203 files",
                color: "bg-green-500",
              },
              {
                name: "Clean Old Files",
                status: "Queued",
                progress: 0,
                details: "0/23 files",
                color: "bg-gray-400",
              },
            ].map((task, i) => (
              <div key={i} className="mb-6 last:mb-0">
                <div className="flex justify-between items-center mb-2 gap-4">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className={`font-medium ${
                      isChatMaximized ? 'text-sm' : 'text-base'
                    }`} style={{ color: 'var(--theme-text-primary)' }}>{task.name}</span>
                    <span
                      className={`text-xs px-2 py-1 rounded-full ${
                        task.status === "Running"
                          ? "bg-blue-100 text-blue-700"
                          : task.status === "Complete"
                          ? "bg-green-100 text-green-700"
                          : "bg-gray-100 text-gray-600"
                      }`}
                    >
                      {task.status}
                    </span>
                  </div>
                  <span className="text-sm whitespace-nowrap" style={{ color: 'var(--theme-text-secondary)' }}>{task.details}</span>
                </div>
                <div className="relative w-full h-2 rounded-full overflow-hidden" style={{
                  backgroundColor: 'var(--theme-border-primary)'
                }}>
                  <div
                    className={`${task.color} h-full rounded-full transition-all`}
                    style={{ width: `${task.progress}%` }}
                  ></div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;