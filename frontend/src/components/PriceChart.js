import React, { useState, useEffect } from 'react';
import { Line } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, Filler } from 'chart.js';

// Register ChartJS components
ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, Filler);

const PriceChart = ({ symbol }) => {
  const [timeframe, setTimeframe] = useState('1M'); // Default to 1 month
  const [chartData, setChartData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // In a real application, you would fetch real price data from an API
    // For this demo, we'll generate simulated price data
    setLoading(true);
    
    // Simulate API call delay
    const fetchData = setTimeout(() => {
      const data = generateChartData(symbol, timeframe);
      setChartData(data);
      setLoading(false);
    }, 500);

    return () => clearTimeout(fetchData);
  }, [symbol, timeframe]);

  const generateChartData = (symbol, timeframe) => {
    let days;
    switch (timeframe) {
      case '1D': days = 1; break;
      case '1W': days = 7; break;
      case '1M': days = 30; break;
      case '3M': days = 90; break;
      case '1Y': days = 365; break;
      case 'ALL': days = 1825; break; // ~5 years
      default: days = 30;
    }
    
    // Generate dates for the x-axis
    const labels = [];
    const now = new Date();
    for (let i = days; i >= 0; i--) {
      const date = new Date(now);
      date.setDate(date.getDate() - i);
      labels.push(date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }));
    }
    
    // Generate price data
    let priceData;
    
    // Use different patterns depending on the symbol
    if (symbol === 'BTC') {
      const basePrice = 61245.32;
      priceData = simulatePriceHistory(basePrice, days, 0.015, 0.5);
    } else if (symbol === 'ETH') {
      const basePrice = 3500.75;
      priceData = simulatePriceHistory(basePrice, days, 0.018, 0.6);
    } else {
      const basePrice = 100.00;
      priceData = simulatePriceHistory(basePrice, days, 0.02, 0.7);
    }
    
    // Get colors based on price movement
    const startPrice = priceData[0];
    const endPrice = priceData[priceData.length - 1];
    const priceColor = endPrice >= startPrice ? 'rgba(52, 211, 153, 1)' : 'rgba(239, 68, 68, 1)';
    const gradientColor = endPrice >= startPrice ? 'rgba(52, 211, 153, 0.1)' : 'rgba(239, 68, 68, 0.1)';
    
    return {
      labels,
      datasets: [
        {
          label: `${symbol} Price (USD)`,
          data: priceData,
          borderColor: priceColor,
          backgroundColor: gradientColor,
          fill: true,
          tension: 0.4,
          pointRadius: 0,
          pointHoverRadius: 5,
          pointHoverBackgroundColor: priceColor,
          pointHoverBorderColor: '#fff',
          pointHoverBorderWidth: 2
        }
      ]
    };
  };

  const simulatePriceHistory = (currentPrice, days, volatility, trend) => {
    const priceHistory = [];
    
    // Generate random walk with trend
    let price = currentPrice;
    
    // Work backwards from current price
    for (let i = 0; i <= days; i++) {
      if (i === days) {
        // Last element is the current price
        priceHistory.push(currentPrice);
      } else {
        // Generate historical prices working backwards
        const randomFactor = Math.random() * 2 - 1; // Between -1 and 1
        const dayVolatility = (volatility * randomFactor) / Math.sqrt(252); // Daily volatility
        const trendFactor = Math.random() > 0.5 ? trend : -trend;
        const dayReturn = (dayVolatility + trendFactor / 252);
        
        // Calculate previous day's price
        price = price / (1 + dayReturn);
        priceHistory.unshift(price);
      }
    }
    
    return priceHistory;
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false
      },
      tooltip: {
        mode: 'index',
        intersect: false,
        backgroundColor: 'rgba(17, 24, 39, 0.9)',
        titleColor: '#fff',
        bodyColor: '#fff',
        borderColor: 'rgba(75, 85, 99, 0.3)',
        borderWidth: 1,
        padding: 10,
        cornerRadius: 4,
        bodyFont: {
          family: 'Inter, sans-serif',
          size: 12
        },
        titleFont: {
          family: 'Inter, sans-serif',
          size: 14,
          weight: 'bold'
        },
        callbacks: {
          label: function(context) {
            return `${context.dataset.label}: $${context.parsed.y.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
          }
        }
      }
    },
    scales: {
      x: {
        grid: {
          display: false,
          drawBorder: false
        },
        ticks: {
          color: 'rgba(156, 163, 175, 0.8)',
          font: {
            family: 'Inter, sans-serif',
            size: 10
          },
          maxRotation: 0,
          callback: function(value, index, values) {
            // Only show some of the labels for readability
            const interval = Math.ceil(values.length / 6); // Show ~6 labels
            return index % interval === 0 ? this.getLabelForValue(value) : '';
          }
        }
      },
      y: {
        position: 'right',
        grid: {
          color: 'rgba(75, 85, 99, 0.1)',
          drawBorder: false
        },
        ticks: {
          color: 'rgba(156, 163, 175, 0.8)',
          font: {
            family: 'Inter, sans-serif',
            size: 10
          },
          callback: function(value) {
            // Format y-axis labels as compact USD
            return '$' + value.toLocaleString('en-US', { 
              notation: "compact",
              minimumFractionDigits: 0,
              maximumFractionDigits: 0 
            });
          }
        }
      }
    },
    interaction: {
      mode: 'nearest',
      axis: 'x',
      intersect: false
    },
    elements: {
      line: {
        borderWidth: 2
      }
    }
  };

  return (
    <div>
      {/* Timeframe selector */}
      <div className="flex justify-between items-center mb-4">
        <div className="text-lg font-medium">Price Chart</div>
        <div className="flex space-x-1">
          {['1D', '1W', '1M', '3M', '1Y', 'ALL'].map((tf) => (
            <button
              key={tf}
              className={`px-3 py-1 text-xs font-medium rounded ${
                timeframe === tf 
                  ? 'bg-indigo-700 text-white' 
                  : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
              }`}
              onClick={() => setTimeframe(tf)}
            >
              {tf}
            </button>
          ))}
        </div>
      </div>
      
      {/* Chart */}
      <div className="h-64">
        {loading ? (
          <div className="h-full flex items-center justify-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-500"></div>
          </div>
        ) : chartData ? (
          <Line data={chartData} options={chartOptions} height="100%" />
        ) : (
          <div className="h-full flex items-center justify-center">
            <div className="text-gray-400">No price data available</div>
          </div>
        )}
      </div>
    </div>
  );
};

export default PriceChart;