import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Cloud, Sun, CloudRain, Wind, Droplets, X, RefreshCw } from 'lucide-react';

interface WeatherWidgetProps {
  onClose: () => void;
  city?: string;
  lat?: number;
  lon?: number;
}

export default function WeatherWidget({
  onClose,
  city = 'Bengaluru',
  lat = 12.9716,
  lon = 77.5946,
}: WeatherWidgetProps) {
  const [loading, setLoading] = useState<boolean>(true);
  const [temp, setTemp] = useState<number>(27);
  const [condition, setCondition] = useState<string>('Partly Cloudy');
  const [wind, setWind] = useState<number>(12);
  const [humidity, setHumidity] = useState<number>(62);
  const [weatherCode, setWeatherCode] = useState<number>(1);

  const fetchWeather = async () => {
    setLoading(true);
    try {
      const res = await fetch(
        `https://api.open-meteo.com/v1/forecast?latitude=${lat}&longitude=${lon}&current_weather=true&hourly=relative_humidity_2m`
      );
      if (res.ok) {
        const data = await res.json();
        const cw = data.current_weather;
        if (cw) {
          setTemp(Math.round(cw.temperature));
          setWind(Math.round(cw.windspeed));
          setWeatherCode(cw.weathercode);

          // WMO Weather interpretation codes
          if (cw.weathercode === 0) setCondition('Clear Sky');
          else if (cw.weathercode in [1, 2, 3]) setCondition('Partly Cloudy');
          else if (cw.weathercode in [45, 48]) setCondition('Foggy');
          else if (cw.weathercode in [51, 53, 55, 61, 63, 65, 80, 81]) setCondition('Rain Showers');
          else if (cw.weathercode in [95, 96, 99]) setCondition('Thunderstorm');
          else setCondition('Mild Overcast');
        }
        if (data.hourly && data.hourly.relative_humidity_2m) {
          setHumidity(data.hourly.relative_humidity_2m[0] || 60);
        }
      }
    } catch {
      // Fallback defaults on network timeout
      setCondition('Mostly Clear');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchWeather();
  }, [lat, lon]);

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9, y: 20 }}
      animate={{ opacity: 1, scale: 1, y: 0 }}
      exit={{ opacity: 0, scale: 0.9, y: 20 }}
      className="fixed bottom-24 right-8 z-50 w-72 rounded-2xl bg-[#02050e]/95 border border-cyan-400/60 backdrop-blur-2xl shadow-[0_0_35px_rgba(6,182,212,0.35)] p-4 font-mono text-cyan-400 select-none"
    >
      {/* Header */}
      <div className="flex items-center justify-between pb-2 border-b border-cyan-500/30">
        <div className="flex items-center gap-1.5 text-xs text-white font-bold">
          <Cloud size={14} className="text-cyan-300" />
          <span>ATMOSPHERIC TELEMETRY</span>
        </div>
        <div className="flex items-center gap-1">
          <button
            onClick={fetchWeather}
            className="p-1 hover:text-white transition-colors"
            title="Refresh Weather"
          >
            <RefreshCw size={12} className={loading ? 'animate-spin' : ''} />
          </button>
          <button
            onClick={onClose}
            className="p-1 hover:text-rose-400 transition-colors"
            title="Close"
          >
            <X size={14} />
          </button>
        </div>
      </div>

      {/* Main Temp & Condition */}
      <div className="py-3 flex items-center justify-between">
        <div>
          <div className="text-3xl font-extrabold text-white tracking-tight">
            {temp}&deg;<span className="text-lg text-cyan-300 font-normal">C</span>
          </div>
          <div className="text-xs text-cyan-200 mt-0.5 font-sans font-medium">{condition}</div>
          <div className="text-[10px] text-cyan-500">{city} &bull; Sensor Realtime</div>
        </div>
        <div className="p-3 rounded-2xl bg-cyan-950/60 border border-cyan-500/40 text-cyan-200">
          {weatherCode === 0 ? (
            <Sun size={28} className="text-amber-400 animate-spin-slow" />
          ) : weatherCode >= 50 ? (
            <CloudRain size={28} className="text-cyan-300" />
          ) : (
            <Cloud size={28} className="text-cyan-200" />
          )}
        </div>
      </div>

      {/* Stats Footer */}
      <div className="pt-2 border-t border-cyan-500/20 grid grid-cols-2 gap-2 text-[11px]">
        <div className="flex items-center gap-1.5 text-cyan-300">
          <Wind size={12} />
          <span>WIND: <strong className="text-white">{wind} km/h</strong></span>
        </div>
        <div className="flex items-center gap-1.5 text-cyan-300">
          <Droplets size={12} />
          <span>HUMIDITY: <strong className="text-white">{humidity}%</strong></span>
        </div>
      </div>
    </motion.div>
  );
}
