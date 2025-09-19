// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Check if we're on the dashboard page
    if (typeof predictions !== 'undefined' && typeof sentimentStats !== 'undefined') {
        renderSubscriberChart();
        renderSentimentChart();
        renderVideoChart();
    }
});

function renderSubscriberChart() {
    const ctx = document.getElementById('subscriberChart').getContext('2d');
    
    if (predictions && predictions.length > 0) {
        const labels = predictions.map(p => p[0]);
        const data = predictions.map(p => p[1]);
        
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Predicted Subscribers',
                    data: data,
                    borderColor: 'rgb(75, 192, 192)',
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                    tension: 0.1,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: '7-Day Subscriber Prediction'
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return `Subscribers: ${context.raw.toLocaleString()}`;
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: false,
                        ticks: {
                            callback: function(value) {
                                return value.toLocaleString();
                            }
                        }
                    }
                }
            }
        });
    } else {
        ctx.font = '16px Arial';
        ctx.fillStyle = '#666';
        ctx.textAlign = 'center';
        ctx.fillText('Not enough data for prediction', ctx.canvas.width / 2, ctx.canvas.height / 2);
    }
}

function renderSentimentChart() {
    const ctx = document.getElementById('sentimentChart').getContext('2d');
    
    const data = [
        sentimentStats.positive || 0,
        sentimentStats.neutral || 0,
        sentimentStats.negative || 0
    ];
    
    const total = data.reduce((a, b) => a + b, 0);
    
    if (total > 0) {
        new Chart(ctx, {
            type: 'pie',
            data: {
                labels: ['Positive', 'Neutral', 'Negative'],
                datasets: [{
                    data: data,
                    backgroundColor: [
                        'rgba(75, 192, 192, 0.7)',
                        'rgba(255, 206, 86, 0.7)',
                        'rgba(255, 99, 132, 0.7)'
                    ],
                    borderColor: [
                        'rgba(75, 192, 192, 1)',
                        'rgba(255, 206, 86, 1)',
                        'rgba(255, 99, 132, 1)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                    },
                    title: {
                        display: true,
                        text: 'Comment Sentiment Distribution'
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const label = context.label || '';
                                const value = context.raw || 0;
                                const percentage = Math.round((value / total) * 100);
                                return `${label}: ${value} (${percentage}%)`;
                            }
                        }
                    }
                }
            }
        });
    } else {
        ctx.font = '16px Arial';
        ctx.fillStyle = '#666';
        ctx.textAlign = 'center';
        ctx.fillText('No sentiment data available', ctx.canvas.width / 2, ctx.canvas.height / 2);
    }
}

function renderVideoChart() {
    const ctx = document.getElementById('videoChart').getContext('2d');
    
    if (videos && videos.length > 0) {
        const labels = videos.map(v => v.title.length > 20 ? v.title.substring(0, 20) + '...' : v.title);
        const views = videos.map(v => v.view_count);
        const likes = videos.map(v => v.like_count);
        const comments = videos.map(v => v.comment_count);
        
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'Views',
                        data: views,
                        backgroundColor: 'rgba(54, 162, 235, 0.7)',
                        borderColor: 'rgba(54, 162, 235, 1)',
                        borderWidth: 1
                    },
                    {
                        label: 'Likes',
                        data: likes,
                        backgroundColor: 'rgba(75, 192, 192, 0.7)',
                        borderColor: 'rgba(75, 192, 192, 1)',
                        borderWidth: 1
                    },
                    {
                        label: 'Comments',
                        data: comments,
                        backgroundColor: 'rgba(255, 159, 64, 0.7)',
                        borderColor: 'rgba(255, 159, 64, 1)',
                        borderWidth: 1
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Video Performance Metrics'
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return `${context.dataset.label}: ${context.raw.toLocaleString()}`;
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return value.toLocaleString();
                            }
                        }
                    }
                }
            }
        });
    } else {
        ctx.font = '16px Arial';
        ctx.fillStyle = '#666';
        ctx.textAlign = 'center';
        ctx.fillText('No video data available', ctx.canvas.width / 2, ctx.canvas.height / 2);
    }
}