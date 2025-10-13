import React from "react";
import { File, Calendar, HardDrive, Copy, Activity } from "lucide-react";

const Dashboard = () => {
  return (
    <div className="flex-1 overflow-auto p-8 space-y-10 bg-gray-50">
      {/* Dashboard Section */}
      <div>
        <h1 className="text-2xl font-semibold text-gray-800 mb-2">Dashboard</h1>
        <p className="text-gray-500 mb-6">
          AI-powered file organization overview
        </p>

        {/* Quick Sort */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-8 border border-gray-200">
          <h2 className="text-lg font-medium text-gray-800 mb-4">Quick Sort</h2>
          <p className="text-sm text-gray-500 mb-4">
            Organize files quickly with AI-powered actions
          </p>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {[
              { icon: File, label: "By Type", desc: "Sort by file type" },
              { icon: Calendar, label: "By Date", desc: "Sort by date modified" },
              { icon: HardDrive, label: "By Size", desc: "Sort by file size" },
              { icon: Copy, label: "Duplicates", desc: "Find duplicate files" },
            ].map((item, idx) => (
              <button
                key={idx}
                className="flex flex-col items-center justify-center border border-gray-200 rounded-xl p-6 hover:shadow-md transition"
              >
                <item.icon className="w-8 h-8 text-gray-700 mb-2" />
                <span className="font-medium text-gray-800">{item.label}</span>
                <span className="text-xs text-gray-500 mt-1">{item.desc}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Organization Progress */}
        <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
          <h2 className="text-lg font-medium text-gray-800 mb-2">
            Organization Progress
          </h2>
          <p className="text-sm text-gray-500 mb-4">
            Overall Organization
          </p>
          <div className="relative w-full h-3 bg-gray-200 rounded-full overflow-hidden mb-3">
            <div className="absolute top-0 left-0 h-full bg-black rounded-full w-[73%] transition-all"></div>
          </div>
          <div className="flex justify-between text-sm text-gray-600 mb-6">
            <span>2,081 files organized</span>
            <span>73%</span>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
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
                className="bg-gray-50 border border-gray-200 rounded-lg p-4 text-center"
              >
                <p className="text-gray-600 text-sm">{stat.title}</p>
                <p className="text-2xl font-bold text-gray-800 mt-1">
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
        <h1 className="text-2xl font-semibold text-gray-800 mb-2">
          Active Activity
        </h1>
        <p className="text-gray-500 mb-6">
          System metrics and task monitoring
        </p>

        {/* Metrics */}
        <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200 mb-6">
          <div className="flex flex-wrap justify-between items-center mb-4">
            <div className="flex items-center gap-2">
              <Activity className="w-5 h-5 text-gray-700" />
              <span className="text-sm font-medium text-gray-800">
                CPU Usage
              </span>
            </div>
            <span className="text-2xl font-semibold text-gray-800">45%</span>
          </div>
          <div className="w-full h-2 bg-gray-200 rounded-full mb-6 overflow-hidden">
            <div className="h-full bg-black w-[45%] rounded-full"></div>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-3 gap-6 text-sm text-gray-700">
            <div>
              <p className="font-medium">Processing Speed</p>
              <p className="text-gray-500">127 files/min</p>
            </div>
            <div>
              <p className="font-medium">Queue Status</p>
              <p className="text-gray-500">23 files pending</p>
            </div>
          </div>
        </div>

        {/* Active Tasks */}
        <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
          <h2 className="text-lg font-medium text-gray-800 mb-4">
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
            <div key={i} className="mb-6">
              <div className="flex justify-between items-center mb-2">
                <div className="flex items-center gap-2">
                  <span className="font-medium text-gray-800">{task.name}</span>
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
                <span className="text-sm text-gray-500">{task.details}</span>
              </div>
              <div className="relative w-full h-2 bg-gray-200 rounded-full overflow-hidden">
                <div
                  className={`${task.color} h-full rounded-full`}
                  style={{ width: `${task.progress}%` }}
                ></div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
