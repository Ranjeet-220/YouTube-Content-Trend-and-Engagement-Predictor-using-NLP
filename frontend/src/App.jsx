import React, { useState } from 'react';
import axios from 'axios';
import { Doughnut } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
  CategoryScale,
  LinearScale,
  BarElement
} from 'chart.js';
import { AlertCircle, TrendingUp, Search, MessageSquare, Loader2, Sparkles, Youtube, Eye, ThumbsUp, MessageCircle } from 'lucide-react';

ChartJS.register(ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement);

const API_BASE = 'http://127.0.0.1:5000';

function App() {
  const [formData, setFormData] = useState({ title: '', description: '', tags: '' });
  const [youtubeUrl, setYoutubeUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [fetchingVideo, setFetchingVideo] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  const [videoInfo, setVideoInfo] = useState(null);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleClear = () => {
    setFormData({ title: '', description: '', tags: '' });
    setYoutubeUrl('');
    setResults(null);
    setError(null);
    setVideoInfo(null);
  };

  const handleFetchVideo = async () => {
    if (!youtubeUrl) {
      setError("Please enter a YouTube URL.");
      return;
    }
    setFetchingVideo(true);
    setError(null);
    setVideoInfo(null);
    try {
      const response = await axios.post(`${API_BASE}/fetch-video`, { url: youtubeUrl });
      const data = response.data;
      setVideoInfo(data);
      setFormData({
        title: data.title || '',
        description: data.description || '',
        tags: data.tags || ''
      });
    } catch (err) {
      setError(err.response?.data?.error || "Failed to fetch video. Check the URL or backend.");
    } finally {
      setFetchingVideo(false);
    }
  };

  const handleAnalyze = async (e) => {
    e.preventDefault();
    if (!formData.title) {
      setError("Title is required for analysis.");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const response = await axios.post(`${API_BASE}/predict`, formData);
      setResults(response.data);
    } catch (err) {
      setError(err.response?.data?.error || "Failed to connect to the backend server. Make sure it is running.");
    } finally {
      setLoading(false);
    }
  };

  const gaugeData = {
    labels: ['Score', 'Remaining'],
    datasets: [{
      data: results ? [results.engagement_score, 100 - results.engagement_score] : [0, 100],
      backgroundColor: ['#3b82f6', '#1e293b'],
      borderWidth: 0,
      cutout: '80%',
    }],
  };

  const gaugeOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: { legend: { display: false }, tooltip: { enabled: false } },
    animation: { animateScale: true, animateRotate: true }
  };

  return (
    <div className="min-h-screen bg-background p-4 md:p-8 font-sans">
      <div className="max-w-7xl mx-auto space-y-8">

        {/* Header */}
        <header className="text-center space-y-4 pt-8 pb-4">
          <div className="inline-flex items-center justify-center p-3 bg-primary/10 rounded-full mb-2">
            <Sparkles className="w-8 h-8 text-primary" />
          </div>
          <h1 className="text-4xl md:text-5xl font-extrabold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-violet-500">
            YouTube Content Predictor
          </h1>
          <p className="text-slate-400 max-w-2xl mx-auto text-lg">
            Leverage AI and NLP to predict engagement, analyze sentiment, and optimize your video metadata for maximum reach.
          </p>
        </header>

        {/* YouTube URL Fetch Bar */}
        <div className="glass-panel rounded-2xl p-5">
          <h2 className="text-sm font-semibold text-slate-400 mb-3 flex items-center">
            <Youtube className="w-4 h-4 mr-2 text-red-500" />
            Auto-fill from YouTube URL (Optional)
          </h2>
          <div className="flex gap-3">
            <input
              type="text"
              value={youtubeUrl}
              onChange={(e) => setYoutubeUrl(e.target.value)}
              placeholder="Paste YouTube video URL e.g. https://youtube.com/watch?v=..."
              className="flex-1 bg-slate-900/50 border border-slate-700 rounded-xl p-3 text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-red-500/50 transition-all"
            />
            <button
              onClick={handleFetchVideo}
              disabled={fetchingVideo}
              className="bg-red-600 hover:bg-red-500 text-white font-medium py-3 px-5 rounded-xl transition-all duration-200 flex items-center gap-2 whitespace-nowrap"
            >
              {fetchingVideo ? <Loader2 className="w-4 h-4 animate-spin" /> : <Youtube className="w-4 h-4" />}
              {fetchingVideo ? 'Fetching...' : 'Fetch Video'}
            </button>
          </div>

          {/* Video Info Card */}
          {videoInfo && (
            <div className="mt-4 flex items-center gap-4 p-4 bg-slate-800/60 rounded-xl border border-slate-700">
              {videoInfo.thumbnail && (
                <img src={videoInfo.thumbnail} alt="thumbnail" className="w-24 h-16 rounded-lg object-cover flex-shrink-0" />
              )}
              <div className="flex-1 min-w-0">
                <p className="text-white font-medium text-sm truncate">{videoInfo.title}</p>
                <p className="text-slate-400 text-xs mt-1">{videoInfo.channel}</p>
                <div className="flex items-center gap-4 mt-2">
                  <span className="flex items-center gap-1 text-slate-400 text-xs">
                    <Eye className="w-3 h-3" /> {Number(videoInfo.views).toLocaleString()}
                  </span>
                  <span className="flex items-center gap-1 text-slate-400 text-xs">
                    <ThumbsUp className="w-3 h-3" /> {Number(videoInfo.likes).toLocaleString()}
                  </span>
                  <span className="flex items-center gap-1 text-slate-400 text-xs">
                    <MessageCircle className="w-3 h-3" /> {Number(videoInfo.comments).toLocaleString()}
                  </span>
                </div>
              </div>
              <span className="text-green-400 text-xs font-medium bg-green-400/10 px-2 py-1 rounded-full flex-shrink-0">✓ Auto-filled</span>
            </div>
          )}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">

          {/* Input Section */}
          <div className="lg:col-span-5 space-y-6">
            <div className="glass-panel rounded-2xl p-6">
              <h2 className="text-2xl font-semibold mb-6 flex items-center text-slate-100">
                <Search className="w-5 h-5 mr-2 text-primary" />
                Analyze Content
              </h2>

              <form onSubmit={handleAnalyze} className="space-y-5">
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">Video Title *</label>
                  <input
                    type="text"
                    name="title"
                    value={formData.title}
                    onChange={handleInputChange}
                    placeholder="e.g. How to go VIRAL on YouTube FAST!!!"
                    className="w-full bg-slate-900/50 border border-slate-700 rounded-xl p-3 text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">Description</label>
                  <textarea
                    name="description"
                    value={formData.description}
                    onChange={handleInputChange}
                    rows="4"
                    placeholder="Enter your video description here..."
                    className="w-full bg-slate-900/50 border border-slate-700 rounded-xl p-3 text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all resize-none"
                  ></textarea>
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">Tags (comma separated)</label>
                  <input
                    type="text"
                    name="tags"
                    value={formData.tags}
                    onChange={handleInputChange}
                    placeholder="e.g. youtube, viral, tutorial"
                    className="w-full bg-slate-900/50 border border-slate-700 rounded-xl p-3 text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all"
                  />
                </div>

                {error && (
                  <div className="p-4 bg-red-500/10 border border-red-500/50 rounded-xl flex items-start text-red-400 text-sm">
                    <AlertCircle className="w-5 h-5 mr-2 flex-shrink-0 mt-0.5" />
                    <span>{error}</span>
                  </div>
                )}

                <div className="flex space-x-4 pt-2">
                  <button
                    type="submit"
                    disabled={loading}
                    className="flex-1 bg-gradient-to-r from-blue-600 to-violet-600 hover:from-blue-500 hover:to-violet-500 text-white font-medium py-3 px-4 rounded-xl shadow-lg shadow-blue-500/20 transition-all duration-200 flex justify-center items-center"
                  >
                    {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : 'Predict Engagement'}
                  </button>
                  <button
                    type="button"
                    onClick={handleClear}
                    className="px-6 bg-slate-800 hover:bg-slate-700 text-slate-300 font-medium py-3 rounded-xl border border-slate-700 transition-all duration-200"
                  >
                    Clear
                  </button>
                </div>
              </form>
            </div>
          </div>

          {/* Results Section */}
          <div className="lg:col-span-7">
            {results ? (
              <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">

                  {/* Engagement Score */}
                  <div className="glass-panel rounded-2xl p-6 flex flex-col items-center justify-center relative overflow-hidden">
                    <div className="absolute inset-0 bg-blue-500/5 blur-3xl rounded-full"></div>
                    <h3 className="text-slate-400 text-sm font-medium mb-4 relative z-10">Engagement Score</h3>
                    <div className="w-32 h-32 relative z-10">
                      <Doughnut data={gaugeData} options={gaugeOptions} />
                      <div className="absolute inset-0 flex items-center justify-center flex-col mt-2">
                        <span className="text-3xl font-bold text-white">{results.engagement_score}</span>
                        <span className="text-xs text-slate-500">/ 100</span>
                      </div>
                    </div>
                  </div>

                  {/* Viral Probability */}
                  <div className="glass-panel rounded-2xl p-6 flex flex-col items-center justify-center text-center">
                    <div className={`p-4 rounded-full mb-4 ${
                      results.viral_probability.includes('High') ? 'bg-green-500/20 text-green-400' :
                      results.viral_probability === 'Moderate' ? 'bg-yellow-500/20 text-yellow-400' : 'bg-red-500/20 text-red-400'
                    }`}>
                      <TrendingUp className="w-8 h-8" />
                    </div>
                    <h3 className="text-slate-400 text-sm font-medium mb-1">Viral Probability</h3>
                    <p className={`text-2xl font-bold ${
                      results.viral_probability.includes('High') ? 'text-green-400' :
                      results.viral_probability === 'Moderate' ? 'text-yellow-400' : 'text-red-400'
                    }`}>{results.viral_probability}</p>
                  </div>

                  {/* SEO & Sentiment */}
                  <div className="glass-panel rounded-2xl p-6 flex flex-col justify-between">
                    <div>
                      <h3 className="text-slate-400 text-sm font-medium mb-2">SEO Score</h3>
                      <div className="flex items-end justify-between mb-2">
                        <span className="text-2xl font-bold text-white">{results.seo_score}</span>
                        <span className="text-xs text-slate-500 mb-1">/ 100</span>
                      </div>
                      <div className="w-full bg-slate-800 rounded-full h-2 mb-6">
                        <div className="bg-gradient-to-r from-blue-500 to-violet-500 h-2 rounded-full" style={{ width: `${results.seo_score}%` }}></div>
                      </div>
                    </div>
                    <div>
                      <h3 className="text-slate-400 text-sm font-medium mb-2">Sentiment</h3>
                      <div className="inline-flex items-center px-3 py-1 rounded-full bg-slate-800/80 border border-slate-700 text-sm font-medium">
                        {results.sentiment === 'Positive' ? '😊 Positive' : results.sentiment === 'Negative' ? '😟 Negative' : '😐 Neutral'}
                      </div>
                    </div>
                  </div>
                </div>

                {/* Suggestions */}
                <div className="glass-panel rounded-2xl p-6">
                  <h3 className="text-lg font-semibold text-slate-100 mb-4 flex items-center">
                    <MessageSquare className="w-5 h-5 mr-2 text-violet-400" />
                    Improvement Suggestions
                  </h3>
                  <ul className="space-y-3">
                    {results.improvement_suggestions.map((suggestion, index) => (
                      <li key={index} className="flex items-start p-3 bg-slate-800/50 rounded-xl border border-slate-700/50">
                        <div className="w-1.5 h-1.5 rounded-full bg-violet-500 mt-2 mr-3 flex-shrink-0"></div>
                        <p className="text-slate-300 text-sm leading-relaxed">{suggestion}</p>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            ) : (
              <div className="h-full min-h-[400px] glass-panel rounded-2xl flex flex-col items-center justify-center p-8 text-center border-dashed border-2 border-slate-700/50">
                <div className="w-20 h-20 bg-slate-800 rounded-full flex items-center justify-center mb-6">
                  <Sparkles className="w-8 h-8 text-slate-500" />
                </div>
                <h3 className="text-xl font-medium text-slate-300 mb-2">Awaiting Input</h3>
                <p className="text-slate-500 max-w-sm">
                  Paste a YouTube URL above to auto-fill metadata, or manually enter your video details on the left and click 'Predict Engagement'.
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
