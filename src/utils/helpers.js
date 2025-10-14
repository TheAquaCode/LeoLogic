export const getStatusColor = (status) => {
  switch (status) {
    case 'Active': return 'text-green-600 bg-green-50';
    case 'Paused': return 'text-yellow-600 bg-yellow-50';
    default: return 'text-gray-600 bg-gray-50';
  }
};